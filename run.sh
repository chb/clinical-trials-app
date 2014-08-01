#!/bin/bash
#
#  run WSGI

# source environment
if [ -f env.sh ]; then
	. ./env.sh
else
	echo 'You must create the file "env.sh" by copying "environment.sh" and adjusting to your liking'
	exit 1
fi

# start the server
python3 wsgi.py
