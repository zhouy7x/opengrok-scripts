import datetime
import json
import os

env_path = '/tmp/env.json'
if os.path.exists(env_path):
    with open(env_path) as f:
        ENV = json.loads(f.read())
    # for k, v in ENV.items():
    #     os.environ.setdefault(k, v)
else:
    ENV = os.environ.copy()
SRC_ROOT = '/opengrok/src'
LOG_DIR = '/opengrok/logs'
MARK_DIR = "/tmp/project-mark"
P_list = os.popen('ls %s' % SRC_ROOT).read().split()
timezone = lambda: datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
now = lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
try:
    PORT = int(os.environ.get("PORT")) if os.environ.get("PORT") else 8080
except ValueError as e:
    PORT = 8080
try:
    MIRROR = int(os.environ.get("MIRROR")) if os.environ.get("MIRROR") else 1
except ValueError as e:
    MIRROR = 1


