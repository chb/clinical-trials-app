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
	def from_fhir(cls, fhir_prescription):
		""" Fill properties from a FHIR MedicationPrescription instance.
		"""
		assert fhir_prescription
		fhir_med = fhir_prescription.medication.resolved(medication.Medication)
		med = cls()
		med._id = fhir_prescription.id
		
		# find RxNorm code
		if fhir_med is not None and fhir_med.code is not None and fhir_med.code.coding is not None:
			for code in fhir_med.code.coding:
				if 'http://www.nlm.nih.gov/research/umls/rxnorm' == code.system:
					med.rxcui = code.code
					break
		
		med.status = fhir_prescription.status
		med.summary = fhir_med.text.div if fhir_med is not None and fhir_med.text is not None else None
		if med.summary is not None:
			med.summary = re.sub('<[^<]+?>', '', med.summary)		# good enough
		
		return med
	
