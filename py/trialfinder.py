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
		
		# perform search
		trials, meta, more = self.server.find(params=prms)
		total = meta.get('total') or 0
		if self.fetch_all:
			logging.warn("There are {} trials, I am only going to fetch the first 1000".format(total))
			while more and len(trials) <= 1000:
				more_trials, more_meta, more = self.server.find(request=more)
				trials.extend(more_trials)
		
		return trials
