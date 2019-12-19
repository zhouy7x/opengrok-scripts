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

SRC_ROOT = os.environ.get("SRC_ROOT")
MEMSIZE = argv[1] if argv[1:] else utils.get_available_memory()
LOCKFILE = "/var/run/opengrok-indexer"
now = lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
try:
    PORT = int(os.environ.get("PORT")) if os.environ.get("PORT") else 8080
except ValueError as e:
    PORT = 8080
try:
    MIRROR = int(os.environ.get("MIRROR")) if os.environ.get("MIRROR") else 1
except ValueError as e:
    MIRROR = 1


class IndexPrepare(object):
    def __init__(self, lockfile=LOCKFILE, src_root=SRC_ROOT, port=PORT, mirror=MIRROR):
        self.__lockfile = lockfile
        self.__lock_exist = None
        self.src_root = src_root
        self.port = port
        self.mirror = mirror

    def check(self):
        return os.path.exists(self.__lockfile)

    @property
    def _lock(self):
        self.__lock_exist = self.check()
        return self.__lock_exist

    @_lock.setter
    def _lock(self, tmp):
        if tmp and (not self.__lock_exist):
            self.__create_lock_file()

    @_lock.deleter
    def _lock(self):
        self.__delete_lock_file()
        self.__lock_exist = False

    def __create_lock_file(self):
        try:
            f = open(self.__lockfile, 'w')
            f.close()
        except Exception as e:
            print(e)
            print("ERROR: create lock failed.")
        else:
            print("MESSAGE: create lock successfully.")
        self.__lock_exist = self.check()

    def __delete_lock_file(self):
        os.remove(self.__lockfile)
        print("MESSAGE: delete lock successfully.")

    def lock(self, foo):
        def __inside__(*args, **kwargs):
            if self._lock:
                print(now() + "  Indexer still locked, skipping index!")
                return 1
            else:
                self._lock = True
            code = foo(*args, **kwargs)
            del self._lock
            return code
        return __inside__

    def __call__(self, foo):
        @self.lock
        def __inside__(*args, **kwargs):
            print("self.mirror:", self.mirror)
            if self.mirror:
                print(now() + "  Mirroring starting!")
                self.create_mirror()
                print(now() + "  Mirroring finished!")
            return foo(*args, **kwargs)
        return __inside__

    def create_mirror(self):
        cmd1 = "/usr/local/bin/opengrok-mirror --all --uri http://localhost:%d/" % self.port
        utils.Shell(cmd1)
        P_list = os.popen('ls %s' % self.src_root).read().split()
        for p in P_list:
            folder = os.path.join(self.src_root, p)
            with utils.chdir(folder):
                if p.lower() in ["chromeos", "chromiumos"]:
                    shell = "/depot_tools/repo sync"
                    utils.Shell(shell)
                elif p.lower() in ["chromium", "v8"]:
                    if p.lower() == "chromium":
                        os.chdir(os.path.join(folder, 'src'))
                    elif p.lower() == "v8":
                        os.chdir(os.path.join(folder, 'v8'))

                    cmd2 = "/depot_tools/gclient sync -D -f"
                    utils.Shell(cmd2)


@IndexPrepare(LOCKFILE, SRC_ROOT, PORT, MIRROR)
def index(size=MEMSIZE):
    print("Available memory size: %s " % size)
    print(now() + "  Indexing starting.")
    cmd = """
    /usr/local/bin/opengrok-indexer -J=-Djava.util.logging.config.file=/opengrok/doc/logging.properties \
    -J=-Xmx%s -J=-d64 -J=-server  \
    -a /opengrok/lib/opengrok.jar -- \
    -m 256 \
    -s /opengrok/src \
    -d /opengrok/data -H -P -S \
    -W /opengrok/etc/configuration.xml \
    -U http://localhost:%d/
    """ % (size, PORT)
    utils.Shell(cmd)
    print(now() + "  Indexing finished.")


if __name__ == '__main__':
    index(MEMSIZE)
    print('\n\n\n')
