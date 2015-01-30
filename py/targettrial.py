#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import markdown

import clinicaltrials.trial as clintrial
import clinicaltrials.lillyserver as lillysrv
import clinicaltrials.jsondocument.jsondocument as jsondoc


class TargetTrial(clintrial.Trial):
	""" Extending `Trial` to support target profiles.
	"""
	
	def __init__(self, nct=None, json_dict=None):
		super().__init__(nct, json_dict)
		self.score = json_dict.get('_meta', {}).get('score') if json_dict is not None else None
		self.target_profile = None
		trial_info = TargetTrialInfo.find({'_id': self.trial_info_id})
		if trial_info is not None and len(trial_info) > 0:
			self.trial_info = trial_info[0]
			self.trial_info.load()
	
	def as_json(self):
		js = super().as_json().copy()
		if self.trial_info is not None:
			del js['trial_info']
		return js
	
	def for_api(self):
		js = super().for_api()
		if self.trial_info is not None:
			js['info'] = self.trial_info.for_api()
		return js
	
	
	# MARK: Local Trial Info
	
	@property
	def trial_info_id(self):
		return 'info-'+self._id
	
	def set_local_info(self, json_dict):
		if json_dict:
			if self.trial_info is None:
				self.trial_info = TargetTrialInfo(self.trial_info_id)
			self.trial_info.update_with(json_dict)
			self.trial_info.store()


class TargetTrialInfo(jsondoc.JSONDocument):
	def __init__(self, ident, json=None):
		super().__init__(ident, 'trial-info', json)
		if self.notes and str != type(self.notes):
			self.notes = None
	
	def for_api(self):
		js = super().for_api()
		if self.notes:
			js['notes'] = {
				'raw': self.notes,
				'html': markdown.markdown(self.notes),
			}
		return js
