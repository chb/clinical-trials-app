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
	
	@property
	def json(self):
		js = {
			'ok': self.ok,
			'trial': self.trial.json
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
		
		:param trial: A list of Trial instances to match
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
		want = trial.eligibility.get('gender')
		if want is not None and len(want) > 1 and have is not None and len(have) > 1:
			if 'f' == want[0].lower() and 'f' != have[0].lower():
				return TrialMatchResult(trial, False, "Trial only accepts female patients", 'patient.gender')
			if 'm' == want[0].lower() and 'm' != have[0].lower():
				return TrialMatchResult(trial, False, "Trial only accepts male patients", 'patient.gender')
		else:
			logging.info("Not enough information to match by gender. Patient gender: {}, trial: {}".format(have, want))
		
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
			logging.info("Not enough information to match by age. Patient: {}, min: {}, max: {}".format(age, minAge, maxAge))
		
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
	

