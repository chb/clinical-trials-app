#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

import codeable
import targetprofilediagnosisrulematcher


class TargetProfileRuleMatcher():
	""" Match one target profile rule.
	"""
	rule_type = None
	matcher_classes = {}
	
	@classmethod
	def register_rule(cls, klass):
		""" Register a TargetProfileRuleMatcher to match to rules of a given
		type.
		"""
		for_type = klass.rule_type if klass else None
		if not for_type:
			raise Exception('I need a class with a rule_type')
		if for_type in cls.matcher_classes:		# could check if class is different to fail gracefully on double-imports
			raise Exception('I have already registered {} for {}'.format(cls.matcher_classes[for_type]), for_type)
		cls.matcher_classes[for_type] = klass
	
	@classmethod
	def get_matcher(cls, for_rule):
		if for_rule is None:
			raise Exception('Must supply a rule in order to receive a matcher')
		if not for_rule.for_type:
			raise Exception('Invalid rule, does not have "for_type" set: {}'.format(for_rule))
		
		klass = cls.matcher_classes.get(for_rule.for_type)
		return klass(for_rule) if klass is not None else None
	
	def __init__(self, rule):
		self.rule = rule
	
	def test(self, patient):
		""" Performs the matching logic, returning a tuple with True describing
		the patient meeting the criteria, False not meeting and None that the
		test could not be performed.
		
		:returns: A tuple with (True|False|None, "fail reason")
		"""
		return (None, None)


class TargetProfileGenderRuleMatcher(TargetProfileRuleMatcher):
	rule_type = 'gender'
	
	def test(self, patient):
		include = self.rule.include
		match = patient.gender == self.rule.gender
		
		if include ^ match:
			return (False, 'patient.gender')
		return (True, None)


class TargetProfileAgeRuleMatcher(TargetProfileRuleMatcher):
	rule_type = 'age'
	
	def test(self, patient):
		age = patient.age_years
		if age is None:
			logging.debug('Patient doesn\'t have an age')
			return (None, None)
		
		include = self.rule.include
		match = False
		if self.rule.is_upper:
			if age < self.rule.threshold:
				match = True
		else:
			if age > self.rule.threshold:
				match = True
		if not match and self.rule.is_inclusive:
			if age == self.rule.threshold:
				match = True
		
		if include ^ match:
			return (False, 'patient.age')
		return (True, None)


class TargetProfileStateRuleMatcher(TargetProfileRuleMatcher):
	rule_type = 'state'
	
	def test(self, patient):
		include = self.rule.include
		match = False
		
		# check for pregnancy "condition" (SNOMED-CT 77386006)
		if 'pregnant' == self.rule.state:
			matcher = targetprofilediagnosisrulematcher.TargetProfileDiagnosisPregnancyRuleMatcher(self.rule)
			match = matcher.match_for(patient) is not None
		
		elif 'breastfeeding' == self.rule.state:
			return (None, "Testing whether the patient is breastfeeding is not yet supported")
		elif 'able to swallow oral medication' == self.rule.state:
			return (None, None)
		else:
			return (None, 'I cannot match to state "{}" for "{}"'
				.format(self.rule.state, self.rule.description))
		
		if include ^ match:
			return (False, 'patient.state.{}'.format(self.rule.state))
		return (True, None)


class TargetProfileRuleMatcherDiagnosis(TargetProfileRuleMatcher):
	""" Determines if a patient matches a diagnosis by looking at her
	documented conditions.
	"""
	rule_type = 'diagnosis'
	
	def test(self, patient):
		include = self.rule.include
		match = False
		match_desc = 'patient.conditions'
		
		# compare SNOMED-CT codes
		if 'snomedct' == self.rule.diagnosis.system:
			matcher = targetprofilediagnosisrulematcher.TargetProfileDiagnosisSNOMEDRuleMatcher(self.rule)
			matched = matcher.match_for(patient)
			if matched is not None:
				match = True
				match_desc = matched.term or match_desc
		else:
			return (None, 'I cannot match to diagnoses of type "{}" for "{}"'
				.format(self.rule.diagnosis.system, self.rule.description))
		
		# no documentation of the patient having the condition
		if match ^ include:
			return (False, match_desc)
		return (True, None)


class TargetProfileMedicationRuleMatcher(TargetProfileRuleMatcher):
	""" Determines if the patient is currently prescribed the medication(s)
	mentioned in the rule.
	"""
	rule_type = 'medication'
	
	def test(self, patient):
		include = self.rule.include
		match = False
		match_desc = 'patient.medications'
		
		# compare RxNorm meds
		if 'rxnorm' == self.rule.medication.system:
			rxnorm = codeable.Codeable('rxnorm', self.rule.medication.code)
			matched = rxnorm.find_any([c.rxnorm for c in patient.medications])
			if matched is not None:
				match = True
				match_desc = matched.description or match_desc
		else:
			return (None, 'I cannot match to medications of type "{}" for "{}"'
				.format(self.rule.medication.system, self.rule.description))
		
		# no documentation of the patient having the condition
		if match ^ include:
			return (False, match_desc)
		return (True, None)


class TargetProfileAllergyRuleMatcher(TargetProfileRuleMatcher):
	""" Determines if the patient has a documented allergy against the given
	substance.
	"""
	rule_type = 'allergy'
	
	def test(self, patient):
		include = self.rule.include
		match = False
		match_desc = 'patient.allergies'
		
		# compare NDF-RT allergies
		if 'ndfrt' == self.rule.allergy.system:
			ndfrt = codeable.Codeable('ndfrt', self.rule.allergy.code)
			matched = ndfrt.find_any([c.ndfrt for c in patient.allergies])
			if matched is not None:
				match = True
				match_desc = matched.description or match_desc
		else:
			return (None, 'I cannot match to allergies of type "{}" for "{}"'
				.format(self.rule.allergy.system, self.rule.description))
		
		# no documentation of the patient having the condition
		if match ^ include:
			return (False, match_desc)
		return (True, None)


class TargetProfileScoreRuleMatcher(TargetProfileRuleMatcher):
	rule_type = 'score'


class TargetProfileLabValueRuleMatcher(TargetProfileRuleMatcher):
	""" Determines if the patient has a documented laboratory value matching
	the rule.
	"""
	rule_type = 'labValue'
	
	def test(self, patient):
		include = self.rule.include
		match = None
		match_desc = None
		
		# compare LOINC lab values
		if 'lnc' == self.rule.lab.system:
			loinc = codeable.Codeable('lnc', self.rule.lab.code)
			use_latest = 'most recent' == self.rule.qualifier
			latest_matched = None
			
			for lab in patient.labs:
				matched = loinc.find(lab.loinc)
				if matched is not None:
					if lab.unit != self.rule.lab.unit:
						logging.warning('Different units in lab value rule matcher: {} {} vs. {} {}, skipping'
							.format(self.rule.threshold, self.rule.lab.unit, lab.value, lab.unit))
						continue
					
					# assume False if first lab value, reset to false if newer
					# lab value and we should only regard the most recent
					if match is None:
						match = False
					elif use_latest and latest_matched is not None and latest_matched < lab.date:
						match = False
						match_desc = None
					
					# test against bounds
					if self.rule.is_upper:
						if lab.value < self.rule.threshold:
							match = True
					else:
						if lab.value > self.rule.threshold:
							match = True
					if not match and self.rule.is_inclusive:
						if lab.value == self.rule.threshold:
							match = True
					
					if match:
						match_desc = matched.description
					
					latest_matched = lab.date
		else:
			return (None, 'I cannot match to lab values of type "{}" for "{}"'
				.format(self.rule.lab.system, self.rule.description))
		
		# if there is no lab value for the patient, we cannot test the rule
		if match is None:
			return (None, 'No suitable lab value to test "{}"'.format(self.rule.description))
		if match ^ include:
			return (False, match_desc or 'patient.labs')
		return (True, None)


TargetProfileRuleMatcher.register_rule(TargetProfileGenderRuleMatcher)
TargetProfileRuleMatcher.register_rule(TargetProfileAgeRuleMatcher)
TargetProfileRuleMatcher.register_rule(TargetProfileStateRuleMatcher)
TargetProfileRuleMatcher.register_rule(TargetProfileRuleMatcherDiagnosis)
TargetProfileRuleMatcher.register_rule(TargetProfileMedicationRuleMatcher)
TargetProfileRuleMatcher.register_rule(TargetProfileAllergyRuleMatcher)
TargetProfileRuleMatcher.register_rule(TargetProfileScoreRuleMatcher)
TargetProfileRuleMatcher.register_rule(TargetProfileLabValueRuleMatcher)

