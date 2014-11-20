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
	
	def __init__(self, nct=None, json_dict=None):
		super().__init__(nct, json_dict)
		self.score = json_dict.get('_meta', {}).get('score') if json_dict is not None else None
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
	
	def for_api(self):
		js = super().for_api()
		if self.score is not None:
			js['score'] = self.score
		return js
