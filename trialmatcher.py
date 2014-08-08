#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class TrialMatcher(object):
	""" An object to evaluate a list of trials against a given patient.
	"""
	
	def __init__(self, patient):
		self.patient = patient
	
	def match(self, trials):
		""" Match the provided trials against our patient.
		"""
		return trials
	
