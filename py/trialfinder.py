#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging


class TrialFinder(object):
	""" Find trials on a server.
	"""
	
	def __init__(self, server, trial_class=None):
		assert server
		self.server = server
		self.trial_class = trial_class
		
		self.fetch_all = True
		self.recruiting_only = True
		self.limit_location = 'Nashville'
		self.limit_countries = ['United States']
	
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
		if self.limit_countries is not None:
			prms['countries'] = self.limit_countries
		
		# perform search
		trials, meta, more = self.server.find(params=prms, trial_class=self.trial_class)
		if more and self.fetch_all:
			maximum = 1000
			total = int(meta.get('total') or 0)
			if total > maximum:
				logging.warn("There are {} trials, I am only going to fetch the first {}".format(total, maximum))
			while more and len(trials) <= maximum:
				more_trials, more_meta, more = self.server.find(request=more, trial_class=self.trial_class)
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
			if trial.locations is not None:
				locs = []
				for loc in trial.locations:
					inc = False
					if loc.facility is not None:
						if self.limit_location in loc.facility.get('name', ''):
							inc = True
						elif self.limit_location in loc.facility.get('address', {}).get('city', ''):
							inc = True
						elif self.limit_location in loc.facility.get('address', {}).get('state', ''):
							inc = True
					if inc:
						locs.append(loc)
				
				if len(locs) > 0:
					trial.locations = locs
	
