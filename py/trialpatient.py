#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
sys.path.insert(0, os.path.dirname(__file__))

import logging
import datetime
from dateutil.parser import *
from dateutil.relativedelta import *

import trialcondition
import clinicaltrials.jsondocument.jsondocument as jsondocument
import smartclient.fhirclient.models.condition as condition


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
	"""
	
	def __init__(self, ident, json=None):
		super().__init__(ident, "patient", json)
		if json is None:
			self.gender = "female"
		if self.country is None:
			self.country = "United States"
		if self.location is None:
			self.update_location()
	
	def __setattr__(self, name, value):
		""" Overridden to perform some value generation after setting certain
		properties.
		"""
		super().__setattr__(name, value)
		if 'birthday' == name:
			self.update_age_years()
		if 'country' == name or 'city' == name or 'region' == name:
			self.update_location()
	
	
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
		
		return patient
	
	
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
	
