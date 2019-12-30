#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author:lhj
@time: 2019/05/08
"""
import datetime
import json
import os
import argparse
import utils


SRC_DIR = '/opengrok/src'
P_list = os.popen('ls %s' % SRC_DIR).read().split()
env_path = '/scripts/env.json'
ENV = None
if os.path.exists(env_path):
    with open(env_path) as f:
        ENV = json.loads(f.read())


def usage():
    print(parser.format_usage())


parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('-p', '--project', type=str, choices=P_list)
parser.add_argument('-m', '--mem-size', type=str, default=None,
                    help="memory size, like: 10g, 100m, ... ")

args = parser.parse_args()
PROJECT = args.project
MEMSIZE = args.mem_size
if MEMSIZE:
    memory = MEMSIZE
else:
    memory = utils.get_available_memory()

try:
    PORT = int(os.environ.get("PORT")) if os.environ.get("PORT") else 8080
except ValueError as e:
    print(e)
    print("Wrong ENV PORT: must be a number(1000-65535)! set default 8080.")
    PORT = 8080

LOCKFILE = "/tmp/opengrok-repo-sync-%s.lock" % PROJECT

if not PROJECT or not memory:
    usage()
    status = False
else:
    print("PROJECT = %s" % PROJECT)
    print("memory size = %s" % memory)
    print("PORT = %s" % PORT)
    status = True

now = lambda: datetime.datetime.now()
"""
          Real time update of opengrok
-------------------------------------------------
1. 运行上锁
2. 检查更新
3. 更新的话，先mirror， 后reindex；
"""


def check_update():
    folder = SRC_DIR + "/" + PROJECT
    with utils.chdir(folder):
        if PROJECT in ["chromeos", "chromiumos"]:
            shell = "/depot_tools/repo sync"
            utils.RunTimedCheckOutput(shell, env=ENV)

        else:
            cmd = "/usr/local/bin/opengrok-mirror -U 'http://localhost:%d/' -I %s" % (PORT, PROJECT)
            utils.RunTimedCheckOutput(cmd, env=ENV)

            if PROJECT in ["chromium", "v8", "chrome"]:
                if PROJECT in ["chromium", "chrome"]:
                    os.chdir(folder + '/src')
                elif PROJECT == "v8":
                    os.chdir(folder + '/v8')

                cmd2 = "/depot_tools/gclient sync -D -f"
                utils.RunTimedCheckOutput(cmd2, env=ENV)


def create_lock(lock_file):
    f = open(lock_file, 'w')
    f.close()

def remove_lock():
    os.remove(LOCKFILE)

def check_run_status():
    if not os.path.exists(LOCKFILE):
        create_lock(LOCKFILE)
        return 0
    else:
        print("repo-sync: Already running!")
        return 1


def run_update():
    cmd = """
    /usr/local/bin/opengrok-reindex-project -J=-d64 \
        -J=-XX:-UseGCOverheadLimit -J=-Xmx%s -J=-server -a /opengrok/lib/opengrok.jar \
        -t /opengrok/doc/logging.properties.template -p %s \
        -l "DEBUG" -d /log \
        -P %s -U 'http://localhost:%d/' -- \
        --renamedHistory on -r dirbased -m 256 \
        -U 'http://localhost:%d/' \
        -H %s
    """ % (memory, PROJECT, PROJECT, PORT, PORT, PROJECT)
    utils.RunTimedCheckOutput(cmd, env=ENV)


def main():
    if check_run_status():
        return

    print("DEBUG: Now create opengrok mirror...")
    check_update()
    print("DEBUG: Now run repo sync...")
    run_update()
    remove_lock()


if __name__ == '__main__':
    if status:
        print(now(), ": Sync start!")
        main()
        print(now(), ": Sync finish!")



