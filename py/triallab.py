#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import isodate
import datetime
import clinicaltrials.jsondocument.jsondocument as jsondocument


class TrialLab(jsondocument.JSONDocument):
	""" Represents one lab test.
	"""
	
	def __init__(self, json=None):
		self.date = None
		self.loinc = None
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
		lab = cls()
		
		# determine date
		if fhir_observation.appliesDateTime is not None:
			lab.date = fhir_observation.appliesDateTime.date
		elif fhir_observation.appliesPeriod is not None:
			print('LAB PERIOD', fhir_observation.appliesPeriod)
		
		# find LOINC code
		if fhir_observation.name is not None and fhir_observation.name.coding is not None:
			for code in fhir_observation.name.coding:
				if 'http://loinc.org' == code.system:
					lab.loinc = code.code
					break
		
		# find value
		if fhir_observation.valueAttachment is not None:
			print('-- LAB VALUE (as valueAttachment)', fhir_observation.valueAttachment)
		elif fhir_observation.valueCodeableConcept is not None:
			print('-- LAB VALUE (as valueCodeableConcept)', fhir_observation.valueCodeableConcept)
		elif fhir_observation.valuePeriod is not None:
			print('-- LAB VALUE (as valuePeriod)', fhir_observation.valuePeriod)
		elif fhir_observation.valueQuantity is not None:
			lab.unit = fhir_observation.valueQuantity.units
			lab.value = fhir_observation.valueQuantity.value
		elif fhir_observation.valueRatio is not None:
			print('-- LAB VALUE (as valueRatio)', fhir_observation.valueRatio)
		elif fhir_observation.valueSampledData is not None:
			print('-- LAB VALUE (as valueSampledData)', fhir_observation.valueSampledData)
		elif fhir_observation.valueString is not None:
			print('-- LAB VALUE (as valueString)', fhir_observation.valueString)
		
		lab.reliability = fhir_observation.reliability
		lab.status = fhir_observation.status
		lab.summary = fhir_observation.text.div if fhir_observation is not None and fhir_observation.text is not None else None
		if lab.summary is not None:
			lab.summary = re.sub('<[^<]+?>', '', lab.summary)		# good enough
		
		return lab
	
	def update_with(self, js):
		super().update_with(js)
		if self.date is not None and not isinstance(self.date, datetime.date):
			self.date = isodate.parse_date(self.date)
	
	def as_json(self):
		js = super().as_json().copy()
		if self.date is not None:
			js['date'] = self.date.isoformat()
		return js

