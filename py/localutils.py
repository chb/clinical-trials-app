#!/usr/bin/env python3

import io
import os
import json

import targettrial
import targetprofile
import clinicaltrials.trialserver as trialserver


class LocalTrialServer(trialserver.TrialServer):
	""" Only returns trials for the local target profiles.
	"""
	trial_cache = None
	profile_cache = None
	
	def __init__(self, directory, lilly_server):
		super().__init__(None)
		assert os.path.isdir(directory)
		self.directory = directory
		self.lilly_server = lilly_server
	
	def find(self, params=None, request=None, trial_class=None):
		if trial_class is None:
			trial_class = targettrial.TargetTrial
		
		cache_t = self.__class__.trial_cache
		cache_p = self.__class__.profile_cache
		trials = []
		for item in os.listdir(self.directory):
			nct = item.replace('.json', '')
			
			# get trial from either the cache or the server
			trial_json = cache_t.retrieve(nct) if cache_t is not None else None
			if trial_json is not None:
				trial = trial_class(nct, trial_json)
			else:
				trial = self.lilly_server.get_trial(nct, trial_class)
				if cache_t is not None:
					cache_t.store(trial.nct, trial.as_json())
			
			# check cache for target profile data
			if trial.target_profile is None and cache_p is not None:
				prof_json = cache_p.retrieve(trial.nct)
				if prof_json is not None:
					trial.target_profile = targetprofile.TargetProfile(prof_json)
			# else use trial.retrieve_profile once we use LillyTrial trials
			
			trials.append(trial)
		
		return trials, None, None


class LocalJSONCache(object):
	""" Handles caching JSON files by id.
	"""
	def __init__(self, directory):
		directory = os.path.abspath(directory)
		if not os.path.exists(directory):
			os.makedirs(directory, exist_ok=True)
		
		self.cache_dir = directory
		self.can_write = True
		self.timeout = None				# number, in seconds
	
	def cache_filename(self, file_id):
		assert file_id is not None
		# TODO: sanitize filename
		return os.path.join(self.cache_dir, file_id + '.json')
	
	def retrieve(self, file_id):
		pth = self.cache_filename(file_id)
		if pth is None or not os.path.exists(pth):
			return None
		
		# remove if older than timeout
		if self.timeout is not None:
			mtime = os.path.getmtime(pth)
			if time.time() - mtime > self.timeout:
				os.remove(pth)
				return None
		
		#print('<--', pth)
		with io.open(pth, 'r', encoding='UTF-8') as handle:
			return json.load(handle)
	
	def store(self, file_id, js):
		if not self.can_write or js is None:
			return
		
		pth = self.cache_filename(file_id)
		if pth is not None:
			#print('-->', pth)
			with io.open(pth, 'w', encoding='UTF-8') as handle:
				if dict == type(js):
					json.dump(js, handle)
				else:
					handle.write(js)

