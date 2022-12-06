#!/bin/bash

docker start opengrok
pushd /path/to/your/opengrok/expect
/usr/bin/expect ./start-opengrok > start-opengrok.log
popd

exit 0
