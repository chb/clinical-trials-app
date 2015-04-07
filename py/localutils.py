#!/usr/bin/env python3

import io
import os
import json
import logging

import targettrial
import targetprofile
import clinicaltrials.trialserver as trialserver


class LocalTrialServer(trialserver.TrialServer):
	""" Only returns trials for the local target profiles.
	"""
	trial_cache = None
	profile_cache = None
	
	def __init__(self, directory, trialreach_server):
		super().__init__(None)
		assert os.path.isdir(directory)
		self.directory = directory
		self.trialreach_server = trialreach_server
	
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
			elif self.trialreach_server is not None:
				trial = self.trialreach_server.get_trial(nct, trial_class)
				if cache_t is not None:
					cache_t.store(trial.nct, trial.as_json())
			else:
				logging.error("I do NOT have a handle to a TrialReach server, unable to query for trials")
				continue
			
			# check cache for target profile data
			if trial.target_profile is None and cache_p is not None:
				prof_json = cache_p.retrieve(trial.nct)
				if prof_json is not None:
					trial.target_profile = targetprofile.TargetProfile(prof_json)
			# else use trial.retrieve_profile once we use TrialReach trials
			
			trials.append(trial)
		
		return trials, None, None


class LocalCache(object):
	""" Handles caching files by id.
	"""
	def __init__(self, directory):
		directory = os.path.abspath(directory)
		if not os.path.exists(directory):
			os.makedirs(directory, exist_ok=True)
		
		self.cache_dir = directory
		self.can_write = True
		self.timeout = None				# number, in seconds
	
	def cache_filename(self, file_id, **kwargs):
		""" Override in subclasses to generate nicer filenames. """
		return file_id
	
	def cache_path(self, file_id, **kwargs):
		assert file_id is not None
		# TODO: sanitize filename
		filename = self.cache_filename(file_id, **kwargs)
		return os.path.join(self.cache_dir, filename), filename
	
	def existing_cache_path(self, file_id, **kwargs):
		path, fname = self.cache_path(file_id, **kwargs)
		if path is None or not os.path.exists(path):
			return None, None
		
		# remove if older than timeout
		if self.timeout is not None:
			mtime = os.path.getmtime(path)
			if time.time() - mtime > self.timeout:
				os.remove(path)
				return None, None
		
		return path, fname
	
	def retrieve(self, file_id, **kwargs):
		path, fname = self.existing_cache_path(file_id, **kwargs)
		if path is not None:
			return self.retrieve_from(path, **kwargs)
	
	def retrieve_from(self, file_id, **kwargs):
		""" Must be overridden by subclasses. """
		return None
	
	def store_path(self, file_id, data, **kwargs):
		if not self.can_write or data is None:
			return None, None
		return self.cache_path(file_id, **kwargs)
		
	def store(self, file_id, data, **kwargs):
		path, fname = self.store_path(file_id, data, **kwargs)
		if path is None:
			return None, None
		
		self.do_store(path, data, **kwargs)
		return path, fname
	
	def do_store(self, data, path, **kwargs):
		""" Must be overridden by subclasses. """
		pass


class LocalJSONCache(LocalCache):
	""" Handles caching JSON files by id.
	"""
	def cache_filename(self, file_id, **kwargs):
		return file_id + '.json'
	
	def retrieve_from(self, path, **kwargs):
		#print('<--', path)
		with io.open(path, 'r', encoding='UTF-8') as handle:
			return json.load(handle)
	
	def do_store(self, path, data, **kwargs):
		#print('-->', path)
		with io.open(path, 'w', encoding='UTF-8') as handle:
			if dict == type(data):
				json.dump(data, handle)
			else:
				handle.write(data)

class LocalImageCache(LocalCache):
	""" Handles caching JSON files by id.
	"""
	def cache_filename(self, file_id, **kwargs):
		if 'contentType' in kwargs:
			if 'image/jpeg' == kwargs['contentType'] or 'image/jpg' == kwargs['contentType']:
				return file_id + '.jpg'
			if 'image/png' == kwargs['contentType']:
				return file_id + '.png'
		return file_id + '.data'
	
	def retrieve_from(self, path, **kwargs):
		#print('<--', path)
		with open(path, 'rb') as handle:
			return handle.read()
	
	def do_store(self, path, data, **kwargs):
		#print('-->', path)
		with open(path, 'wb') as handle:
			handle.write(data)

