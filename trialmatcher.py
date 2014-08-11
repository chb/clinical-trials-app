#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging


class TrialMatchResult(object):
	""" Indicates the matching result between a patient and a trial.
	"""
	OK = True
	FAIL = False
	
	def __init__(self, trial, flag, reason=None):
		self.trial = trial
		self.ok = TrialMatchResult.OK if flag else TrialMatchResult.FAIL
		self.reason = reason


class TrialMatcher(object):
	""" An object to evaluate a list of trials against a given patient.
	"""
	
	def __init__(self, patient=None):
		self.patient = patient
	
	def match(self, trials):
		""" Match the provided trials against our patient.
		
		:returns: A list of `TrialMatchResult` results, one per trial.
		"""
		results = []
		if trials is not None and len(trials) > 0:
			for trial in trials:
				results.append(self.match_trial(trial))
		
		return results
	
	def match_trial(self, trial):
		""" Perform the actual matching logic. Subclasses should override this
		method and override `TrialMatchResult` suitably.
		
		:note: The `patient` property might be None
		:returns: A `TrialMatchResult` instance for the given trial.
		"""
		return TrialMatchResult(trial, True)


class TrialSerialMatcher(TrialMatcher):
	""" A trial matcher subclass that runs other concrete subclasses of
	`TrialMatcher` instances in series. Matching per trial stops as soon as a
	module fails a trial.
	"""
	
	def __init__(self, patient=None):
		super().__init__(patient)
		self.modules = []
	
	def match_trial(self, trial):
		if len(self.modules) > 0:
			for module in self.modules:
				module.patient = self.patient
				res = module.match_trial(trial)
				if not res.ok:
					return res
			return res
		return None


class TrialGenderMatcher(TrialMatcher):
	""" Matches trials by patient gender.
	"""
	def match_trial(self, trial):
		""" Retrieves the patient's gender string and the trial's eligibility.gender
		string. If the trial's string starts with an "f" and the patient's
		gender does not (and the same with "m") the trial is marked as a
		no-match.
		"""
		have = self.patient.gender
		want = trial.eligibility.get('gender')
		if want is not None and have is not None:
			if 'f' == want[0].lower() and 'f' != want[0].lower():
				return TrialMatchResult(trial, False, "Trial only accepts female patients")
			if 'm' == want[0].lower() and 'm' != want[0].lower():
				return TrialMatchResult(trial, False, "Trial only accepts male patients")
		else:
			logging.info("Not enough information to match by gender. Patient gender: {}, trial: {}".format(have, want))
		
		return TrialMatchResult(trial, True)


class TrialAgeMatcher(TrialMatcher):
	""" Matches a trial by patient age.
	"""
	def match_trial(self, trial):
		""" Retrieves the patient's age (...)
		"""
		age = int(self.patient.age_years) if self.patient.age_years is not None else None
		elig = trial.eligibility
		minAge = self.sanitize_ctg_age(elig.get('minimum_age')) if elig is not None else None
		maxAge = self.sanitize_ctg_age(elig.get('maximum_age')) if elig is not None else None
		if age is not None and (minAge is not None or maxAge is not None):
			if minAge is not None and age < minAge:
				return TrialMatchResult(trial, False, "Must be at least {} years old, but is {}".format(minAge, age))
			if maxAge is not None and age > maxAge:
				return TrialMatchResult(trial, False, "Must be no more than {} years old, but is {}".format(maxAge, age))
		else:
			logging.info("Not enough information to match by age. Patient: {}, min: {}, max: {}".format(age, minAge, maxAge))
		
		return TrialMatchResult(trial, True)
	
	def sanitize_ctg_age(self, age_string):
		""" Return the age in years, as integer, if possible.
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
	

