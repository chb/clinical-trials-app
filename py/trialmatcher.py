#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging


class TrialMatchResult(object):
	""" Indicates the matching result between a patient and a trial.
	"""
	OK = True
	FAIL = False
	
	def __init__(self, trial, flag, fail_reason=None, fail_property=None):
		self.trial = trial
		self.ok = TrialMatchResult.OK if flag else TrialMatchResult.FAIL
		self.fail_reason = fail_reason
		self.fail_property = fail_property
	
	def for_api(self):
		js = {
			'ok': self.ok,
			'trial': self.trial.for_api()
		}
		if self.fail_reason is not None:
			js['reason'] = self.fail_reason
		if self.fail_property is not None:
			js['property'] = self.fail_property
		
		return js


class TrialMatcher(object):
	""" An object to evaluate a list of trials against a given patient.
	"""
	
	def match(self, trials, patient):
		""" Match the provided trials against a patient.
		
		:param trial: A list of TargetTrial instances to match
		:param patient: A TrialPatient instance to match for
		:returns: A list of `TrialMatchResult` results, one per trial.
		"""
		results = []
		if trials is not None and len(trials) > 0:
			for trial in trials:
				results.append(self.match_trial(trial, patient))
		
		return results
	
	def match_trial(self, trial, patient):
		""" Perform the actual matching logic. Subclasses should override this
		method and return a suitable `TrialMatchResult`.
		
		:note: `patient` might be None
		:returns: A `TrialMatchResult` instance for the given trial.
		"""
		return TrialMatchResult(trial, True)


class TrialSerialMatcher(TrialMatcher):
	""" A trial matcher subclass that runs other concrete subclasses of
	`TrialMatcher` instances in series. Matching per trial stops as soon as a
	module fails a trial.
	"""
	
	def __init__(self):
		super().__init__()
		self.modules = []
	
	def match_trial(self, trial, patient):
		if len(self.modules) > 0:
			for module in self.modules:
				res = module.match_trial(trial, patient)
				if not res.ok:
					return res
			return res
		return None


class TrialGenderMatcher(TrialMatcher):
	""" Matches trials by patient gender.
	"""
	def match_trial(self, trial, patient):
		""" Retrieves the patient's gender string and the trial's eligibility.gender
		string. If the trial's string starts with an "f" and the patient's
		gender does not (and the same with "m") the trial is marked as a
		no-match.
		"""
		have = patient.gender
		want = trial.eligibility.get('gender') if trial.eligibility else None
		if want is not None and len(want) > 1 and have is not None and len(have) > 1:
			if 'f' == want[0].lower() and 'f' != have[0].lower():
				return TrialMatchResult(trial, False, "Trial only accepts female patients", 'patient.gender')
			if 'm' == want[0].lower() and 'm' != have[0].lower():
				return TrialMatchResult(trial, False, "Trial only accepts male patients", 'patient.gender')
		else:
			logging.debug('Not enough information to match {} by gender. Patient gender: {}, trial: {}'.format(trial.nct, have, want))
		
		return TrialMatchResult(trial, True)


class TrialAgeMatcher(TrialMatcher):
	""" Matches a trial by patient age.
	"""
	def match_trial(self, trial, patient):
		""" Retrieves the patient's age from CTG's "minimum_age" and
		"maximum_age" fields and compares it to the patient's age_years
		property.
		"""
		age = int(patient.age_years) if patient.age_years is not None else None
		elig = trial.eligibility
		minAge = self.sanitize_ctg_age(elig.get('minimum_age')) if elig is not None else None
		maxAge = self.sanitize_ctg_age(elig.get('maximum_age')) if elig is not None else None
		if age is not None and (minAge is not None or maxAge is not None):
			if minAge is not None and age < minAge:
				return TrialMatchResult(trial, False, "Must be at least {} years old, but is {}".format(minAge, age), 'patient.age_years')
			if maxAge is not None and age > maxAge:
				return TrialMatchResult(trial, False, "Must be no more than {} years old, but is {}".format(maxAge, age), 'patient.age_years')
		else:
			logging.debug('Not enough information to match {} by age. Patient: {}, min: {}, max: {}'.format(trial.nct, age, minAge, maxAge))
		
		return TrialMatchResult(trial, True)
	
	def sanitize_ctg_age(self, age_string):
		""" Return the age in years, as integer, if possible.
		
		:returns: An int for the patient's age in years or None
		"""
		if not age_string or 'N/A' == age_string:
			return None
		if ' Years' in age_string:
			return int(age_string.replace(' Years', ''))
		if ' Year' in age_string:
			return int(age_string.replace(' Year', ''))
		if ' Months' in age_string:
			return int(age_string.replace(' Months', '')) * 12
		if ' Month' in age_string:
			return int(age_string.replace(' Month', '')) * 12
		logging.error("Haven't seen this age string before: {}".format(age_string))
		return None


class TrialProfileMatcher(TrialMatcher):
	""" Matches a trial by its target profile.
	"""
	def match_trial(self, trial, patient):
		""" If the trial has a profile, loops over the profile's rules and
		determines if the patient is disqualified or not.
		"""
		if trial.target_profile is None:
			logging.debug('No target profile for {}, cannot match'.format(trial.nct))
			return TrialMatchResult(trial, True)
		
		# match over all rules
		for rule in trial.target_profile.rules:
			matcher = TargetProfileRuleMatcher.get_matcher(rule)
			if matcher is None:
				logging.debug('No target profile rule matcher is available for {} "{}"'.format(rule.for_type, rule.description))
			elif not matcher.matches(patient):
				return TrialMatchResult(trial, False, rule.description)
		
		return TrialMatchResult(trial, True)


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
		if klass is None:
			raise Exception('I need a class')
		for_type = klass.rule_type
		if not for_type:
			raise Exception('I need a class with a rule_type')
		if for_type in cls.matcher_classes:		# could check if class is different to fail gracefully on double-imports
			raise Exception('I have already registered {} for {}'.format(cls.matcher_classes[for_type]), for_type)
		cls.matcher_classes[for_type] = klass
	
	@classmethod
	def get_matcher(cls, for_rule):
		if for_rule is None or not for_rule.for_type:
			return None
		
		klass = cls.matcher_classes.get(for_rule.for_type)
		return klass(for_rule) if klass is not None else None
	
	def __init__(self, rule):
		self.rule = rule
	
	def matches(self, patient):
		""" Performs the matching logic, returning True if the patient meets
		the criteria and False otherwise, meaning she fails to qualify for the
		trial.
		"""
		return True
	

class TargetProfileGenderRuleMatcher(TargetProfileRuleMatcher):
	rule_type = 'gender'


class TargetProfileAgeRuleMatcher(TargetProfileRuleMatcher):
	rule_type = 'age'


class TargetProfileStateRuleMatcher(TargetProfileRuleMatcher):
	rule_type = 'state'


class TargetProfileDiagnosisRuleMatcher(TargetProfileRuleMatcher):
	""" Determines if a patient matches a diagnosis by looking at her
	documented conditions.
	"""
	rule_type = 'diagnosis'
	
	def matches(self, patient):
		include = self.rule.include
		
		# compare SNOMED-CT codes
		if 'snomed' == self.rule.diagnosis.system:
			code = self.rule.diagnosis.code
			for condition in patient.conditions:
				if code == condition.snomed:
					return include
		else:
			logging.debug('I cannot match to diagnoses of type "{}"'.format(self.rule.diagnosis.system))
		
		return False if include else True


class TargetProfileMedicationRuleMatcher(TargetProfileRuleMatcher):
	rule_type = 'medication'


class TargetProfileScoreRuleMatcher(TargetProfileRuleMatcher):
	rule_type = 'score'


TargetProfileRuleMatcher.register_rule(TargetProfileGenderRuleMatcher)
TargetProfileRuleMatcher.register_rule(TargetProfileAgeRuleMatcher)
TargetProfileRuleMatcher.register_rule(TargetProfileStateRuleMatcher)
TargetProfileRuleMatcher.register_rule(TargetProfileDiagnosisRuleMatcher)
TargetProfileRuleMatcher.register_rule(TargetProfileMedicationRuleMatcher)
TargetProfileRuleMatcher.register_rule(TargetProfileScoreRuleMatcher)
