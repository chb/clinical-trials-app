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
		if klass is None or klass.tests is None:
			raise Exception('Can only announce an extra class that defines "tests"')
		cls.extras[klass.tests] = klass
	
	@classmethod
	def extra_for(cls, concept):
		if concept is None or concept.code is None:
			raise Exception('Need a SNOMED concept code to return an extra test')
		extra = cls.extras.get(concept.code)
		return extra() if extra is not None else None
	
	def match_for(self, patient):
		if self.rule is None or self.rule.diagnosis is None:
			raise Exception('Need a rule with a diagnosis, but have {}'.format(self.rule))
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


class TargetProfileDiagnosisSNOMEDMutationRuleMatcher(object):
	""" Superclass for testers that test SNOMED-coded diseases with mutations.
	"""
	tests = None
	parents = []
	hgnc = None
	hgnc_positive = True
	
	def __init__(self):
		self.specific = self.__class__.tests
		self.parents = self.__class__.parents
		self.hgnc = self.__class__.hgnc
		self.positive = self.__class__.hgnc_positive
	
	def matches(self, condition):
		""" Tests if:
		1. Is the given condition the same concept as the specific one?
		2. Is the given condition a child of the parent(s), and if so
		3. Is the given mutation present or absent as desired?
		"""
		cpt = snomed.SNOMEDConcept(condition.snomed)
		spec = snomed.SNOMEDConcept(self.specific)
		if cpt.code == spec.code or cpt.isa(spec.code):
			return True
		
		# is the condition a child of the parent(s) at all?
		gotit = False
		for parent in self.parents:
			bca = snomed.SNOMEDConcept(parent)
			if cpt.code == bca.code or cpt.isa(bca.code):
				gotit = True
				break
		if not gotit:
			return False
		
		# do we have the mutation?
		if condition.mutations is not None:
			for mute in condition.mutations:
				if self.hgnc == mute.hgnc:
					if mute.interpretation is not None:
						return self.positive == mute.interpretation.positive
					logging.warning('Have mutation {} but no interpretation, cannot determine positivity'
						.format(self.hgnc))
					break
		return not self.positive


class TargetProfileDiagnosisSNOMEDHer2PosRuleMatcher(TargetProfileDiagnosisSNOMEDMutationRuleMatcher):
	""" Special checks for Her 2 Neu Positive Ca (SNOMED 427685000). Breast-
	Ca is SNOMED 254838004.
	"""
	tests = '427685000'
	parents = ['254838004']
	hgnc = 'HGNC:3430'
	hgnc_positive = True

TargetProfileDiagnosisSNOMEDRuleMatcher.announce_extra(TargetProfileDiagnosisSNOMEDHer2PosRuleMatcher)


class TargetProfileDiagnosisSNOMEDHer2NegRuleMatcher(TargetProfileDiagnosisSNOMEDMutationRuleMatcher):
	""" Special checks for Her 2 Neu Negative Ca (SNOMED 431396003). Breast-
	Ca is SNOMED 254838004.
	"""
	tests = '431396003'
	parents = ['254838004']
	hgnc = 'HGNC:3430'
	hgnc_positive = False

TargetProfileDiagnosisSNOMEDRuleMatcher.announce_extra(TargetProfileDiagnosisSNOMEDHer2NegRuleMatcher)


class TargetProfileDiagnosisSNOMEDESRPosRuleMatcher(TargetProfileDiagnosisSNOMEDMutationRuleMatcher):
	""" Special checks for Estrogen receptor positive neoplasm (SNOMED
	416053008). Parent is "neoplastic disease", SNOMED 55342001.
	"""
	tests = '416053008'
	parents = ['55342001']
	hgnc = 'HGNC:3467'
	hgnc_positive = True

TargetProfileDiagnosisSNOMEDRuleMatcher.announce_extra(TargetProfileDiagnosisSNOMEDESRPosRuleMatcher)


class TargetProfileDiagnosisSNOMEDESRNegRuleMatcher(TargetProfileDiagnosisSNOMEDMutationRuleMatcher):
	""" Special checks for Estrogen receptor negative neoplasm (SNOMED
	441117001). Parent is "neoplastic disease", SNOMED 55342001.
	"""
	tests = '441117001'
	parents = ['55342001']
	hgnc = 'HGNC:3467'
	hgnc_positive = False

TargetProfileDiagnosisSNOMEDRuleMatcher.announce_extra(TargetProfileDiagnosisSNOMEDESRNegRuleMatcher)


class TargetProfileDiagnosisSNOMEDPGRPosRuleMatcher(TargetProfileDiagnosisSNOMEDMutationRuleMatcher):
	""" Special checks for Progesterone receptor positive neoplasm (SNOMED
	416561008). Parent is "neoplastic disease", SNOMED 55342001.
	"""
	tests = '416561008'
	parents = ['55342001']
	hgnc = 'HGNC:8910'
	hgnc_positive = True

TargetProfileDiagnosisSNOMEDRuleMatcher.announce_extra(TargetProfileDiagnosisSNOMEDPGRPosRuleMatcher)


class TargetProfileDiagnosisSNOMEDPGRNegRuleMatcher(TargetProfileDiagnosisSNOMEDMutationRuleMatcher):
	""" Special checks for Progesterone receptor negative neoplasm (SNOMED
	441118006). Parent is "neoplastic disease", SNOMED 55342001.
	"""
	tests = '441118006'
	parents = ['55342001']
	hgnc = 'HGNC:8910'
	hgnc_positive = False

TargetProfileDiagnosisSNOMEDRuleMatcher.announce_extra(TargetProfileDiagnosisSNOMEDPGRNegRuleMatcher)


class TargetProfileDiagnosisSNOMEDHormoneReceptorPosRuleMatcher(TargetProfileDiagnosisSNOMEDMutationRuleMatcher):
	""" Tests for positivity of estrogen and progesterone receptors.
	"""
	tests = '417742002'
	
	def __init__(self, snomed):
		super().__init__(snomed)
		self.esr = TargetProfileDiagnosisSNOMEDESRPosRuleMatcher(snomed)
		self.pgr = TargetProfileDiagnosisSNOMEDPGRPosRuleMatcher(snomed)
	
	def matches(self, condition):
		if not self.esr.matches(condition):
			return False
		return self.pgr.matches(condition)

TargetProfileDiagnosisSNOMEDRuleMatcher.announce_extra(TargetProfileDiagnosisSNOMEDHormoneReceptorPosRuleMatcher)


class TargetProfileDiagnosisSNOMEDHormoneReceptorNegRuleMatcher(TargetProfileDiagnosisSNOMEDMutationRuleMatcher):
	""" Tests for negativity of estrogen and progesterone receptors.
	"""
	tests = '438628005'
	
	def __init__(self, snomed):
		super().__init__(snomed)
		self.esr = TargetProfileDiagnosisSNOMEDESRNegRuleMatcher(snomed)
		self.pgr = TargetProfileDiagnosisSNOMEDPGRNegRuleMatcher(snomed)
	
	def matches(self, condition):
		if not self.esr.matches(condition):
			return False
		return self.pgr.matches(condition)

TargetProfileDiagnosisSNOMEDRuleMatcher.announce_extra(TargetProfileDiagnosisSNOMEDHormoneReceptorNegRuleMatcher)


class TargetProfileDiagnosisSNOMEDTripleNegRuleMatcher(TargetProfileDiagnosisSNOMEDMutationRuleMatcher):
	""" Tests for negativity of Her2, estrogen and progesterone receptors.
	"""
	tests = '706970001'
	
	def __init__(self, snomed):
		super().__init__(snomed)
		self.her = TargetProfileDiagnosisSNOMEDHer2NegRuleMatcher(snomed)
		self.esr = TargetProfileDiagnosisSNOMEDESRNegRuleMatcher(snomed)
		self.pgr = TargetProfileDiagnosisSNOMEDPGRNegRuleMatcher(snomed)
	
	def matches(self, condition):
		if not self.her.matches(condition):
			return False
		if not self.esr.matches(condition):
			return False
		if not self.pgr.matches(condition):
			return False
		return True


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

