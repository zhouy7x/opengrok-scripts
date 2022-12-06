# vim: set ts=4 sw=4 tw=99 et:
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
import subprocess
import signal


class FolderChanger:
    def __init__(self, folder):
        self.old = os.getcwd()
        self.new = folder

    def __enter__(self):
        os.chdir(self.new)

    def __exit__(self, type, value, traceback):
        os.chdir(self.old)


def chdir(folder):
    return FolderChanger(folder)


def check_folder(foo):
    def _inside(folder):
        if os.path.exists(folder):
            # print("Folder '%s' already exists! Exit." % folder)
            return
        foo(folder)

    return _inside


@check_folder
def mkdir(folder):
    Run(['mkdir', '-p', folder])


def Run(vec, env=os.environ.copy()):
    print(">> Executing in " + os.getcwd())
    print(' '.join(vec))
    # print("with: " + str(env))
    try:
        o = subprocess.check_output(vec, stderr=subprocess.STDOUT, env=env)
    except subprocess.CalledProcessError as e:
        print('output was: ', e.output)
        print(e)
        raise e
    o = o.decode("utf-8")
    try:
        print(o)
    except:
        print("print exception...")
    return o


def Shell(string):
    print(string)
    status, output = subprocess.getstatusoutput(string)
    print(output)
    return status, output


class TimeException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeException()


class Handler:
    def __init__(self, signum, lam):
        self.signum = signum
        self.lam = lam
        self.old = None

    def __enter__(self):
        self.old = signal.signal(self.signum, self.lam)

    def __exit__(self, type, value, traceback):
        signal.signal(self.signum, self.old)


def RunTimedCheckOutput(args, env=os.environ.copy(), timeout=None, **popenargs):
    if type(args) == list:
        print('Running: "' + '" "'.join(args) + '" with timeout: ' + str(timeout) + 's')
    elif type(args) == str:
        print('Running: "' + args + '" with timeout: ' + str(timeout) + 's')
    else:
        print('Running: ' + args)
    try:
        if type(args) == list:
            print("list......................")
            p = subprocess.Popen(args, bufsize=-1, env=env, close_fds=True, preexec_fn=os.setsid,
                                 stdout=subprocess.PIPE, **popenargs)

            with Handler(signal.SIGALRM, timeout_handler):
                try:
                    signal.alarm(timeout)
                    output = p.communicate()[0]
                    # if we get an alarm right here, nothing too bad should happen
                    signal.alarm(0)
                    if p.returncode:
                        print("ERROR: returned" + str(p.returncode))
                except TimeException:
                    # make sure it is no longer running
                    # p.kill()
                    os.killpg(p.pid, signal.SIGINT)
                    # in case someone looks at the logs...
                    print("WARNING: Timed Out 1st.")
                    # try to get any partial output
                    output = p.communicate()[0]
                    print('output 1st =', output)

                    # try again.
                    p = subprocess.Popen(args, bufsize=-1, env=env, close_fds=True,
                                         preexec_fn=os.setsid,
                                         stdout=subprocess.PIPE, **popenargs)
                    try:
                        signal.alarm(timeout)
                        output = p.communicate()[0]
                        # if we get an alarm right here, nothing too bad should happen
                        signal.alarm(0)
                        if p.returncode:
                            print("ERROR: returned" + str(p.returncode))
                    except TimeException:
                        # make sure it is no longer running
                        # p.kill()
                        os.killpg(p.pid, signal.SIGINT)
                        # in case someone looks at the logs...
                        print("WARNING: Timed Out 2nd.")
                        # try to get any partial output
                        output = p.communicate()[0]

        else:
            # import subprocess32
            p = subprocess.Popen(args, bufsize=-1, shell=True, env=env, close_fds=True, preexec_fn=os.setsid,
                                 stdout=subprocess.PIPE, **popenargs)
            try:
                output = p.communicate(timeout=timeout)[0]
                # if we get an alarm right here, nothing too bad should happen
                if p.returncode:
                    print("ERROR: returned" + str(p.returncode))
            except subprocess.TimeoutExpired:
                # make sure it is no longer running
                # p.kill()
                os.killpg(p.pid, signal.SIGINT)
                # in case someone looks at the logs...
                print("WARNING: Timed Out 1st.")
                # try to get any partial output
                output = p.communicate()[0]
                print('output 1st =', output)

                # try again.
                p = subprocess.Popen(args, bufsize=-1, shell=True, env=env, close_fds=True, preexec_fn=os.setsid,
                                     stdout=subprocess.PIPE, **popenargs)
                try:
                    output = p.communicate(timeout=timeout)[0]
                    # if we get an alarm right here, nothing too bad should happen
                    if p.returncode:
                        print("ERROR: returned" + str(p.returncode))
                except subprocess.TimeoutExpired:
                    # make sure it is no longer running
                    # p.kill()
                    os.killpg(p.pid, signal.SIGINT)
                    # in case someone looks at the logs...
                    print("WARNING: Timed Out 2nd.")
                    # try to get any partial output
                    output = p.communicate()[0]

        print('output final =', output)
        return output
    except Exception as e:
        pass


def get_available_memory():
    cmd = "cat /proc/meminfo | grep MemAvailable"
    try:
        free_mem = int(os.popen(cmd).read().split()[1])
    except Exception as e:
        print(e)
        free_mem_final = '8g'
    else:
        kw = 'k'
        if free_mem > 1024:
            kw = 'm'
            free_mem = free_mem / 1024
            if free_mem > 1024:
                kw = 'g'
                free_mem = free_mem / 1024
        free_mem_final = str(int(free_mem * 0.8)) + kw
    print(free_mem_final)
    return free_mem_final


def check_mark(dir, names):
    symbol = 0
    if not os.path.exists(dir):
        mkdir(dir)
    for name in names:
        if not os.path.exists(os.path.join(dir, name)):
            symbol = 1
            with open(os.path.join(dir, name), 'w'):
                pass
    return symbol


def RunShellWithEnv(string, env=os.environ.copy()):
    delayed = subprocess.Popen(string, shell=True, env=env, stderr=subprocess.STDOUT)
    delayed.communicate()
