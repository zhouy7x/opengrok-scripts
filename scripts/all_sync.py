#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author:lhj
@time: 201905/13
"""
import os
import sys
import time
import datetime

import utils
import argparse


parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('-c', '--cyclic', type=bool, default=False, help="default: false")

args = parser.parse_args()
status = args.cyclic

SRC_DIR = '/opengrok/src'
LOG_DIR = '/opengrok/log'
P_list = os.popen('ls %s' % SRC_DIR).read().split()
now = lambda: datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
# memory = utils.get_available_memory()


def run(p_list, name):
    with utils.chdir(sys.path[0]):
        for project in p_list:
            memory = utils.get_available_memory()
            log_dir = "%s/%s" % (LOG_DIR, project)
            utils.mkdir(log_dir)
            cmd = "python3 schedule.py -m %s -p %s > %s/schedule-%s.log 2>&1" % (memory, project, log_dir, name)
            stat, ret = utils.Shell(cmd)
            print("stat:", stat)


if __name__ == '__main__':
    while True:
        print(">>>>>> Start time:", datetime.datetime.now())
        run(P_list, now())
        print("<<<<<< Stop time:", datetime.datetime.now())
        if not status:
            break
        else:
            print('sleep 15 mins...')
            time.sleep(15*60)
