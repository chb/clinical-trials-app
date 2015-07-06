#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import isodate
import datetime
import clinicaltrials.jsondocument.jsondocument as jsondocument


class TrialObservation(jsondocument.JSONDocument):
	""" Represents one observation.
	"""
	
	def __init__(self, json=None):
		self.date = None
		self.coding = None				# FHIR Coding array
		self.value = None				# numeric value
		self.unit = None				# the UCUM unit
		self.reliability = None
		self.status = None
		self.summary = None
		super().__init__(None, "lab", json)
	
	@classmethod
	def from_fhir(cls, fhir_observation):
		""" Fill properties from a FHIR Observation instance.
		"""
		assert fhir_observation
		obs = cls()
		obs._id = fhir_observation.id
		
		# determine date
		if fhir_observation.appliesDateTime is not None:
			obs.date = fhir_observation.appliesDateTime.date
		elif fhir_observation.appliesPeriod is not None:
			print('LAB PERIOD', fhir_observation.appliesPeriod)
		
		# find coding
		if fhir_observation.code is not None and fhir_observation.code.coding is not None:
			obs.coding = fhir_observation.code.coding
		
		# find value
		if fhir_observation.valueAttachment is not None:
			print('-- LAB VALUE (as valueAttachment)', fhir_observation.valueAttachment)
		elif fhir_observation.valueCodeableConcept is not None:
			print('-- LAB VALUE (as valueCodeableConcept)', fhir_observation.valueCodeableConcept)
		elif fhir_observation.valuePeriod is not None:
			print('-- LAB VALUE (as valuePeriod)', fhir_observation.valuePeriod)
		elif fhir_observation.valueQuantity is not None:
			obs.unit = fhir_observation.valueQuantity.units
			obs.value = fhir_observation.valueQuantity.value
		elif fhir_observation.valueRatio is not None:
			print('-- LAB VALUE (as valueRatio)', fhir_observation.valueRatio)
		elif fhir_observation.valueSampledData is not None:
			print('-- LAB VALUE (as valueSampledData)', fhir_observation.valueSampledData)
		elif fhir_observation.valueString is not None:
			print('-- LAB VALUE (as valueString)', fhir_observation.valueString)
		
		obs.reliability = fhir_observation.reliability
		obs.status = fhir_observation.status
		obs.summary = fhir_observation.text.div if fhir_observation is not None and fhir_observation.text is not None else None
		if obs.summary is not None:
			obs.summary = re.sub('<[^<]+?>', '', obs.summary)		# good enough
		
		return obs
	
	def update_with(self, js):
		super().update_with(js)
		if self.date is not None and not isinstance(self.date, datetime.date):
			self.date = isodate.parse_date(self.date)
	
	def as_json(self):
		js = super().as_json().copy()
		if self.date is not None:
			js['date'] = self.date.isoformat()
		return js

