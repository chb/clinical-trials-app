#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import smartclient.fhirclient.models.substance as substance
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
		allergy = cls()
		allergy._id = fhir_allergy.id
		
		# find NDF-RT code
		display = None
		if fhir_allergy.substance is not None and fhir_allergy.substance.coding is not None:
			for code in fhir_allergy.substance.coding:
				if 'http://rxnav.nlm.nih.gov/REST/Ndfrt' == code.system:
					allergy.ndfrt = code.code
					display = code.display
					break
		
		# TODO: use criticality
		allergy.status = fhir_allergy.status
		allergy.summary = fhir_allergy.text.div if fhir_allergy.text is not None else display
		if allergy.summary is not None:
			allergy.summary = re.sub('<[^<]+?>', '', allergy.summary)		# good enough
		
		return allergy
	
