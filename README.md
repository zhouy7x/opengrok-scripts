# opengrok-scripts
For zhouy7x/opengrok docker image. 

* Official source url: https://github.com/oracle/opengrok.git

[clone]
```
mkdir -p /mnt/docker/
cd /mnt/docker/ && git clone https://github.com/zhouy7x/opengrok-scripts.git opengrok
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
1. set .boto file for chromium build "NO_AUTH_BOTO_CONFIG" config;
2. build image:
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
```
docker exec -it opengrok /bin/bash
crontab -e   # add new line: 0  3  *    *   6    /usr/bin/python3 /scripts/all_sync.py >> /opengrok/logs/all_sync.log 2>&1 &
```
then save and exit.
5. TODO

    You can set your own update frequency(-e "REINDEX=7d"), default is 7d
    ("h" means hours, "d" means days, "w" means weeks, "m" means months).
6. Start container:
```
docker start opengork
```
7. Auto start container when server reboot:
 a. ```cd /mnt/docker/opengrok/expect/```
 b. edit start-docker.sh  # e.g. "pushd /mnt/docker/opengrok/expect"
 c. save and exit;
 d.  
```
sudo chmod 755 ./start-docker.sh
sudo mv ./start-docker.sh /etc/init.d/
cd /etc/init.d/
sudo update-rc.d start-docker.sh defaults 90
```
8. If you need to remove autostart:
```
sudo update-rc.d -f start-docker.sh remove
```
  
