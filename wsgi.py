#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import json
import re
import markdown
import codecs
from datetime import datetime

# flask
from flask import Flask, request, redirect, render_template, session, jsonify, send_from_directory

# settings
DEBUG = int(os.environ.get('DEBUG', 0)) > 0
LILLY_SECRET = os.environ.get('LILLY_SECRET')
SMART_DEFAULTS = {
	'app_id': os.environ.get('SMART_APP_ID'),
	'auth_type': 'oauth2',
	'api_base': os.environ.get('SMART_API_BASE'),
	'redirect_uri': os.environ.get('SMART_REDIRECT'),
}

# SMART
import py.smartclient.fhirclient.client as smart

# App
from py.clinicaltrials.lillyserver import LillyV2Server
from py.trialpatient import TrialPatient
from py.trialfinder import TrialFinder
from py.targettrial import TargetTrial
from py.trialmatcher import *

app = Flask(__name__)

# Trial Server
trialserver = None
if LILLY_SECRET is not None:
	trialserver = LillyV2Server(LILLY_SECRET)

# Trial Matcher
trialmatcher = TrialSerialMatcher()
trialmatcher.modules = [
	TrialGenderMatcher(),
	TrialAgeMatcher()
]


# MARK: Utilities

def _reset_session():
	""" Resets session state.
	"""
	if 'smart_state' in session:
		del session['smart_state']

def _get_smart(iss=None, launch=None):
	settings = SMART_DEFAULTS
	if iss is not None:		# launched from EHR, restart
		_reset_session()
		settings['api_base'] = iss
		if launch is not None:
			settings['launch_token'] = launch
	
	# use state if we have state or init from settings
	state = session.get('smart_state')
	if state:
		return smart.FHIRClient(state=state)
	return smart.FHIRClient(settings=settings)

def _save_smart(client):
	session['smart_state'] = client.state


# MARK: Index

@app.route('/')
@app.route('/index.html')
def index():
	""" The app's main page.
	"""
	smart_client = _get_smart(iss=request.args.get('iss'), launch=request.args.get('launch'))
	
	# no patient yet, maybe need to authorize
	if smart_client.patient is None:
		if not smart_client.ready:
			auth_url = smart_client.authorize_url
			_save_smart(smart_client)
			logging.debug('redirecting to app launch page at {}'.format(auth_url))
			return redirect(auth_url)
		
		return "Ready, but no patient"
	
	# patient data ready
	defs = {
		'debug': DEBUG,
		'need_patient_banner': True,
		'google_api_key': os.environ.get('GOOGLE_API_KEY')
	}
	
	return render_template('index.html', defs=defs)

@app.route('/fhir-app/launch.html')
def from_fhir_app():
	return redirect('/?{}'.format(request.query_string.decode("utf-8")))

@app.route('/logout')
def logout():
	""" Throws away all state.
	"""
	_reset_session()
	return redirect('/')


@app.route('/help')
@app.route('/help.html')
def help():
	""" Show the help page.
	"""
	help_html = os.path.join('static', 'help.html')
	help_md = os.path.join('templates', 'help.md')
	
	# update help html from markdown if needed
	if not os.path.exists(help_html) \
		or os.path.getmtime(help_html) < os.path.getmtime(help_md):
		
		with codecs.open(help_md, 'r', 'utf-8') as help:
			text = markdown.markdown(help.read())
			links = [{'text': "Trial Eligibility App", 'href': '/'}]
			html = render_template('master.html', content=text, links=links)
			
			# render to html
			with codecs.open(help_html, 'w', 'utf-8') as write:
				write.write(html)
	
	return send_from_directory('static', 'help.html')


@app.route('/fhir-app/')
def callback():
	""" Extract the OAuth code from the callback and exchange it for an
	access token.
	"""
	smart_client = _get_smart()
	try:
		smart_client.handle_callback(request.url)
		_save_smart(smart_client)
	except Exception as e:
		return """<h1>Authorization Error</h1><p>{}</p><p><a href="/logout">Start over</a></p>""".format(e)
	logging.debug("Got an access token, returning home")
	return redirect('/')


@app.route('/endpoint_select')
def endpoints():
	""" Shows all possible endpoints, sending the user back to index when one is
	chosen.
	"""
	raise Exception("Must re-implement")
	# get the callback
	# NOTE: this is done very cheaply, we need to make sure to end the url with either "?" or "&"
	callback = request.args.get('callback', 'index.html?')
	if '?' != callback[-1] and '&' != callback[-1]:
		callback += '&' if '?' in callback else '?'
	
	# render selections
	return render_template('endpoint_select.html', endpoints=smart.endpoints(), callback=callback)


# MARK: Patient

@app.route('/patients/<id>')						# placeholder, id will be ignored
@app.route('/patient')
def patient(id=None):
	""" Returns the current patient's data as JSON.
	"""
	patient = TrialPatient.load_from_fhir(_get_smart())
	if patient is None:
		logging.info("Trying to retrieve /patient without authorized smart client")
		return 401
	
	return jsonify(patient.for_api())


# MARK: Trials

@app.route('/find/')
def find():
	""" Retrieve trials for the current patient.
	"""
	patient = TrialPatient.load_from_fhir(_get_smart())
	if patient is None:
		logging.info("Trying to find trials for a patient without authorized smart client")
		return 401
	
	finder = TrialFinder(trialserver, trial_class=TargetTrial)
	#finder.fetch_all = False
	found = finder.find(request.args)
	
	results = []
	for result in trialmatcher.match(found, patient):
		results.append(result.for_api())
	
	return jsonify({'results': results or []})


# MARK: Enrolling

@app.route('/enroll')
def enroll():
	return render_template('enroll.html', {'title': "Randomize"})


# MARK: Static Files

@app.route('/static/<filename>')
def static_file(filename):
	return send_from_directory('static', filename)


# start the app
if '__main__' == __name__:
	import py.smartclient.flaskbeaker as flaskbeaker
	flaskbeaker.FlaskBeaker.setup_app(app)
	
	if DEBUG:
		logging.basicConfig(level=logging.DEBUG)
		app.run(debug=True, port=8000)
	else:
		logging.basicConfig(level=logging.WARNING)
		app.run(host='0.0.0.0', port=8000)
