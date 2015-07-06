#!/usr/bin/env python3
#
# App settings
# copy to "config.py"

DEBUG = 0
USE_TEST_PATIENT = 0
PATIENT_CACHE_TIMEOUT = 300      # seconds until cached patient data becomes stale
SESSION_SECRET = "supersecretsecret"

# SMART
SMART_APP_ID = "my_web_app"
SMART_API_BASE = "https://fhir-open-api-dstu2.smarthealthit.org"
SMART_REDIRECT = "http://localhost:8000/fhir-app/"

# TrialReach API key (base64 encoded "key:secret" string)
TRIALREACH_SECRET = None

# Mongo params; leave host/port/db at None for default localhost connection
MONGO_HOST = None
MONGO_PORT = None
MONGO_DB = None
MONGO_USER = None
MONGO_PASS = None
MONGO_BUCKET = None		# this must be set to a name, there is no default value
