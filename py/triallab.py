#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import trialobservation


class TrialLab(trialobservation.TrialObservation):
	""" Represents one lab test.
	"""
	
	def __init__(self, json=None):
		self.loinc = None
		super().__init__(json)
	
	@classmethod
	def is_lab(cls, fhir_observation):
		""" Returns True if the observation has a LOINC code.
		"""
		if fhir_observation.code is not None and fhir_observation.code.coding is not None:
			for code in fhir_observation.code.coding:
				if 'http://loinc.org' == code.system:
					return True
		return False
	
	@classmethod
	def from_fhir(cls, fhir_observation):
		""" Fill properties from a FHIR Observation instance.
		"""
		lab = super().from_fhir(fhir_observation)
		
		# find LOINC code
		if lab.coding is not None:
			for code in lab.coding:
				if 'http://loinc.org' == code.system:
					lab.loinc = code.code
			lab.coding = None
		return lab
