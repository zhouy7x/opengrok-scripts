#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author:lhj
@time: 2018/12/10
"""
import os
import time
from sys import argv

PROJECT = argv[1]
LOCKFILE = "/tmp/opengrok-repo-sync-%s.lock" % PROJECT

"""
          Real time update of opengrok
-------------------------------------------------
1. 运行上锁
2. 检查更新
3. 更新的话，先mirror， 后reindex；没更新，sleep 15 min

"""


def check_update():
    cmd = "opengrok-mirror -U 'http://localhost:8080/' -I %s" % PROJECT
    ret = os.popen(cmd).read()
    print(ret)
    if "No incoming changes for repositories" in ret:
        return 0
    else:
        return 1

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
    opengrok-reindex-project -J=-d64 \
        -J=-XX:-UseGCOverheadLimit -J=-Xmx45g -J=-server -a /opengrok/lib/opengrok.jar \
        -t /opengrok/doc/logging.properties.template -p %s \
        -l "DEBUG" -d /log \
        -P %s -U 'http://localhost:8080/' -- \
        --renamedHistory on -r dirbased -G -m 256 \
        -c /usr/local/bin/ctags -U 'http://localhost:8080/' \
         -H %s
    """ % (PROJECT, PROJECT, PROJECT)
    return os.system(cmd)


def main():
    if check_run_status():
        return

    while True:
        print("DEBUG: Now create opengrok mirror...")
        if check_update():
            print("DEBUG: Now run repo sync...")
            if run_update():
                print("repo-sync: Update %s failed!" % PROJECT)
            else:
                print("repo-sync: Update %s successfully." % PROJECT)
            # clean_up()
        else:
            print("repo-sync: no source update, sleep 15m")
            time.sleep(15*60)

    remove_lock()


if __name__ == '__main__':
    main()


