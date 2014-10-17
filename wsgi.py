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
import py.flaskbeaker as flaskbeaker

# settings
DEBUG = int(os.environ.get('DEBUG', 0)) > 0
USE_NLP = int(os.environ.get('USE_NLP', 0)) > 0
LILLY_SECRET = os.environ.get('LILLY_SECRET')
SMART_DEFAULTS = {
	'app_id': os.environ.get('SMART_APP_ID'),
	'api_base': os.environ.get('SMART_API_BASE'),
	'redirect_uri': os.environ.get('SMART_REDIRECT'),
}

# SMART
import py.smartclient.fhirclient.client as smart

# App
from py.clinicaltrials.trial import Trial
from py.clinicaltrials.lillyserver import LillyV2Server
from py.trialpatient import TrialPatient
from py.trialfinder import TrialFinder
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

def _get_smart():
	state = session.get('smart_state')
	if state:
		return smart.FHIRClient(state=state)
	return smart.FHIRClient(settings=SMART_DEFAULTS)

def _save_smart(client):
	session['smart_state'] = client.state


# MARK: Index

@app.route('/')
@app.route('/index.html')
def index():
	""" The app's main page.
	"""
	smart_client = _get_smart()
	
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
		'use_smart': True,
		'google_api_key': os.environ.get('GOOGLE_API_KEY')
	}
	
	return render_template('index.html', defs=defs)


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
		return """<h1>Authorization Error</h1><p>{}</p><p><a href="/">Start over</a></p>""".format(e)
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

@app.route('/patients/x')				# TODO: remove
@app.route('/patient', methods=['GET', 'PUT'])
def patient():
	""" Updates - if PUT - and returns the current patient's data as JSON.
	"""
	client = _get_smart()
	patient = client.patient
	if patient is None:
		logging.info("Trying to retrieve /patient without authorized smart client")
		return 401
	
	# TODO: REFACTOR
	
	pat = session.get('patient')
	patient = TrialPatient('x', pat)
	
	# PUT new demographics
	if 'PUT' == request.method:
		patient.updateWith(request.form)
		session['patient'] = patient.json
	
	return jsonify(patient.api)


# MARK: Trials

@app.route('/find', methods=['GET', 'PUT'])
def find():
	""" Retrieve trials for the given patient.
	"""
	id = 'x'
	if 'PUT' == request.method:
		patient = Patient(id)
		patient.updateWith(request.form)
	else:
		pat = session.get('patient')
		patient = Patient(id, pat)
	
	finder = TrialFinder(trialserver, patient)
	finder.fetch_all = False
	found = finder.find(request.args)
	
	results = []
	trialmatcher.patient = patient
	for result in trialmatcher.match(found):
		results.append(result.js)
	
	return jsonify({'results': results or []})


# MARK: Enrolling

@app.route('/enroll')
def enroll():
	return render_template('enroll.html', {'title': "Randomize"})


# MARK: Static Files

@app.route('/static/<filename>')
def static_file(filename):
	return send_from_directory('static', filename)

@app.route('/templates/<ejs_name>.ejs')
def ejs(ejs_name):
	return send_from_directory('templates', '%s.ejs' % ejs_name)


# start the app
if '__main__' == __name__:
	flaskbeaker.FlaskBeaker.setup_app(app)
	
	if DEBUG:
		logging.basicConfig(level=logging.DEBUG)
		app.run(debug=True, port=8000)
	else:
		logging.basicConfig(level=logging.WARNING)
		app.run(host='0.0.0.0', port=8000)
