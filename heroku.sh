#!/bin/bash
#
#  Script to set Heroku environment variables


if [ -f env.sh ]; then
	. ./env.sh
else
	echo 'You must create the file "env.sh" by copying "environment.sh" and adjusting it to your liking'
	exit 1
fi

read -p "App id (empty for default): " app_id

heroku config:set --app=$app_id \
	DEBUG=$DEBUG \
	USE_SMART=$USE_SMART \
	USE_SMART_05=$USE_SMART_05 \
	USE_APP_ID=$USE_APP_ID \
	LILLY_SECRET=$LILLY_SECRET \
	GOOGLE_API_KEY=$GOOGLE_API_KEY
