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
from flask import Flask, request, render_template, session, jsonify, abort, send_from_directory
from flask.sessions import SessionInterface
from beaker.middleware import SessionMiddleware

# settings
DEBUG = int(os.environ.get('DEBUG', 0)) > 0
USE_SMART = int(os.environ.get('USE_SMART', 0)) > 0
USE_SMART_05 = int(os.environ.get('USE_SMART_05', 0)) > 0
USE_NLP = int(os.environ.get('USE_NLP', 0)) > 0
LILLY_SECRET = os.environ.get('LILLY_SECRET')

# SMART
if USE_SMART:
	import smart

# App
from ClinicalTrials.trial import Trial
from ClinicalTrials.lillyserver import LillyV2Server
from patient import Patient
from trialfinder import TrialFinder
from trialmatcher import *

# session setup
session_opts = {
	'session.type': 'file',
	'session.timeout': 3600,
	'session.cookie_expires': 3600,
	'session.data_dir': './session_data',
	'session.auto': True
}

class BeakerSessionInterface(SessionInterface):
	def open_session(self, app, request):
		session = request.environ['beaker.session']
		return session
	
	def save_session(self, app, session, response):
		session.save()

app = application = Flask(__name__)

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


# ------------------------------------------------------------------------------ Utilities

def _reset_session(with_runs=False):
	""" Removes patient-related session settings.
	"""
	if 'record_id' in session:
		del session['record_id']
	if 'token' in session:
		del session['token']
	if 'consumer_key' in session:
		del session['consumer_key']
	if 'consumer_secret' in session:
		del session['consumer_secret']
	
	if 'patient' in session:
		del session['patient']

def _get_smart():
	if USE_SMART:
		return smart.client()
	return None

# ------------------------------------------------------------------------------ Index

@app.route('/')
@app.route('/index.html')
def index():
	""" The app's main page.
	"""
	
	# look at URL params first, if they are there store them in the session
	api_base = request.args.get('api_base') if USE_SMART else 'none'
	if api_base is not None:
		session['api_base'] = api_base
	else:
		api_base = session.get('api_base')
	
	# no endpoint, show selector
	if not api_base:
		_reset_session()
		logging.debug('redirecting to endpoint selection')
		redirect('endpoint_select')
	
	# determine record id
	record_id = request.args.get('record_id')
	if record_id is not None:
		old_id = sess.get('record_id')
		
		# reset session if we get a new record (or none)
		if old_id != record_id:
			_reset_session()
		
		# set (or don't) the record id
		if 0 != int(record_id):
			session['record_id'] = record_id
		else:
			record_id = None
	else:
		record_id = session.get('record_id')
	
	# try to connect to SMART
	smart_client = _get_smart()
	if smart_client is None and 'none' != api_base:
		return "Cannot connect to SMART sandbox at %s" % api_base
	
	# using SMART, make sure we have a patient id
	if smart_client is not None:
		
		# no record id, call launch page
		if record_id is None:
			launch = smart_client.launch_url
			if launch is None:
				return "Unknown app start URL, cannot launch"
			
			logging.debug('redirecting to app launch page')
			redirect(launch)
			return
		
		# still here, test the token
		if not smart.test_record_token():
			smart_client.token = None
			try:
				sess['token'] = smart_client.fetch_request_token()
			except Exception as e:
				_reset_session()
				logging.error("Failed getting request token. %s" % e)
				return "Failed to obtain access permissions, please reload"
			
			# now go and authorize the token
			logging.debug("Have request token, redirecting to authorize token")
			redirect(smart_client.auth_redirect_url)
			return
	
	# everything in order, render index
	defs = {
		'debug': DEBUG,
		'use_smart': USE_SMART,
		'smart_v05': USE_SMART_05,
		'google_api_key': os.environ.get('GOOGLE_API_KEY')
	}
	
	return render_template('index.html', defs=defs, api_base=api_base)


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


@app.route('/authorize')
def authorize():
	""" Extract the oauth_verifier from the callback and exchange it for an
	access token.
	"""
	smart_client = _get_smart()
	if smart_client is None:
		return "Cannot connect to SMART sandbox"
	
	verifier = request.args.get('oauth_verifier')
	try:
		session['token'] = smart_client.exchange_token(verifier)
	except Exception as e:
		logging.error("Token exchange failed: %s" % e)
		return str(e)
	
	# looks good!
	logging.debug("Got an access token, returning home")
	redirect('/index.html?api_base=%s&record_id=%s' % (session['api_base'], session['record_id']))


@app.route('/endpoint_select')
def endpoints():
	""" Shows all possible endpoints, sending the user back to index when one is
	chosen.
	"""
	
	# reset session api_base
	if 'api_base' in sess:
		del sess['api_base']
	
	# get the callback
	# NOTE: this is done very cheaply, we need to make sure to end the url with either "?" or "&"
	callback = request.args.get('callback', 'index.html?')
	if '?' != callback[-1] and '&' != callback[-1]:
		callback += '&' if '?' in callback else '?'
	
	# render selections
	return render_template('endpoint_select.html', endpoints=smart.endpoints(), callback=callback)


# ------------------------------------------------------------------------------ Patient

@app.route('/patients/<id>', methods=['GET', 'PUT'])
def patients(id):
	""" Updates - if PUT - and returns the current patient's data as JSON.
	"""
	pat = session.get('patient')
	patient = Patient('x', pat)
	
	# PUT new demographics
	if 'PUT' == request.method:
		patient.updateWith(request.form)
		session['patient'] = patient.json
	
	# auto-fetch demographics
	elif USE_SMART and not patient.did_fetch:
		smart.fetch_patient_data(_get_smart(), patient)
	
	return jsonify(patient.api)


# ------------------------------------------------------------------------------ Trials

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
	
	# force country to be US for now
	patient.country = "United States"
	
	finder = TrialFinder(trialserver, patient)
	found = finder.find(request.args)
	
	results = []
	trialmatcher.patient = patient
	for result in trialmatcher.match(found):
		results.append(result.js)
	
	return jsonify({'results': results or []})


# ------------------------------------------------------------------------------ Enrolling

@app.route('/enroll')
def enroll():
	return render_template('enroll.html', {'title': "Randomize"})


# ------------------------------------------------------------------------------ Static Files

@app.route('/static/<filename>')
def static_file(filename):
	return send_from_directory('static', filename)

@app.route('/templates/<ejs_name>.ejs')
def ejs(ejs_name):
	return send_from_directory('templates', '%s.ejs' % ejs_name)


# start the app
if '__main__' == __name__:
	app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
	app.session_interface = BeakerSessionInterface()
	
	if DEBUG:
		logging.basicConfig(level=logging.DEBUG)
		app.run(debug=True, port=8008)
	else:
		logging.basicConfig(level=logging.WARNING)
		app.run(host='0.0.0.0', port=8008)
