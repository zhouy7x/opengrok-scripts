#!/bin/bash

# start crontab
/etc/init.d/cron start
crontab -l

indexer(){
	# Wait for Tomcat startup.
	date +"%F %T Waiting for Tomcat startup..."
	while [ "`curl --silent --write-out '%{response_code}' -o /dev/null 'http://localhost:8080/'`" == "000" ]; do
		sleep 1;
	done
	date +"%F %T Startup finished"

	if [[ ! -d /opengrok/data/index ]]; then
		# Perform initial indexing.
		# NOMIRROR=1 /scripts/index.sh
		/scripts/index.py
		date +"%F %T Initial reindex finished"
	fi
}

# Start all necessary services.
indexer &
catalina.sh run
