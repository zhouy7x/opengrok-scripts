#!/bin/bash

LOCKFILE=/var/run/opengrok-indexer

if [ -f "$LOCKFILE" ]; then
    date +"%F %T Indexer still locked, skipping indexing"
    exit 1
fi

touch $LOCKFILE
date +"%F %T Indexing starting"

opengrok-indexer -J=-Djava.util.logging.config.file=/opengrok/doc/logging.properties \
    -J=-Xmx45g -J=-d64 -J=-server  \
    -a /opengrok/lib/opengrok.jar -- \
    -m 256 \
    -s /var/opengrok/src \
    -d /var/opengrok/data -H -P -S  \
    -W /var/opengrok/etc/configuration.xml \
    -U http://localhost:8080/

rm -f $LOCKFILE
date +"%F %T Indexing finished"
