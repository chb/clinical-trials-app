#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging


class TrialFinder(object):
	""" Find trials on a server.
	"""
	
	def __init__(self, server):
		assert server
		self.server = server
		
		self.fetch_all = True
		self.recruiting_only = True
		self.limit_location = 'Sarah Cannon'
	
	def find(self, params):
		""" Find trials with the given parameters. Will return at max 1000
		trials.
		"""
		if params is None:
			raise Exception("Cannot find trials without parameters")
		
		# extend parameters
		prms = params.copy()
		if 'recruiting' not in prms:
			prms['recruiting'] = self.recruiting_only
		if self.limit_location is not None:
			prms['location_term'] = self.limit_location
		
		# perform search
		trials, meta, more = self.server.find(params=prms)
		total = meta.get('total') or 0
		if self.fetch_all:
			logging.warn("There are {} trials, I am only going to fetch the first 1000".format(total))
			while more and len(trials) <= 1000:
				more_trials, more_meta, more = self.server.find(request=more)
				trials.extend(more_trials)
		
		self.tamper_with(trials)
		return trials
	
	def tamper_with(self, trials):
		""" Gives a chance to tamper with trials.
		"""
		if trials is None or self.limit_location is None:
			return
		
		# remove non-desired locations
		for trial in trials:
			if trial.location is not None:
				locs = []
				for loc in trial.location:
					name = loc.get('facility', {}).get('name')
					if name and self.limit_location in name:
						locs.append(loc)
				if 0 == len(locs) and len(trial.location) > 0:
					locs = trial.location[0]
				trial.location = locs
