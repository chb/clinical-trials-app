#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import markdown
from dateutil.parser import *
from dateutil.relativedelta import *

import trialcondition
import trialmedication
import clinicaltrials.jsondocument.jsondocument as jsondocument
import smartclient.fhirclient.models.condition as condition
import smartclient.fhirclient.models.medicationprescription as medicationprescription


class TrialPatient(jsondocument.JSONDocument):
	""" A representation for a patient.
	
	Properties:
	
	- full_name: string
	- gender: string, "female" or "male"
	
	- birthday: ISO-8601 date string
	- deathdate: ISO-8601 date string
	- age_years: int
	- age_string: string
	
	- city: string
	- region: string
	- country: string
	- location = city, region: string
	
	- conditions: [TrialCondition]
	- medications: [TrialMedication]
	// - allergies: [TrialAllergy]
	
	- trial_info: [TrialPatientInfo] (loaded from db on init)
	"""
	
	def __init__(self, ident, json=None):
		super().__init__(ident, "patient", json)
		if json is None:
			self.gender = "female"
		if self.country is None:
			self.country = "United States"
		if self.location is None:
			self.update_location()
		
		if self.conditions is not None:
			cond = []
			for c in self.conditions:
				if isinstance(c, trialcondition.TrialCondition):
					cond.append(c)
				else:
					cond.append(trialcondition.TrialCondition(c))
			self.conditions = cond
		
		if self.medications is not None:
			meds = []
			for m in self.medications:
				if isinstance(m, trialmedication.TrialMedication):
					meds.append(m)
				else:
					meds.append(trialmedication.TrialMedication(m))
			self.medications = meds
		
		self.trial_info = TrialPatientInfo.find({'type': 'trial-patient-info', 'patient_id': ident})
	
	def __setattr__(self, name, value):
		""" Overridden to perform some value generation after setting certain
		properties.
		"""
		super().__setattr__(name, value)
		if 'birthday' == name:
			self.update_age_years()
		if 'country' == name or 'city' == name or 'region' == name:
			self.update_location()
	
	def for_api(self, stripped=False):
		js_dict = super().for_api().copy()
		if self.conditions is not None:
			js_dict['conditions'] = None if stripped else [c.for_api() for c in self.conditions]
		if self.medications is not None:
			js_dict['medications'] = None if stripped else [m.for_api() for m in self.medications]
		if self.trial_info is not None:
			js_dict['trial_info'] = [i.for_api() for i in self.trial_info]
		return js_dict
	
	@classmethod
	def load_from_fhir(cls, client):
		""" Instantiates a TrialPatient with data from a FHIR Patient resource,
		retrieved from a SMART client (fhirclient) instance.
		
		:param client: A handle to a `fhirclient` instance
		:returns: A TrialPatient instance, or None on error
		"""
		fpat = client.patient if client is not None else None
		if fpat is None:
			return None
		
		patient = cls(fpat._remote_id)
		patient.full_name = client.human_name(fpat.name[0] if fpat.name and len(fpat.name) > 0 else None)
		patient.gender = client.string_gender(fpat.gender)
		patient.birthday = fpat.birthDate.isostring
		
		if fpat.address is not None and len(fpat.address) > 0:
			address = fpat.address[0]
			for addr in fpat.address:
				if 'home' == addr.use:
					address = addr
					break
			patient.city = address.city
			patient.region = address.state
			patient.country = address.country
		
		# retrieve problem list
		cond_search = condition.Condition.where(struct={'subject': fpat._remote_id})
		patient.conditions = [trialcondition.TrialCondition.from_fhir(c) for c in cond_search.perform(fpat._server)]
		
		# retrieve meds
		med_search = medicationprescription.MedicationPrescription.where(struct={'subject': fpat._remote_id})
		patient.medications = [trialmedication.TrialMedication.from_fhir(m) for m in med_search.perform(fpat._server)]
		
		return patient
	
	
	# MARK: Trial Info
	
	def info_for_trial(self, trial_id):
		if self.trial_info is not None:
			for trialinfo in self.trial_info:
				if trialinfo.trial_id == trial_id:
					return trialinfo
		return None
	
	
	# MARK: Birthday & Age
	
	def age_delta(self):
		if self.birthday:
			try:
				birth = parse(self.birthday)
			except Exception as e:
				logging.error("Failed to parse birthday \"{}\": {}".format(self.birthday, e))
				return None
			
			now = datetime.datetime.now()
			if self.deathdate:
				try:
					now = parse(self.deathdate)
				except Exception as e:
					logging.error("Failed to parse deathdate \"{}\": {}".format(self.deathdate, e))
			
			return relativedelta(now, birth)
		return None
	
	@property
	def age_years(self):
		if self.__dict__.get('age_years') is None:
			self.update_age_years()
		return self.__dict__.get('age_years')
	
	@age_years.setter
	def age_years(self, years):
		self.__dict__['age_years'] = years
	
	def update_age_years(self):
		delta = self.age_delta()
		self.age_years = delta.years if delta is not None else None
	
	@property
	def age_string(self):
		delta = self.age_delta()
		if delta is not None:
			if 1 == delta.years:
				years = "{} year".format(delta.years)
			else:
				years = "{} years".format(delta.years)
			
			if delta.years < 3:
				if 1 == delta.months:
					return "{} {} month".format(years, delta.months)
				return "{} {} months".format(years, delta.months)
			return years
		return ''
	
	
	# MARK: Location
	
	def update_location(self):
		parts = []
		if self.city:
			parts.append(self.city)
		if self.region:
			parts.append(self.region)
		setattr(self, 'location', ', '.join(parts) if len(parts) > 0 else None)


class TrialPatientInfo(jsondocument.JSONDocument):
	""" Information linking a patient and a trial, stored by app users.
	"""
	def __init__(self, trial_id=None, patient_id=None, json=None):
		if json is not None:
			if trial_id is None:
				trial_id = json.get('trial_id')
			if patient_id is None:
				patient_id = json.get('patient_id')
		if not trial_id or not patient_id:
			raise Exception("Need both a trial- and patient-id, have trial: {}, patient: {}"
				.format(trial_id, patient_id))
		
		ident = '{}-{}'.format(trial_id, patient_id)
		super().__init__(ident, 'trial-patient-info', json)
		self.trial_id = trial_id
		self.patient_id = patient_id
	
	def for_api(self):
		js = {
			'trial_id': self.trial_id,
			'patient_id': self.patient_id,
		}
		if self.suggested:
			js['suggested'] = True
		if self.notes:
			js['notes'] = {
				'raw': self.notes,
				'html': markdown.markdown(self.notes),
			}
		
		return js
	
	def update_from_api(self, json):
		d = {}
		if 'suggested' in json:
			d['suggested'] = True if 'true' == json['suggested'] or 1 == int(json['suggested']) else False
		if 'notes' in json:
			d['notes'] = json['notes']
		self.update_with(d)
		self.store()

