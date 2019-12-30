#!/usr/bin/python3
# -*-coding:utf-8-*-
"""
@author:lhj
@time: 2018/12/17
"""
import json
import os
import datetime
from sys import argv
import utils

SRC_ROOT = os.environ.get("SRC_ROOT")
MEMSIZE = argv[1] if argv[1:] else utils.get_available_memory()
LOCKFILE = "/var/run/opengrok-indexer"
MARK_DIR = "/tmp/project-mark"
now = lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

env_path = '/scripts/env.json'
ENV = None
if os.path.exists(env_path):
    with open(env_path) as f:
        ENV = json.loads(f.read())

try:
    PORT = int(os.environ.get("PORT")) if os.environ.get("PORT") else 8080
except ValueError as e:
    PORT = 8080
try:
    MIRROR = int(os.environ.get("MIRROR")) if os.environ.get("MIRROR") else 1
except ValueError as e:
    MIRROR = 1


class IndexPrepare(object):
    def __init__(self, lockfile=LOCKFILE, src_root=SRC_ROOT, port=PORT, mirror=MIRROR, mark=MARK_DIR):
        self.__lockfile = lockfile
        self.__lock_exist = None
        self.src_root = src_root
        self.port = port
        self.mirror = mirror
        self.mark = mark
        self.projects = os.popen('ls %s' % self.src_root).read().split()

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
            if self.mirror:
                print(now() + "  Mirroring starting!")
                self.create_mirror()
                print(now() + "  Mirroring finished!")
            else:
                with open(env_path, 'w') as f:
                    f.write(json.dumps(os.environ.copy()))
            # mark names of all projects.
            os.system('rm -rf %s' % self.mark)
            utils.check_mark(self.mark, self.projects)
            return foo(*args, **kwargs)
        return __inside__

    def create_mirror(self):
        cmd1 = "/usr/local/bin/opengrok-mirror --all --uri http://localhost:%d/" % self.port
        utils.RunTimedCheckOutput(cmd1, env=ENV)
        for p in self.projects:
            folder = os.path.join(self.src_root, p)
            with utils.chdir(folder):
                if p.lower() in ["chromeos", "chromiumos"]:
                    shell = "/depot_tools/repo sync"
                    utils.RunTimedCheckOutput(shell, env=ENV)
                elif p.lower() in ["chromium", "v8", "chrome"]:
                    if p.lower() in ["chromium", "chrome"]:
                        os.chdir(os.path.join(folder, 'src'))
                    elif p.lower() == "v8":
                        os.chdir(os.path.join(folder, 'v8'))

                    cmd2 = "/depot_tools/gclient sync -D -f"
                    utils.RunTimedCheckOutput(cmd2, env=ENV)


@IndexPrepare(LOCKFILE, SRC_ROOT, PORT, MIRROR, MARK_DIR)
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
    utils.RunTimedCheckOutput(cmd, env=ENV)
    print(now() + "  Indexing finished.")


if __name__ == '__main__':
    index(MEMSIZE)
    print('\n\n\n')
