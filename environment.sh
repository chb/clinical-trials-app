#!/bin/sh
#
# environment variables
# copy to "env.sh" and make executable if you change these!

export DEBUG=1

# SMART
export SMART_APP_ID="my_web_app"
export SMART_API_BASE="https://fhir-api.smartplatforms.org"
export SMART_REDIRECT="http://localhost:8000/fhir-app/"

# LillyCOI API key (base64 encoded "key:secret" string)
export LILLY_SECRET=

# Mongo params; leave host/port/db empty for default localhost connection
export MONGO_HOST=
export MONGO_PORT=
export MONGO_DB=
export MONGO_USER=
export MONGO_PASS=
export MONGO_BUCKET=
