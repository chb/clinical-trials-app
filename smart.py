#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from endpoints import ENDPOINTS
from rdflib.graph import Graph
from smart_client_python.client import SMARTClient


def client(session):
	if session is None:
		logging.info("There is no session")
		return None
	
	# configure SMART client
	api_base = session.get('api_base')
	if not api_base:
		logging.info("No api_base is set")
		return None
	
	# we're not using SMART
	if 'none' == api_base:
		return None
	
	# find server credentials and store in session
	cons_key = session.get('consumer_key')
	cons_sec = session.get('consumer_secret')
	if not cons_key or not cons_sec:
		server = None
		for ep in ENDPOINTS:
			if ep.get('url') == api_base:
				server = ep
				break
		
		if server is None:
			logging.error("There is no server with base URI %s" % api_base)
			return None
		
		session['consumer_key'] = cons_key = server.get('consumer_key')
		session['consumer_secret'] = cons_sec = server.get('consumer_secret')
	
	# init client
	config = {
		'consumer_key': cons_key,
		'consumer_secret': cons_sec
	}
	
	try:
		smart = SMARTClient(os.environ.get('USE_APP_ID'), api_base, config)
		smart.record_id = sess.get('record_id')
	except Exception as e:
		logging.warning("Failed to instantiate SMART client: %s" % e)
		smart = None
	
	# if we have tokens, update the client
	token = sess.get('token')
	if token is not None:
		smart.update_token(token)
	
	return smart


def endpoints():
	""" Return all configured endpoints.
	"""
	available = []
	for srvr in smart.ENDPOINTS:
		available.append(srvr)
	
	return available


# ------------------------------------------------------------------------------

def fetch_patient_data(smart_client, patient):
	""" Fills the patient object from SMART data.
	"""
	retrieve_demographics(smart_client, patient)
	patient.problems = retrieve_problems(smart_client)
	patient.didFetch()


def retrieve_demographics(smart_client, patient, smart_05=False):
	demo = {}
	demo_ld = None
	
	# SMART 0.5 fallback (the JS client writes demographics to session storage)
	if smart_05:
		demo_rdf = session.get('demographics') if session is not None else None
		
		# use session data (parse RDF, convert to json-ld-serialization, load json... :P)
		try:
			# hack v0.5 format to be similar to v0.6 format, part 1
			demo_rdf = demo_rdf.replace('xmlns:v=', 'xmlns:vcard=')
			demo_rdf = demo_rdf.replace('<v:', '<vcard:')
			demo_rdf = demo_rdf.replace('</v:', '</vcard:')
			graph = Graph().parse(data=demo_rdf)
		except Exception as e:
			logging.error("Failed to parse demographics: %s" % e)
		
		# hack v0.5 format to be similar to v0.6 format, part 2
		demo_ld = {u"@graph": [json.loads(graph.serialize(format='json-ld'))]}
	
	# SMART 0.6+
	elif smart_client is not None:
		ret = smart_client.get_demographics()
		if 200 == int(ret.response.status):
			demo_ld = json.loads(ret.graph.serialize(format='json-ld')) if ret.graph is not None else None
		else:
			logging.error("Failed to get demographics: %d" % int(ret.response.status))
	
	# extract interesting pieces
	if demo_ld is not None:
		for gr in demo_ld.get("@graph", []):
			if "sp:Demographics" == gr.get("@type"):
				demo = gr
				break
	
	# apply
	n = demo.get('vcard:n') or {}
	fn = "Unknown"
	if 'vcard:family-name' in n:
		fn = n['vcard:family-name']
	if 'vcard:given-name' in n:
		gn = n['vcard:given-name']
		fn = gn if 0 == len(fn) else "{}, {}".format(fn, gn)
	patient.full_name = fn
	
	patient.birthday = demo.get('vcard:bday')
	patient.deathdate = demo.get('vcard:deathdate')
	patient.ethnicity = demo.get('sp:ethnicity')
	
	adr = demo.get('vcard:adr') or {}
	if 'vcard:locality' in adr:
		patient.city = adr['vcard:locality']
	if 'vcard:region' in adr:
		patient.region = adr['vcard:region']
	if 'vcard:country' in adr:
		patient.country = adr['vcard:country']
	
	
	
	return d

def retrieve_problems(smart_client, smart_05=False):
	""" Returns the current patient's problems as JSON extracted from JSON-LD.
	"""
	prob_ld = None
	
	# SMART 0.5 fallback (the JS client writes problem data to session storage)
	if smart_05:
		prob_rdf = session.get('problems') if session is not None else None
		
		# use session data (parse RDF, convert to json-ld-serialization, load json... :P)
		try:
			graph = Graph().parse(data=prob_rdf)
		except Exception as e:
			logging.error("Failed to parse problems: %s\n%s" % (e, prob_rdf))
			return {'problems': []}
		
		prob_ld = json.loads(graph.serialize(format='json-ld'))
	
	# SMART 0.6+
	elif smart_client is not None:
		ret = smart_client.get_problems()
		if 200 == int(ret.response.status):
			prob_ld = json.loads(ret.graph.serialize(format='json-ld')) if ret.graph is not None else None
		else:
			logging.error("Failed to get problems: %d" % int(ret.response.status))
	
	# pick out the individual problems
	problems = []
	if prob_ld is not None:
		for gr in prob_ld.get("@graph", []):
			if "sp:Problem" == gr.get("@type"):
				problems.append(gr)
	
	return problems


def test_record_token():
	""" Tries to fetch demographics with the given token and returns a bool
	whether thas was successful. """
	
	smart = SMART()
	if smart is None:
		return False
	
	# try to get demographics
	try:
		ret = smart.get_demographics()
		
		# did work!
		if 200 == int(ret.response.status):
			return True
	except Exception as e:
		pass
	
	return False

