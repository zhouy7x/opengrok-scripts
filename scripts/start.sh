#!/bin/bash

indexer(){
	# Wait for Tomcat startup.
	#date +"%F %T Waiting for Tomcat startup..."
	#while [ "`curl --silent --write-out '%{response_code}' -o /dev/null 'http://localhost:8080/'`" == "000" ]; do
	#	sleep 1;
	#done
	#date +"%F %T Startup finished"

	if [[ ! -d /opengrok/data/index ]]; then
		# Populate the webapp with bare configuration.
		BODY_INCLUDE_FILE="/opengrok/data/body_include"
		if [[ -f $BODY_INCLUDE_FILE ]]; then
			mv "$BODY_INCLUDE_FILE" "$BODY_INCLUDE_FILE.orig"
		fi
		echo '<p><h1>Waiting on the initial reindex to finish.. Stay tuned !</h1></p>' > "$BODY_INCLUDE_FILE"
		/scripts/index.sh --noIndex
		rm -f "$BODY_INCLUDE_FILE"
		if [[ -f $BODY_INCLUDE_FILE.orig ]]; then
			mv "$BODY_INCLUDE_FILE.orig" "$BODY_INCLUDE_FILE"
		fi

		# Perform initial indexing.
		MIRROR=0 /scripts/index.py
		date +"%F %T Initial reindex finished"
	fi
}

# Start all necessary services.
/etc/init.d/cron start
crontab -l
indexer &
#startup.sh
catalina.sh run

