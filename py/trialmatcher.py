#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import targetprofilerulematcher


class TrialMatchResult(object):
	""" Indicates the matching result between a patient and a trial.
	"""
	PASS = True
	UNSURE = None
	FAIL = False
	
	def __init__(self, trial, tests):
		self.trial = trial
		self.tests = tests
		self.trial_patient_info = None
	
	def add_patient_info(self, patient):
		assert self.trial
		self.trial_patient_info = patient.info_for_trial(self.trial.nct)
	
	def for_api(self):
		js = {
			'trial': self.trial.for_api(),
			'tests': [c.for_api() for c in self.tests],
		}
		if self.trial_patient_info is not None:
			js['patient_info'] = self.trial_patient_info.for_api()
		return js


class TrialMatchTest(object):
	""" One condition that a trial must pass in order to be suitable for a
	patient.
	"""
	
	@classmethod
	def passed(cls, test):
		return cls(TrialMatchResult.PASS, test)
	
	@classmethod
	def failed(cls, test, fail_property):
		return cls(TrialMatchResult.FAIL, test, fail_property)
	
	@classmethod
	def unsure(cls, test):
		return cls(TrialMatchResult.UNSURE, test)
	
	def __init__(self, result, test, fail_property=None):
		self.result = result
		self.test = test
		self.fail_property = fail_property
	
	def for_api(self):
		js = {
			'test': self.test,
		}
		if TrialMatchResult.PASS == self.result:
			js['status'] = 'pass'
		elif TrialMatchResult.FAIL == self.result:
			js['status'] = 'fail'
		if self.fail_property is not None:
			js['property'] = self.fail_property
		
		return js


class TrialMatcher(object):
	""" An object to evaluate a list of trials against a given patient.
	"""
	
	def match(self, patient, trials):
		""" Match the provided trials against a patient.
		
		:param patient: A TrialPatient instance to match for
		:param trials: A list of TargetTrial instances to match
		:returns: A list of `TrialMatchResult` results, one per trial.
		"""
		results = []
		if trials is not None and len(trials) > 0:
			for trial in trials:
				tests = self.test_against_trial(patient, trial)
				results.append(TrialMatchResult(trial, tests))
		
		return results
	
	def test_against_trial(self, patient, trial):
		""" Perform the actual matching logic. Subclasses should override this
		method and return a list of `TrialMatchTest` instances.
		
		:note: `patient` might be None
		:returns: A list of `TrialMatchTest` instances for the given trial,
			never None.
		"""
		return [TrialMatchTest.unsure(None)]


class TrialSerialMatcher(TrialMatcher):
	""" A trial matcher subclass that runs other concrete subclasses of
	`TrialMatcher` instances in series. Matching per trial stops as soon as a
	module fails a trial.
	"""
	
	def __init__(self):
		super().__init__()
		self.modules = []
	
	def test_against_trial(self, patient, trial):
		tests = []
		if len(self.modules) > 0:
			for module in self.modules:
				ext = module.test_against_trial(patient, trial)
				tests.extend(ext)
		return tests


class TrialGenderMatcher(TrialMatcher):
	""" Matches trials by patient gender.
	"""
	def test_against_trial(self, patient, trial):
		""" Retrieves the patient's gender string and the trial's eligibility.gender
		string. If the trial's string starts with an "f" and the patient's
		gender does not (and the same with "m") the trial is marked as a
		no-match.
		"""
		want = trial.eligibility.get('gender') if trial.eligibility else None
		if want is not None and len(want) > 0:
			if 'both' == want.lower():
				return [TrialMatchTest.passed("Trial accepts patients of any gender")]
			
			have = patient.gender
			
			if 'f' == want[0].lower():
				if have is not None and len(have) > 0:
					if 'f' != have[0].lower():
						return [TrialMatchTest.failed("Trial only accepts female patients", 'patient.gender')]
					return [TrialMatchTest.passed("Trial only accepts female patients")]
				return [TrialMatchTest.unsure("Trial only accepts female patients")]
			
			if 'm' == want[0].lower():
				if have is not None and len(have) > 0:
					if 'm' != have[0].lower():
						return [TrialMatchTest.failed("Trial only accepts male patients", 'patient.gender')]
					return [TrialMatchTest.passed("Trial only accepts male patients")]
				return [TrialMatchTest.unsure("Trial only accepts male patients")]
			
			logging.warning('Not sure which gender is expected by "{}", trial: {}'.format(want, trial.nct))
			return [TrialMatchTest.unsure("Trial requests unknown gender \"{}\"".format(want))]
		
		return []


class TrialAgeMatcher(TrialMatcher):
	""" Matches a trial by patient age.
	"""
	def test_against_trial(self, patient, trial):
		""" Retrieves the patient's age from CTG's "minimum_age" and
		"maximum_age" fields and compares it to the patient's age_years
		property.
		"""
		tests = []
		age = int(patient.age_years) if patient.age_years is not None else None
		elig = trial.eligibility
		minAge = self.sanitize_ctg_age(elig.get('minimum_age')) if elig is not None else None
		maxAge = self.sanitize_ctg_age(elig.get('maximum_age')) if elig is not None else None
		
		if minAge is not None:
			if age is not None:
				if age < minAge:
					tests.append(TrialMatchTest.failed("Must be at least {} years old, but is {}".format(minAge, age), 'patient.age_years'))
				else:
					tests.append(TrialMatchTest.passed("Must be at least {} years old".format(minAge)))
			else:
				tests.append(TrialMatchTest.unsure("Must be at least {} years old".format(minAge)))
				
		if maxAge is not None:
			if age is not None:
				if age > maxAge:
					tests.append(TrialMatchTest.failed("Must be no more than {} years old, but is {}".format(maxAge, age), 'patient.age_years'))
				else:
					tests.append(TrialMatchTest.passed("Must be no more than {} years old".format(maxAge)))
			else:
				tests.append(TrialMatchTest.unsure("Must be no more than {} years old".format(maxAge)))
		
		return tests
	
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
	def test_against_trial(self, patient, trial):
		""" If the trial has a profile, loops over the profile's rules and
		determines if the patient is disqualified or not.
		"""
		if trial.target_profile is None:
			logging.debug('No target profile for {}, cannot match'.format(trial.nct))
			return []
		
		# match over all rules
		tests = []
		for rule in trial.target_profile.rules:
			matcher = targetprofilerulematcher.TargetProfileRuleMatcher.get_matcher(rule)
			if matcher is None:
				logging.debug('{}: No target profile rule matcher is available for {} "{}"'.format(trial.nct, rule.for_type, rule.description))
				tests.append(TrialMatchTest.unsure("No rule matcher to test {} rule \"{}\"".format(rule.for_type, rule.description)))
			else:
				res, reason = matcher.test(patient)
				test = None
				if res is None:
					test = TrialMatchTest.unsure(reason or matcher.rule.description)
				elif res:
					test = TrialMatchTest.passed(matcher.rule.description)
				else:
					test = TrialMatchTest.failed(matcher.rule.description, reason)
				tests.append(test)
		
		return tests

