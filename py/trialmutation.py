#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import trialobservation


class TrialMutation(trialobservation.TrialObservation):
	""" Represents a mutation extension for a Condition, should have a HGNC
	code and a SMART modifier-extension of "http://fhir-registry.smarthealthit.org/StructureDefinition/gene-expression-in".
	"""
	
	def __init__(self, json=None):
		self.hgnc = None
		self.reference = None
		super().__init__(json)
	
	@classmethod
	def is_mutation(cls, fhir_observation):
		""" Returns True if the observation has a hgnc code.
		"""
		if fhir_observation.code is not None and fhir_observation.code.coding is not None:
			for code in fhir_observation.code.coding:
				if 'http://www.genenames.org' == code.system:
					return True
		return False
	
	@classmethod
	def from_fhir(cls, fhir_observation):
		""" Fill properties from a FHIR Observation instance.
		"""
		mut = super().from_fhir(fhir_observation)
		
		if fhir_observation.modifierExtension is not None:
			for ext in fhir_observation.modifierExtension:
				if 'http://fhir-registry.smarthealthit.org/StructureDefinition/gene-expression-in' == ext.url:
					mut.reference = ext.valueReference.reference if ext.valueReference is not None else None
		
		# find HGNC code
		if mut.coding is not None:
			for code in mut.coding:
				if 'http://www.genenames.org' == code.system:
					mut.hgnc = code.code
			mut.coding = None
		return mut
