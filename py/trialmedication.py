#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import smartclient.fhirclient.models.medication as medication
import clinicaltrials.jsondocument.jsondocument as jsondocument


class TrialMedication(jsondocument.JSONDocument):
	""" Represents a patient's prescribed medication.
	"""
	
	def __init__(self, json=None):
		self.rxcui = None
		self.status = None
		self.summary = None
		super().__init__(None, "medication", json)
	
	@classmethod
	def from_fhir(cls, fhir_order):
		""" Fill properties from a FHIR MedicationOrder instance.
		"""
		assert fhir_order
		med = cls()
		med._id = fhir_order.id
		
		# extract coding
		coding = None
		if fhir_order.medicationReference:
			print("TODO: test")
			fhir_med = fhir_order.medicationReference.resolved(medication.Medication)
			if fhir_med is not None and fhir_med.code is not None:
				coding = fhir_med.code.coding
			med.summary = fhir_med.text.div if fhir_med is not None and fhir_med.text is not None else None
		elif fhir_order.medicationCodeableConcept:
			coding = fhir_order.medicationCodeableConcept.coding
		
		# find RxNorm code
		if coding is not None:
			for code in coding:
				if 'http://www.nlm.nih.gov/research/umls/rxnorm' == code.system:
					med.rxcui = code.code
					break
		
		med.status = fhir_order.status
		med.summary = fhir_order.text.div if fhir_order.text is not None else None
		if med.summary is not None:
			med.summary = re.sub('<[^<]+?>', '', med.summary)		# good enough
		
		return med
	
