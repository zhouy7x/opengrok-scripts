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
# Copyright (c) 2018, 2019, Oracle and/or its affiliates. All rights reserved.
#

from ..utils.command import Command
from .repository import Repository, RepositoryException
from shutil import which


class SubversionRepository(Repository):
    def __init__(self, logger, path, project, command, env, hooks, timeout):

        super().__init__(logger, path, project, command, env, hooks, timeout)

        if command:
            self.command = command
        else:
            self.command = which("svn")

        if not self.command:
            raise RepositoryException("Cannot get svn command")

    def reposync(self):
        svn_command = [self.command]

        #
        # The proxy configuration in SVN does not heed environment variables so
        # they need to be converted to the options.
        #
        http_proxy = self.env.get('http_proxy')
        if http_proxy:
            data = http_proxy.split(':')
            if len(data) != 2:
                self.logger.error("Cannot split '{}' into two strings by ':'".
                                  format(http_proxy))
                return 1

            svn_command.append("--config-option")
            svn_command.append("servers:global:http-proxy-host=" + data[0])
            svn_command.append("--config-option")
            svn_command.append("servers:global:http-proxy-port=" + data[1])

        no_proxy = self.env.get('no_proxy')
        if no_proxy:
            svn_command.append("--config-option")
            svn_command.append("servers:global:http-proxy-exceptions=" +
                               no_proxy)

        svn_command.append("update")
        cmd = self.getCommand(svn_command, work_dir=self.path,
                              env_vars=self.env, logger=self.logger)
        cmd.execute()
        self.logger.info("output of {}:".format(cmd))
        self.logger.info(cmd.getoutputstr())
        if cmd.getretcode() != 0 or cmd.getstate() != Command.FINISHED:
            cmd.log_error("failed to perform update")
            return 1

        return 0
