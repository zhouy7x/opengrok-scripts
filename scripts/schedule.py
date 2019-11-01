#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author:lhj
@time: 2019/05/08
"""
import datetime
import os
import argparse
import utils


SRC_DIR = '/opengrok/src'
P_list = os.popen('ls %s' % SRC_DIR).read().split()


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
except Exception as e:
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
        if PROJECT in ["chromeos"]:
            shell = "/depot_tools/repo sync"
            stat, ret = utils.Shell(shell)
            print(1, stat)

        else:
            cmd = "/usr/local/bin/opengrok-mirror -U 'http://localhost:%d/' -I %s" % (PORT, PROJECT)
            stat, ret = utils.Shell(cmd)
            # ret = os.popen(cmd).read()
            print(2, stat)

            if PROJECT in ["chromium", "v8"]:
                if PROJECT == "chromium":
                    os.chdir(folder + '/src')
                elif PROJECT == "v8":
                    os.chdir(folder + '/v8')

                cmd2 = "/depot_tools/gclient sync -D -f"
                stat, ret = utils.Shell(cmd2)
                print(3, stat)


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
    return os.system(cmd)


def main():
    if check_run_status():
        return

    print("DEBUG: Now create opengrok mirror...")
    check_update()
    print("DEBUG: Now run repo sync...")
    if run_update():
        print("repo-sync: Update %s failed!" % PROJECT)
    #     return 2
    else:
        print("repo-sync: Update %s successfully." % PROJECT)
    #     return 0
    remove_lock()


if __name__ == '__main__':
    if status:
        print(now(), ": Sync start!")
        main()
        print(now(), ": Sync finish!")



