# opengrok-scripts
For zhouy7x/opengrok docker image. 

* Official source url: https://github.com/oracle/opengrok.git

[clone]
```
mkdir -p /mnt/docker/
cd /mnt/docker/ && git clone https://gitlab.devtools.intel.com/zhouy7x/opengrok.git
```

[docker network proxy]
```
Reference: https://blog.frognew.com/2017/01/docker-http-proxy.html
Add
  EnvironmentFile=/etc/sysconfig/docker
to /lib/systemd/system/docker.service
Add or modify
  HTTP_PROXY=http://proxy.example.com:80/
  HTTPS_PROXY=http://proxy.example.com:80/
  NO_PROXY=localhost,127.0.0.1,internal-docker-registry.somecorporation.com
  export HTTP_PROXY HTTPS_PROXY NO_PROXY
to /etc/sysconfig/docker
Enable configure
  systemctl daemon-reload
  systemctl restart docker
```
[build]
```
cd /mnt/docker/opengrok/
docker build -t zhouy7x/opengrok .
```
[prepare]
```
mkdir -p /mnt/docker/opengrok-volumes/src/
mkdir -p /mnt/docker/opengrok-volumes/data/
mkdir -p /mnt/docker/opengrok-volumes/logs/
```
Put all your repo sources into "/mnt/docker/opengrok-volumes/src/"

[run]
```
cd /mnt/docker/opengrok/
docker run -it -d \
	--name=opengrok \
	-v /mnt/docker/opengrok-scripts/VOLUMES/src/:/opengrok/src \
	-v /mnt/docker/opengrok-scripts/VOLUMES/data/:/opengrok/data \
	-v /mnt/docker/opengrok-scripts/VOLUMES/logs/:/opengrok/logs \
	-p 8080:8080/tcp \
	zhouy7x/opengrok
```
1. You can set your own tomcat port(-p <your_port>:8080/tcp), default is 8080.
2. Now can auto index and update all projects.
3. If your projects are too large(such as chromium and chromiumos), It maybe needs
a long time to first index all projects(about 6-12 hours, dependence on your device performance).
4. Now reindex all projects every Saturday 3:00 am(takes about 3 hours).
5. TODO

    You can set your own update frequency(-e "REINDEX=7d"), default is 7d
    ("h" means hours, "d" means days, "w" means weeks, "m" means months).
6. If you want to restart container, you should do the following steps after restart.
```
docker start opengork
```