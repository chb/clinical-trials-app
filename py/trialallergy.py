#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import py.smartclient.fhirclient.models.substance as substance
import clinicaltrials.jsondocument.jsondocument as jsondocument


class TrialAllergy(jsondocument.JSONDocument):
	""" Represents a patient's allergy.
	"""
	
	def __init__(self, json=None):
		self.ndfrt = None
		self.status = None
		self.summary = None
		super().__init__(None, "allergy", json)
	
	@classmethod
	def from_fhir(cls, fhir_allergy):
		""" Fill properties from a FHIR AllergyIntolerance instance.
		"""
		assert fhir_allergy
		fhir_substance = fhir_allergy.substance.resolved(substance.Substance)
		allergy = cls()
		
		# find NDF-RT code
		if fhir_substance is not None and fhir_substance.type is not None and fhir_substance.type.coding is not None:
			for code in fhir_substance.type.coding:
				if 'http://rxnav.nlm.nih.gov/REST/Ndfrt' == code.system:
					allergy.ndfrt = code.code
					break
		
		# TODO: use criticality
		allergy.status = fhir_allergy.status
		allergy.summary = fhir_substance.text.div if fhir_substance is not None and fhir_substance.text is not None else None
		if allergy.summary is not None:
			allergy.summary = re.sub('<[^<]+?>', '', allergy.summary)		# good enough
		
		return allergy
	
