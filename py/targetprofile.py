#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import json
import logging


class TargetProfile(object):
	""" Class representing one target profile in JSON format.
	"""
	rule_classes = {}
	
	@classmethod
	def register_rule(cls, klass):
		""" Register a TargetProfileRule to handle rules of a given type.
		"""
		if klass is None:
			raise Exception("I need a class")
		for_type = klass.for_type
		if not for_type:
			raise Exception("I need a class with a type name")
		if for_type in cls.rule_classes:		# could check if class is different to fail gracefully on double-imports
			raise Exception("I have already registered {} for {}".format(cls.rule_classes[for_type]), for_type)
		cls.rule_classes[for_type] = klass
	
	
	def __init__(self, json_arr):
		self.rules = []
		if json_arr is not None:
			if not isinstance(json_arr, list):
				raise Exception("Only supporting JSON formats whose root is a list, is {}".format(type(json_arr)))
			for js in json_arr:
				klass = self.rule_classes.get(js.get('type'))
				if klass is None:
					logging.info('No target profile rule class to represent "{}", using base class'.format(js.get('type')))
					klass = TargetProfileRule
				self.rules.append(klass(js))
	
	
	# Mark: Parsing
	
	@classmethod
	def load(cls, json_handle):
		""" Load a target profile from a file handle pointing at a JSON file.
		"""
		return cls(json.load(json_handle))
	
	@classmethod
	def loads(cls, json_string):
		""" Load a target profile from a JSON string.
		"""
		return cls(json.loads(json_string))


class TargetProfileRule(object):
	""" Abstract base class for target profile model representations.
	"""
	for_type = None
	
	def __init__(self, json_dict):
		self.type = None
		self.description = None
		self.include = True
		
		if json_dict is not None:
			self.type = json_dict.get('type')
			self.description = json_dict.get('description')
			self.include = json_dict.get('include')
	

class TargetProfilePatientState(TargetProfileRule):
	""" Describe a patient's state.
	"""
	for_type = 'state'


class TargetProfileGender(TargetProfileRule):
	""" Limit a patient's gender.
	"""
	for_type = 'gender'


class TargetProfileAge(TargetProfileRule):
	""" Limit a patient's age.
	"""
	for_type = 'age'


class TargetProfileDiagnosis(TargetProfileRule):
	""" Require or exclude based on a diagnosis.
	"""
	for_type = 'diagnosis'
	
	def __init__(self, json_dict):
		super().__init__(json_dict)
		self.diagnosis = None
		
		if json_dict is not None:
			inp_1 = json_dict['inputs'][0] if json_dict.get('inputs') and len(json_dict['inputs']) > 0 else None
			if inp_1 is not None:
				self.diagnosis = TargetProfileInputDiagnosis(inp_1)


class TargetProfileMeasurement(TargetProfileRule):
	""" Describe or exclude a patient metric.
	"""
	for_type = 'measurement'


class TargetProfileAllergy(TargetProfileRule):
	""" Handle allergies.
	"""
	for_type = 'allergy'


class TargetProfileMedicalScore(TargetProfileRule):
	""" Handle medical scores.
	"""
	for_type = 'score'


class TargetProfileMedication(TargetProfileRule):
	""" Handle medications.
	"""
	for_type = 'medication'


class TargetProfileProcedure(TargetProfileRule):
	""" Handle procedures.
	"""
	for_type = 'procedure'


class TargetProfileAgreement(TargetProfileRule):
	""" Handle agreements.
	"""
	for_type = 'agreement'


class TargetProfileAdverseEvent(TargetProfileRule):
	""" Handle adverse events.
	"""
	for_type = 'adverse-event'


class TargetProfileLabValue(TargetProfileRule):
	""" Handle lab values.
	"""
	for_type = 'labValue'


class TargetProfileMutation(TargetProfileRule):
	""" Handle mutation information.
	"""
	for_type = 'mutation'


class TargetProfileCancerStage(TargetProfileRule):
	""" Handle cancer stage description.
	"""
	for_type = 'cancer_stage'


class TargetProfileDevice(TargetProfileRule):
	""" Handle devices.
	"""
	for_type = 'device'


TargetProfile.register_rule(TargetProfilePatientState)
TargetProfile.register_rule(TargetProfileGender)
TargetProfile.register_rule(TargetProfileAge)
TargetProfile.register_rule(TargetProfileDiagnosis)
TargetProfile.register_rule(TargetProfileMeasurement)
TargetProfile.register_rule(TargetProfileAllergy)
TargetProfile.register_rule(TargetProfileMedicalScore)
TargetProfile.register_rule(TargetProfileMedication)
TargetProfile.register_rule(TargetProfileProcedure)
TargetProfile.register_rule(TargetProfileAgreement)
TargetProfile.register_rule(TargetProfileAdverseEvent)
TargetProfile.register_rule(TargetProfileLabValue)
TargetProfile.register_rule(TargetProfileMutation)
TargetProfile.register_rule(TargetProfileCancerStage)
TargetProfile.register_rule(TargetProfileDevice)


class TargetProfileInput(object):
	""" Superclass for all input objects of a target profile criterion.
	The JSON representation for these is still in flux, so this will change
	A LOT.
	"""
	def __init__(self, json_dict):
		self.description = json_dict.get('description') if json_dict is not None else None
	

class TargetProfileInputDiagnosis(TargetProfileInput):
	def __init__(self, json_dict):
		super().__init__(json_dict)
		self.system = json_dict.get('system') if json_dict is not None else None
		self.code  = json_dict.get('code') if json_dict is not None else None

