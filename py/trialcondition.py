#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import clinicaltrials.jsondocument.jsondocument as jsondocument
import trialmutation


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
		self.mutations = None
		super().__init__(None, "condition", json)
	
	def update_with(self, js):
		super().update_with(js)
		if self.mutations is not None:
			mutes = []
			for mute in self.mutations:
				mutes.append(trialmutation.TrialMutation(mute))
			self.mutations = mutes
	
	def as_json(self):
		js_dict = super().as_json()
		if self.mutations is not None:
			js_dict['mutations'] = [m.as_json() for m in self.mutations]
		return js_dict
	
	def for_api(self):
		js_dict = super().for_api()
		if self.mutations is not None:
			js_dict['mutations'] = [m.for_api() for m in self.mutations]
		return js_dict
	
	@classmethod
	def from_fhir(cls, fhir_cond):
		""" Fill properties from a FHIR condition instance.
		"""
		assert fhir_cond
		
		cond = cls()
		cond._id = fhir_cond.id
		
		if fhir_cond.code is not None and fhir_cond.code.coding is not None:
			for code in fhir_cond.code.coding:
				if 'http://snomed.info/sct' == code.system:
					cond.snomed = code.code
					cond.summary = code.display
					break
		cond.date_onset = fhir_cond.onsetDateTime.isostring if fhir_cond.onsetDateTime is not None else None
		cond.date_resolution = fhir_cond.abatementDateTime.isostring if fhir_cond.abatementDateTime is not None else None
		cond.status = fhir_cond.clinicalStatus
		if cond.summary is None:
			cond.summary = fhir_cond.text.div if fhir_cond.text is not None else None
		if cond.summary is not None:
			cond.summary = re.sub('<[^<]+?>', '', cond.summary)		# good enough
		cond.notes = fhir_cond.notes
		
		return cond
	
