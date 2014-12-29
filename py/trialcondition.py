#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import clinicaltrials.jsondocument.jsondocument as jsondocument


class TrialCondition(jsondocument.JSONDocument):
	""" Represents one of a patient's conditions.
	"""
	
	def __init__(self, json=None):
		self.snomed = None
		self.date_onset = None
		self.date_resolution = None
		self.status = None
		self.summary = None
		self.notes = None
		super().__init__(None, "condition", json)
	
	@classmethod
	def from_fhir(cls, fhir_cond):
		""" Fill properties from a FHIR condition instance.
		"""
		assert fhir_cond
		
		cond = cls()
		if fhir_cond.code is not None and fhir_cond.code.coding is not None:
			for code in fhir_cond.code.coding:
				if 'http://snomed.info/sct' == code.system:
					cond.snomed = code.code
					break
		cond.date_onset = fhir_cond.onsetDate.isostring if fhir_cond.onsetDate is not None else None
		cond.date_resolution = fhir_cond.abatementDate.isostring if fhir_cond.abatementDate is not None else None
		cond.status = fhir_cond.status
		cond.summary = fhir_cond.text.div if fhir_cond.text is not None else None
		if cond.summary is not None:
			cond.summary = re.sub('<[^<]+?>', '', cond.summary)		# good enough
		cond.notes = fhir_cond.notes
		
		return cond
	
