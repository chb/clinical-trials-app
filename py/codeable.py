#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Codeable(object):
	""" Holds a coding system and a code that can expand into child codes.
	"""
	
	class Code(object):
		def __init__(self, code, description=None, child_nodes=None):
			self.code = code
			self.description = description
			self.children = [self.__class__(tpl[0], tpl[1], tpl[2] if len(tpl) > 2 else None) for tpl in child_nodes] if child_nodes is not None else None
		
		def matches(self, code):
			if code == self.code:
				return self
			if self.children is not None:
				for child in self.children:
					if child.matches(code):
						return child
			return None
	
	
	def __init__(self, system, code, description=None, child_codes=None):
		""" child_codes must be a list that contains tuples in the form
		(code, desc); can be nested like (code, desc, ((c, d), (c, d))).
		"""
		self.system = system
		self.code = Codeable.Code(code, description, child_codes)
	
	def find(self, code):
		""" Returns a `Codeable.Code` instance, or None.
		"""
		if code is not None:
			return self.code.matches(code)
		return None
	
	def find_any(self, codes):
		""" Returns a `Codeable.Code` instance, or None.
		"""
		if codes is not None:
			for code in codes:
				matched = self.find(code)
				if matched is not None:
					return matched
		return None
