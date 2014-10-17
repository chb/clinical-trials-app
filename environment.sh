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

# Google Maps API key
export GOOGLE_API_KEY=
