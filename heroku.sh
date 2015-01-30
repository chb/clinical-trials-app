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
	USE_TEST_PATIENT=$USE_TEST_PATIENT \
	SESSION_SECRET=$SESSION_SECRET \
	SMART_APP_ID=$SMART_APP_ID \
	SMART_API_BASE=$SMART_API_BASE \
	SMART_REDIRECT=$SMART_REDIRECT \
	LILLY_SECRET=$LILLY_SECRET \
	MONGO_HOST=$MONGO_HOST \
	MONGO_PORT=$MONGO_PORT \
	MONGO_DB=$MONGO_DB \
	MONGO_USER=$MONGO_USER \
	MONGO_PASS=$MONGO_PASS \
	MONGO_BUCKET=$MONGO_BUCKET \
