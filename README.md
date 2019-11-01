# opengrok-scripts
For zhouy7x/opengrok docker image.

[clone]
```
mkdir -p /mnt/docker/
git clone https://github.com/zhouy7x/opengrok-scripts.git
git submodule update --init --recursive
```

[build]
```
cd /mnt/docker/opengrok-scripts/
docker build -t test/opengrok .
```
[prepare]
```
mkdir -p /mnt/docker/opengrok-scripts/VOLUMNS/src/
mkdir -p /mnt/docker/opengrok-scripts/VOLUMNS/data/
mkdir -p /mnt/docker/opengrok-scripts/VOLUMNS/log/
```
Put all your repo sources into "/mnt/docker/opengrok-scripts/VOLUMNS/src/"

[run]

1. You can set your own tomcat port(-e "PORT=9090" & -p 9090:8080), default is 8080.
2. TODO

    You can set your own update frequency(-e "FREQ=7d"), default is 7d
    ("h" means hours, "d" means days, "w" means weeks, "m" means months).
    
```
docker run -it -d \
	--name=opengrok \
	-v /mnt/docker/opengrok-scripts/VOLUMNS/src/:/opengrok/src \
	-v /mnt/docker/opengrok-scripts/VOLUMNS/data/:/opengrok/data \
	-v /mnt/docker/opengrok-scripts/VOLUMNS/log/:/opengrok/log \
	-e "FREQ=7d" \
	-p 9090:8080/tcp \
	test/opengrok \
	/bin/bash
docker exec -it opengrok /bin/bash
startup.sh
/scripts/index.py
```

