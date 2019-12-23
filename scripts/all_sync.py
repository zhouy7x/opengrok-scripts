#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author:lhj
@time: 201905/13
"""
import os
import sys
import datetime
import utils

SRC_ROOT = os.environ.get("SRC_ROOT")
LOG_DIR = '/opengrok/log'
MARK_DIR = "/tmp/project-mark"
P_list = os.popen('ls %s' % SRC_ROOT).read().split()
now = lambda: datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def run(p_list, name, reindex=False):
    with utils.chdir(sys.path[0]):
        if reindex:
            log_dir = os.path.join(LOG_DIR, 'index')
            utils.mkdir(log_dir)
            cmd = "/usr/bin/python3 /scripts/index.py >> %s/index-%s.log 2>&1" % (log_dir, name)
            stat, ret = utils.Shell(cmd)
            print("stat:", stat)
        else:
            for project in p_list:
                memory = utils.get_available_memory()
                log_dir = os.path.join(LOG_DIR, project)
                utils.mkdir(log_dir)
                cmd = "python3 schedule.py -m %s -p %s > %s/schedule-%s.log 2>&1" % (memory, project, log_dir, name)
                stat, ret = utils.Shell(cmd)
                print("stat:", stat)


if __name__ == '__main__':
    print(">>>>>> Start time:", now())
    REINDEX = False
    if utils.check_mark(MARK_DIR, P_list):
        REINDEX = True
    run(P_list, now(), REINDEX)
    print("<<<<<< Stop time:", now())

