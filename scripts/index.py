#!/usr/bin/python3
# -*-coding:utf-8-*-
"""
@author:lhj
@time: 2018/12/17
"""
import os
import datetime
from sys import argv
import utils


MEMSIZE = argv[1] if argv[1:] else utils.get_available_memory()
LOCKFILE = "/var/run/opengrok-indexer"
try:
    PORT = int(os.environ.get("PORT")) if os.environ.get("PORT") else 8080
except Exception as e:
    print(e)
    PORT = 8080


class IndexLock(object):
    def __init__(self, lockfile=LOCKFILE):
        self.__lockfile = lockfile
        self.__lock = None

    def check(self):
        return os.path.exists(self.__lockfile)

    @property
    def _lock(self):
        self.__lock = self.check()
        return self.__lock

    @_lock.setter
    def _lock(self, tmp):
        if tmp and (not self.__lock):
            self.__create_lock_file()

    @_lock.deleter
    def _lock(self):
        self.__delete_lock_file()
        self.__lock = False

    def __create_lock_file(self):
        try:
            f = open(self.__lockfile, 'w')
            f.close()
        except Exception as e:
            print(e)
            print("create lock failed.")
        else:
            print("create lock successfully.")
        self.__lock = self.check()

    def __delete_lock_file(self):
        os.remove(self.__lockfile)
        print("delete lock successfully.")

    def lock(self, foo):
        def __inside__(*args, **kwargs):
            if self._lock:
                print(datetime.datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S') + "  Indexer still locked, skipping indexing..")
                return 1
            else:
                self._lock = True

            code = foo(*args, **kwargs)
            # import time
            # time.sleep(10)
            del self._lock
            return code
        return __inside__

    def __call__(self, foo):
        @self.lock
        def __inside__(*args, **kwargs):
            return foo(*args, **kwargs)
        return __inside__


@IndexLock()
def index(size=MEMSIZE):
    print("Available memory size: %s " % size)
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ":  Indexing starting.")
    cmd = """
    opengrok-indexer -J=-Djava.util.logging.config.file=/opengrok/doc/logging.properties \
    -J=-Xmx%s -J=-d64 -J=-server  \
    -a /opengrok/lib/opengrok.jar -- \
    -m 256 \
    -s /opengrok/src \
    -d /opengrok/data -H -P -S \
    -W /opengrok/etc/configuration.xml \
    -U http://localhost:%d/
    """ % (size, PORT)
    # code = os.system(cmd)
    code = os.popen(cmd).read()
    print(code)
    # code = size
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ":  Indexing finished.")
    return code


if __name__ == '__main__':
    print(MEMSIZE)
    index(MEMSIZE)
