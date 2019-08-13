#!/usr/bin/python3
# -*- coding:utf-8 -*-
import datetime
# from apscheduler.schedulers.background import BackgroundScheduler


def job_func(text=None):
    print(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])


# @scheduler.scheduled_job(job_func, 'interval', minutes=2)
# def job_func(text):
#     print(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
#
# scheduler = BackgroundScheduler()
# scheduler.start()
#
# if __name__ == '__main__':
#     scheduler = BackgroundScheduler()
#     # 每隔两分钟执行一次 job_func 方法
#     # scheduler.add_job(job_func, 'interval', minutes=2)
#     # 在 2017-12-13 14:00:01 ~ 2017-12-13 14:00:10 之间, 每隔两分钟执行一次 job_func 方法
#     scheduler.add_job(job_func, 'interval', seconds=5, start_date='2019-6-24 00:00:01')
#     # scheduler.add_job(job_func, 'cron', month='1-3,7-9', day='0, tue', hour='0-3')
#     scheduler.add_job(job_func, 'cron', month='1-3,7-9', day_of_week='1, 2, 3, 4', hour='0-12', minute='*',
#                       second='1-59')
#
#     scheduler.start()
#     # job_func()


import time
from apscheduler.schedulers.blocking import BlockingScheduler


def func():
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('do func  time :',ts)

def func2():
    #耗时2S
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('do func2 time：',ts)
    time.sleep(2)

def dojob():
    #创建调度器：BlockingScheduler
    scheduler = BlockingScheduler()
    #添加任务,时间间隔2S
    scheduler.add_job(func, 'interval', seconds=2, id='test_job1')
    #添加任务,时间间隔5S
    scheduler.add_job(func2, 'interval', seconds=3, id='test_job2')
    scheduler.add_job(job_func, 'cron', day_of_week='1, 2, 3, 4', hour='0-23', minute='*',
                      second='1-59')
    scheduler.start()
dojob()