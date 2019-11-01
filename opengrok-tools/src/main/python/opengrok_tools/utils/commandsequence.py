#
# CDDL HEADER START
#
# The contents of this file are subject to the terms of the
# Common Development and Distribution License (the "License").
# You may not use this file except in compliance with the License.
#
# See LICENSE.txt included in this distribution for the specific
# language governing permissions and limitations under the License.
#
# When distributing Covered Code, include this CDDL HEADER in each
# file and include the License file at LICENSE.txt.
# If applicable, add the following below this CDDL HEADER, with the
# fields enclosed by brackets "[]" replaced with your own identifying
# information: Portions Copyright [yyyy] [name of copyright owner]
#
# CDDL HEADER END
#

#
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#

import logging
from .command import Command
from .webutil import put, post, delete
from .utils import is_web_uri
from .exitvals import (
    CONTINUE_EXITVAL,
    SUCCESS_EXITVAL
)
import json
import re


class CommandSequenceBase:
    """
    Wrap the run of a set of Command instances.

    This class intentionally does not contain any logging
    so that it can be passed through Pool.map().
    """

    def __init__(self, name, commands, loglevel=logging.INFO, cleanup=None,
                 driveon=False):
        self.name = name
        self.commands = commands
        self.failed = False
        self.retcodes = {}
        self.outputs = {}
        if cleanup and not isinstance(cleanup, list):
            raise Exception("cleanup is not a list of commands")

        self.cleanup = cleanup
        self.loglevel = loglevel
        self.driveon = driveon

    def __str__(self):
        return str(self.name)

    def get_cmd_output(self, cmd, indent=""):
        str = ""
        if self.outputs[cmd]:
            for line in self.outputs[cmd]:
                str += '{}{}'.format(indent, line)

        return str

    def fill(self, retcodes, outputs, failed):
        self.retcodes = retcodes
        self.outputs = outputs
        self.failed = failed


class CommandSequence(CommandSequenceBase):
    PROJECT_SUBST = '%PROJECT%'

    re_program = re.compile('ERROR[:]*\\s+')

    def __init__(self, base):
        super().__init__(base.name, base.commands, loglevel=base.loglevel,
                         cleanup=base.cleanup, driveon=base.driveon)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(base.loglevel)

    def run_command(self, command):
        """
        Execute a command and return its return code.
        """
        command_args = command.get("command")
        cmd = Command(command_args,
                      env_vars=command.get("env"),
                      resource_limits=command.get("limits"),
                      args_subst={self.PROJECT_SUBST: self.name},
                      args_append=[self.name], excl_subst=True)
        cmd.execute()
        self.retcodes[str(cmd)] = cmd.getretcode()
        self.outputs[str(cmd)] = cmd.getoutput()

        return cmd.getretcode()

    def call_rest_api(self, command):
        """
        Make RESTful API call. Occurrence of PROJECT_SUBST in the URI will be
        replaced by project name.
        """
        command = command.get("command")
        uri = command[0].replace(self.PROJECT_SUBST, self.name)
        verb = command[1]
        data = command[2]

        headers = None
        json_data = None
        if data:
            headers = {'Content-Type': 'application/json'}
            json_data = json.dumps(data).replace(self.PROJECT_SUBST, self.name)
            self.logger.debug("JSON data: {}".format(json_data))

        if verb == 'PUT':
            put(self.logger, uri, headers=headers, data=json_data)
        elif verb == 'POST':
            post(self.logger, uri, headers=headers, data=json_data)
        elif verb == 'DELETE':
            delete(self.logger, uri, data)
        else:
            self.logger.error('Unknown HTTP verb in command {}'.
                              format(command))

    def run(self):
        """
        Run the sequence of commands and capture their output and return code.
        First command that returns code other than 0 terminates the sequence.
        If the command has return code 2, the sequence will be terminated
        however it will not be treated as error (unless the 'driveon' parameter
        is True).

        If a command contains PROJECT_SUBST pattern, it will be replaced
        by project name, otherwise project name will be appended to the
        argument list of the command.

        Any command entry that is a URI, will be used to submit RESTful API
        request. Return codes for these requests are not checked.
        """

        for command in self.commands:
            if is_web_uri(command.get("command")[0]):
                self.call_rest_api(command)
            else:
                retcode = self.run_command(command)

                # If a command exits with non-zero return code,
                # terminate the sequence of commands.
                if retcode != SUCCESS_EXITVAL:
                    if retcode == CONTINUE_EXITVAL:
                        if not self.driveon:
                            self.logger.debug("command '{}' for project {} "
                                              "requested break".
                                              format(self.name, command))
                            self.run_cleanup()
                        else:
                            self.logger.debug("command '{}' for project {} "
                                              "requested break however "
                                              "the 'driveon' option is set "
                                              "so driving on.".
                                              format(self.name, command))
                            continue
                    else:
                        self.logger.error("command '{}' for project {} failed "
                                          "with code {}, breaking".
                                          format(command, self.name, retcode))
                        self.failed = True
                        self.run_cleanup()

                    break

    def run_cleanup(self):
        """
        Call cleanup sequence in case the command sequence failed
        or termination was requested.
        """
        if self.cleanup is None:
            return

        for cleanup_cmd in self.cleanup:
            if is_web_uri(cleanup_cmd.get("command")[0]):
                self.call_rest_api(cleanup_cmd)
            else:
                command_args = cleanup_cmd.get("command")
                self.logger.debug("Running cleanup command '{}'".
                                  format(command_args))
                cmd = Command(command_args,
                              args_subst={self.PROJECT_SUBST: self.name},
                              args_append=[self.name], excl_subst=True)
                cmd.execute()
                if cmd.getretcode() != SUCCESS_EXITVAL:
                    self.logger.info("cleanup command '{}' failed with "
                                     "code {}".
                                     format(cmd.cmd, cmd.getretcode()))
                    self.logger.info('output: {}'.format(cmd.getoutputstr()))

    def check(self, ignore_errors):
        """
        Check the output of the commands and perform logging.

        Return 0 on success, 1 if error was detected.
        """

        ret = SUCCESS_EXITVAL
        self.logger.debug("Output for project '{}':".format(self.name))
        for cmd in self.outputs.keys():
            if self.outputs[cmd] and len(self.outputs[cmd]) > 0:
                self.logger.debug("{}: {}".
                                  format(cmd, self.outputs[cmd]))

        if self.name in ignore_errors:
            self.logger.debug("errors of project '{}' ignored".
                              format(self.name))
            return

        self.logger.debug("retcodes = {}".format(self.retcodes))
        if any(rv != SUCCESS_EXITVAL and rv != CONTINUE_EXITVAL
               for rv in self.retcodes.values()):
            ret = 1
            self.logger.error("processing of project '{}' failed".
                              format(self))
            indent = "  "
            self.logger.error("{}failed commands:".format(indent))
            failed_cmds = {k: v for k, v in
                           self.retcodes.items() if v != SUCCESS_EXITVAL}
            indent = "    "
            for cmd in failed_cmds.keys():
                self.logger.error("{}'{}': {}".
                                  format(indent, cmd, failed_cmds[cmd]))
                out = self.get_cmd_output(cmd,
                                          indent=indent + "  ")
                if out:
                    self.logger.error(out)
            self.logger.error("")

        errored_cmds = {k: v for k, v in self.outputs.items()
                        if self.re_program.match(str(v))}
        if len(errored_cmds) > 0:
            ret = 1
            self.logger.error("Command output in project '{}'"
                              " contains errors:".format(self.name))
            indent = "  "
            for cmd in errored_cmds.keys():
                self.logger.error("{}{}".format(indent, cmd))
                out = self.get_cmd_output(cmd,
                                          indent=indent + "  ")
                if out:
                    self.logger.error(out)
                self.logger.error("")

        return ret
