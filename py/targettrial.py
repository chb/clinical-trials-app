#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

import clinicaltrials.trial as clintrial
import clinicaltrials.lillyserver as lillysrv
import targetprofiles.model.targetprofile as tarprof


class TargetTrial(clintrial.Trial):
	""" Extending `Trial` to support target profiles.
	"""
	cache = None
	
	def __init__(self, nct=None, json=None):
		super().__init__(nct, json)
		self.find_target_profile()
	
	def find_target_profile(self):
		""" Finds and parses the Target Profile for the receiver, if one can
		be found.
		"""
		if self.target_profile is None:
			if self.cache is None:
				
				# HARD CODED PATH to the Sarah Cannon TPs
				directory = os.path.join(os.path.dirname(__file__), '..', 'sarah-cannon-pilot', 'breast-target-profiles', 'JSON')
				self.__class__.cache = lillysrv.LillyTargetProfileCache(directory)
			
			profile = self.cache.retrieve(self)
			if profile is not None:
				self.target_profile = tarprof.TargetProfile(profile)
	
