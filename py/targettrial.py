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
	
	def __init__(self, nct=None, json_dict=None):
		super().__init__(nct, json_dict)
		self.score = json_dict.get('_meta', {}).get('score') if json_dict is not None else None
		self.target_profile = None
	
	def for_api(self):
		js = super().for_api()
		if self.score is not None:
			js['score'] = self.score
		return js

