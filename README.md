# opengrok-scripts
For zhouy7x/opengrok docker image.

[clone]
```
mkdir -p /mnt/docker/
git clone https://github.com/zhouy7x/opengrok-scripts.git
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

1. You can set your own tomcat port(-e "PORT=9090"), default is 9090.
2. TODO

    You can set your own update frequency(-e "FREQ=7d"), default is 7d
    ("h" means hours, "d" means days, "w" means weeks, "m" means months).
    
```
docker run -it -d \
	--net=host \
	--name=opengrok \
	-v /mnt/docker/opengrok-scripts/VOLUMNS/src/:/src \
	-v /mnt/docker/opengrok-scripts/VOLUMNS/data/:/data \
	-v /mnt/docker/opengrok-scripts/VOLUMNS/log/:/log \
	-e "PORT=9090" \
	-e "FREQ=7d" \
	test/opengrok \
	/bin/bash
docker exec -it opengrok /bin/bash
startup.sh
/scripts/index.py
```

