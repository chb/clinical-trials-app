#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import umls.snomed as snomed



class TargetProfileDiagnosisRuleMatcher(object):
	""" Abstract superclass to handle diagnosis matching.
	"""
	def __init__(self, rule):
		self.rule = rule
	
	def match_for(self, patient):
		raise Exception('Abstract class use')


class TargetProfileDiagnosisSNOMEDRuleMatcher(TargetProfileDiagnosisRuleMatcher):
	""" Handle SNOMED Matching.
	"""
	extras = {}
	
	@classmethod
	def announce_extra(cls, klass):
		if klass is None or klass.tests is None or not isinstance(klass.tests, list):
			raise Exception('Can only announce an extra class that defines "tests" as a list')
		for tests in klass.tests:
			cls.extras[tests] = klass
	
	@classmethod
	def extra_for(cls, concept):
		if concept is None or concept.code is None:
			raise Exception('Need a SNOMED concept code to return an extra test')
		extra = cls.extras.get(concept.code)
		if extra is not None:
			return extra(concept)
		return None
	
	def match_for(self, patient):
		if self.rule is None or self.rule.diagnosis is None:
			raise Exception('Need a rule with a diagnosis, but have {}'.formate(self.rule))
		if 'snomedct' != self.rule.diagnosis.system:
			raise Exception('Can only be used for SNOMED diagnoses, but have {}'.format(self.rule.diagnosis.system))
		
		test = snomed.SNOMEDConcept(self.rule.diagnosis.code)
		extra = self.__class__.extra_for(test)
		
		for condition in patient.conditions:
			cpt = snomed.SNOMEDConcept(condition.snomed)
			if extra is not None:
				if extra.matches(condition):
					return cpt
			elif cpt.code == test.code or cpt.isa(test.code):
				return cpt
		return None


class TargetProfileDiagnosisSNOMEDHer2PosRuleMatcher(object):
	""" Special checks for Her 2 Neu Positive Ca (SNOMED 427685000). Breast-
	Ca is SNOMED 254838004.
	"""
	tests = ['427685000']
	
	def __init__(self, snomed):
		self.snomed = snomed
	
	def matches(self, condition):
		if condition.mutations is not None:
			for mute in condition.mutations:
				if 'HGNC:3430' == mute.hgnc and mute.interpretation is not None and not mute.interpretation.positive:
					return False
		cpt = snomed.SNOMEDConcept(condition.snomed)
		bca = snomed.SNOMEDConcept('254838004')
		return cpt.code == bca.code or cpt.isa(bca.code)

TargetProfileDiagnosisSNOMEDRuleMatcher.announce_extra(TargetProfileDiagnosisSNOMEDHer2PosRuleMatcher)


class TargetProfileDiagnosisSNOMEDHer2NegRuleMatcher(object):
	""" Special checks for Her 2 Neu Negative Ca (SNOMED 431396003). Breast-
	Ca is SNOMED 254838004.
	"""
	tests = ['431396003']
	
	def __init__(self, snomed):
		self.snomed = snomed
	
	def matches(self, condition):
		if condition.mutations is not None:
			for mute in condition.mutations:
				if 'HGNC:3430' == mute.hgnc and mute.interpretation is not None and mute.interpretation.positive:
					return False
		cpt = snomed.SNOMEDConcept(condition.snomed)
		bca = snomed.SNOMEDConcept('254838004')
		return cpt.code == bca.code or cpt.isa(bca.code)

TargetProfileDiagnosisSNOMEDRuleMatcher.announce_extra(TargetProfileDiagnosisSNOMEDHer2NegRuleMatcher)


class TargetProfileDiagnosisPregnancyRuleMatcher(TargetProfileDiagnosisRuleMatcher):
	def match_for(self, patient):
		for c in patient.conditions:
			if c.date_onset is not None:
				pass		# TODO: compare dates
			if c.date_resolution is not None:
				pass		# TODO: check if "resolved"
			
			cpt = snomed.SNOMEDConcept(c.snomed)
			if cpt.code == '77386006' or cpt.isa('77386006'):
				return cpt
		return None

