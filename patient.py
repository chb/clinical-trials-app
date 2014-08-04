#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
from dateutil.parser import *
from dateutil.relativedelta import *

from ClinicalTrials.jsondocument.jsondocument import JSONDocument


class Patient(JSONDocument):
	""" A representation for a patient.
	
	Properties:
	
	- full_name [string]
	- gender [string, "female" or "male"]
	
	- birthday
	- deathdate
	- age_years [int]
	- age_string [string]
	
	- city [string]
	- region [string]
	- country [string]
	- location = city, region, country [string]
	"""
	
	def __init__(self, ident, json=None):
		super().__init__(ident, "patient", json)
		if json is None:
			self.gender = "female"
	
	def didFetch(self):
		self.did_fetch = True
	
	
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
		if self.__dict__['age_years'] is None:
			delta = self.age_delta()
			self.age_years = delta.years if delta is not None else None
		return self.__dict__['age_years']
	
	@age_years.setter
	def age_years(self, years):
		self.__dict__['age_years'] = years
	
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
	
	@property
	def location(self):
		if self.__dict__['location'] is None:
			parts = []
			if self.city:
				parts.append(self.city)
			if self.region:
				parts.append(self.region)
			if self.country:
				parts.append(self.country)
			self.__dict__['location'] = ', '.join(parts) if len(parts) > 0 else ''
		return self.__dict__['location']
	
	@location.setter
	def location(self, value):
		self.__dict__['location'] = value
	
