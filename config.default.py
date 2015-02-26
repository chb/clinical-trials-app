#!/usr/bin/env python3
#
# App settings
# copy to "config.py"

DEBUG = 1
USE_TEST_PATIENT = 1
SESSION_SECRET = "supersecretsecret"

# SMART
SMART_APP_ID = "my_web_app"
SMART_API_BASE = "https://fhir-api.smartplatforms.org"
SMART_REDIRECT = "http://localhost:8000/fhir-app/"

# LillyCOI API key (base64 encoded "key:secret" string)
LILLY_SECRET = None

# Mongo params; leave host/port/db at None for default localhost connection
MONGO_HOST = None
MONGO_PORT = None
MONGO_DB = None
MONGO_USER = None
MONGO_PASS = None
MONGO_BUCKET = None
