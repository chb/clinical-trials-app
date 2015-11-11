#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import io
import sys
import logging
import json
import re
import markdown
import codecs
import datetime

# flask
from flask import Flask, request, redirect, render_template, abort, session, jsonify, send_from_directory
from settings import *

# SMART
import py.smartclient.fhirclient.client as smart
import py.smartclient.flaskbeaker as flaskbeaker

# App
from trialpatient import TrialPatient, TrialPatientInfo
from trialfinder import TrialFinder
from targettrial import TargetTrial, TargetTrialInfo
from trialmatcher import *
from clinicaltrials.trialreachserver import TrialReachServer
from localutils import LocalTrialServer, LocalJSONCache, LocalImageCache
from clinicaltrials.jsondocument.mongoserver import MongoServer

app = Flask(__name__)
flaskbeaker.FlaskBeaker.setup_app(app)
app.secret_key = SESSION_SECRET or 'supersecretkey'

# Trial Caches
LocalTrialServer.trial_cache = LocalJSONCache('trial-cache')
tpdir = os.path.join('sarah-cannon-pilot', 'JSON')
LocalTrialServer.profile_cache = LocalJSONCache(tpdir)
LocalTrialServer.profile_cache.can_write = False

# Local Storage
jsonserver = MongoServer()
TrialPatient.hookup(jsonserver, os.environ.get('MONGO_BUCKET'))
TargetTrialInfo.hookup(jsonserver, os.environ.get('MONGO_BUCKET'))
TrialPatientInfo.hookup(jsonserver, os.environ.get('MONGO_BUCKET'))


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
		return smart.FHIRClient(state=state, save_func=_save_smart)
	return smart.FHIRClient(settings=settings, save_func=_save_smart)

def _save_smart(state):
	session['smart_state'] = state

def _get_patient():
	""" Return a `TrialPatient` instance, as authorized in the session.
	
	:raises: Exception unless returning a patient instance
	"""
	if USE_TEST_PATIENT:
		with io.open('static/patient-test.json', 'r', encoding='utf-8') as h:
			return TrialPatient('x', json.load(h))
	
	smart = _get_smart()
	if smart.patient_id is None:
		raise Exception('Did read patient via SMART, but did not receive a patient_id')
	
	# Try to load from MongoDB and use if it's not older than 5 minutes
	now = datetime.datetime.now()
	patient = TrialPatient(smart.patient_id)
	patient.load()
	if patient.cached is not None and patient.cached + datetime.timedelta(seconds=PATIENT_CACHE_TIMEOUT) > now:
		logging.debug('Patient was recently cached, returning cached data from {}'.format(patient.cached))
		return patient
	
	logging.debug('Loading patient data via FHIR, was last cached {}'.format(patient.cached))
	patient = TrialPatient.load_from_fhir(smart)
	patient.cached = now
	patient.store()
	
	return patient


# MARK: Index

@app.route('/')
@app.route('/index.html')
def index():
	""" The app's main page.
	"""
	defs = {
		'debug': DEBUG,
		'need_patient_switcher': not USE_TEST_PATIENT,
		#'google_api_key': GOOGLE_API_KEY,
	}
	
	if not USE_TEST_PATIENT:
		mrn = request.args.get('mrn')
		smart_client = _get_smart(iss=request.args.get('iss'), launch=request.args.get('launch'))
		if mrn:
			if smart_client.patient_id != mrn:
				smart_client.reset_patient()
			if smart_client.patient is None:
				smart_client.patient_id = mrn
		
		# no patient yet, maybe need to authorize
		if smart_client.patient is None:
			if not smart_client.ready:
				auth_url = smart_client.authorize_url
				if auth_url is not None:
					logging.debug('redirecting to app launch page at {}'.format(auth_url))
					return redirect(auth_url)
				logging.debug('Server does not advertise an authorize_url')
			
			# no patient, but authorized: let user select patient manually
			# (since the server did not do that). This might actually load the
			# patient since we just called smart_client.ready.
			if smart_client.patient is None:
				return render_template('manual_patient.html', defs=defs, mrn=mrn)
	
	# patient data ready
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
			html = render_template('content.html', content=text, links=links)
			
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

@app.route('/patients/<id>/photo')
@app.route('/patient/photo')
def patient_photo(id=None):
	""" Return the patient's photo, if any, placeholder image otherwise.
	"""
	try:
		patient = _get_patient()
	except Exception as e:
		logging.error("Exception trying to retrieve patient photo: {}".format(e))
		abort(500)
	if id is not None and id != patient._id:
		logging.error("Trying to retrieve photo of patient {} while being authorized for patient {}".format(id, patient._id))
		abort(401)
	
	# check cache
	cache = LocalImageCache('patient-photos')
	cached, fname = cache.existing_cache_path(patient.id, contentType='image/jpeg')
	if cached is None:
		cached, fname = cache.existing_cache_path(patient.id, contentType='image/png')
	if cached is not None:
		return send_from_directory('patient-photos', fname)
	
	# no cache, load from FHIR
	typ, dat = patient.load_photo()
	if dat is not None:
		cpath, fname = cache.store(patient.id, dat, contentType=typ)
		return send_from_directory('patient-photos', fname)
	
	return static_file('portrait_default.png')



@app.route('/patients/<id>')						# placeholder, id will be ignored
@app.route('/patient')
def patient(id=None):
	""" Returns the current patient's data as JSON.
	"""
	try:
		patient = _get_patient()
	except Exception as e:
		logging.error("Exception trying to retrieve /patient: {}".format(e))
		abort(500)
	if id is not None and id != patient._id:
		logging.error("Trying to retrieve patient {} while being authorized for patient {}".format(id, patient._id))
		abort(401)
	return jsonify(patient.for_api(stripped=True))


# MARK: Trials

@app.route('/find/')
def find():
	""" Retrieve trials for the current patient.
	"""
	try:
		patient = _get_patient()
	except Exception as e:
		logging.error("Trying to find trials for a patient without authorized smart client: {}".format(e))
		abort(401)
	
	# find trials
	trialserver = None
	if TRIALREACH_SECRET is not None:
		trialserver = TrialReachServer(TRIALREACH_SECRET)
	trialserver = LocalTrialServer(os.path.join('sarah-cannon-pilot', 'JSON'), trialserver)
	
	finder = TrialFinder(trialserver, trial_class=TargetTrial)
	#finder.fetch_all = False
	found = finder.find(request.args)
	
	# match trials and add patient specific trial information
	trialmatcher = TrialSerialMatcher()
	trialmatcher.modules = [
		TrialGenderMatcher(),
		TrialAgeMatcher(),
		TrialProfileMatcher(),
	]
	results = []
	for result in trialmatcher.match(patient, found):
		result.add_patient_info(patient)
		results.append(result.for_api())
	
	return jsonify({'patient_id': patient.id, 'results': results or []})

@app.route('/trials/<trial_id>/info', methods=['GET', 'PUT'])
def trial_info(trial_id):
	""" "PUT" will update the trial info for the given trial.
	"""
	trial = TargetTrial(trial_id)
	
	# check method and update
	if 'PUT' == request.method:
		if request.json is None:
			abort(400, "No JSON document body")
		trial.set_local_info(request.json)
	
	# check if trial info exists
	if trial.trial_info is None:
		abort(404)
	
	return jsonify({'trial': trial.trial_info.for_api()})

@app.route('/trials/<trial_id>/patient/<patient_id>/info', methods=['PUT'])
def trial_patient_info(trial_id, patient_id):
	""" Update info concerning a trial-patient combination.
	"""
	if request.json is None:
		abort(400, "No JSON document body")
	
	# only allow to get info about the patient this user has currently selected
	try:
		patient = _get_patient()
	except Exception as e:
		logging.error("Failed to retrieve trial info for patient: {}".formate(e))
	if patient.id != patient_id:
		logging.error("Trying to update trial-patient info for patient {} while SMART has patient {}"
			.format(patient_id, patient.id))
		abort(401, "You are not authorized to update trial-patient-info for patient {}"
			.format(patient_id))
	
	# update data
	info = patient.info_for_trial(trial_id)
	if info is None:
		info = TrialPatientInfo(trial_id, patient_id)
	info.update_from_api(request.json)
	
	return jsonify(info.for_api())


# MARK: Enrolling

@app.route('/enroll')
def enroll():
	return render_template('enroll.html', {'title': "Randomize"})


# MARK: Static Files

@app.route('/static/<filename>')
def static_file(filename):
	return send_from_directory('static', filename)

@app.route('/templates/<filename>')
def template_file(filename):
	return send_from_directory('templates', filename)


# if starting directly, put into debug mode
if '__main__' == __name__:
	logging.basicConfig(level=logging.DEBUG)
	app.run(debug=True, port=8000)
