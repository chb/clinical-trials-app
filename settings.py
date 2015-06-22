#!/usr/bin/env python3
#
#  You're looking for "config.default.py", no need to change things here

import os.path
import logging

if os.path.exists('./config.py'):
	from config import *
	if MONGO_HOST:
		os.environ['MONGO_HOST'] = MONGO_HOST
	if MONGO_PORT:
		os.environ['MONGO_PORT'] = MONGO_PORT
	if MONGO_DB:
		os.environ['MONGO_DB'] = MONGO_DB
	if MONGO_BUCKET:
		os.environ['MONGO_BUCKET'] = MONGO_BUCKET
	if MONGO_USER:
		os.environ['MONGO_USER'] = MONGO_USER
	if MONGO_PASS:
		os.environ['MONGO_PASS'] = MONGO_PASS
else:
	logging.warning('No "config.py" found, relying on environment variables')
	DEBUG = int(os.environ.get('DEBUG', 0)) > 0
	USE_TEST_PATIENT = int(os.environ.get('USE_TEST_PATIENT', 1)) > 0
	PATIENT_CACHE_TIMEOUT = int(os.environ.get('PATIENT_CACHE_TIMEOUT', 300))
	SESSION_SECRET = os.environ.get('SESSION_SECRET')
	SMART_APP_ID = os.environ.get('SMART_APP_ID')
	SMART_API_BASE = os.environ.get('SMART_API_BASE')
	SMART_REDIRECT = os.environ.get('SMART_REDIRECT')
	TRIALREACH_SECRET = os.environ.get('TRIALREACH_SECRET')
	GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

SMART_DEFAULTS = {
	'app_id': SMART_APP_ID,
	'api_base': SMART_API_BASE,
	'redirect_uri': SMART_REDIRECT,
}
