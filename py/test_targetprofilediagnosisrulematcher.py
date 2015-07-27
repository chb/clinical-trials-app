#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import json
import unittest
import trialpatient
import trialcondition
import targetprofile
import targetprofilediagnosisrulematcher

import clinicaltrials.jsondocument.jsonserver as jsonserver
import smartclient.fhirclient.models.condition as condition
import smartclient.fhirclient.models.observation as observation


class TargetProfileDiagnosisRuleMatcherTests(unittest.TestCase):
	"""
	"""
	def setUp(self):
		self.patient = trialpatient.TrialPatient('test-pat')
		with io.open(os.path.join('testdata', 'Condition_dstu2_inf_lob_ca.json')) as h:
			fhircond = condition.Condition(json.load(h))
			cond = trialcondition.TrialCondition.from_fhir(fhircond)
			self.patient.conditions = [cond]
	
	def makeHer2Pos(self, clean=True):
		if clean:
			self.patient.conditions[0].mutations = None
		obs = []
		with io.open(os.path.join('testdata', 'Observation_dstu2_HER2-positive.json')) as h:
			obs.append(observation.Observation(json.load(h)))
		self.patient.process_observations(obs)
	
	def makeHer2Neg(self, clean=True):
		if clean:
			self.patient.conditions[0].mutations = None
		obs = []
		with io.open(os.path.join('testdata', 'Observation_dstu2_HER2-negative.json')) as h:
			obs.append(observation.Observation(json.load(h)))
		self.patient.process_observations(obs)
	
	def makeESRPos(self, clean=True):
		if clean:
			self.patient.conditions[0].mutations = None
		obs = []
		with io.open(os.path.join('testdata', 'Observation_dstu2_ESR-positive.json')) as h:
			obs.append(observation.Observation(json.load(h)))
		self.patient.process_observations(obs)
	
	def makeESRNeg(self, clean=True):
		if clean:
			self.patient.conditions[0].mutations = None
		obs = []
		with io.open(os.path.join('testdata', 'Observation_dstu2_ESR-negative.json')) as h:
			obs.append(observation.Observation(json.load(h)))
		self.patient.process_observations(obs)
	
	def makePGRPos(self, clean=True):
		if clean:
			self.patient.conditions[0].mutations = None
		obs = []
		with io.open(os.path.join('testdata', 'Observation_dstu2_PGR-positive.json')) as h:
			obs.append(observation.Observation(json.load(h)))
		self.patient.process_observations(obs)
	
	def makePGRNeg(self, clean=True):
		if clean:
			self.patient.conditions[0].mutations = None
		obs = []
		with io.open(os.path.join('testdata', 'Observation_dstu2_PGR-negative.json')) as h:
			obs.append(observation.Observation(json.load(h)))
		self.patient.process_observations(obs)
	
	def testSetUp(self):
		self.assertIsNotNone(self.patient)
		self.assertIsNotNone(self.patient.conditions)
		self.assertIsNone(self.patient.conditions[0].mutations)
		self.makeHer2Pos()
		self.assertIsNotNone(self.patient.conditions[0].mutations)
	
	
	def testBreastCa(self):
		rulejs = {
			"description": "Patient must have active diagnosis of Breast cancer.",
			"type": "diagnosis",
			"include": True,
			"qualifier": "active",
			"inputs": [{
				"purl": "http://purl.bioontology.org/ontology/SNOMEDCT/254837009",
				"prefLabel": "Malignant tumor of breast",
				"description": "Breast cancer",
				"system": "snomedct",
				"code": "254837009"
			}]
		}
		profile = targetprofile.TargetProfile([rulejs])
		test = targetprofilediagnosisrulematcher.TargetProfileDiagnosisSNOMEDRuleMatcher(profile.rules[0])
		match = test.match_for(self.patient)
		self.assertIsNotNone(match)
		
	def testBreastTumorHER2Pos(self):
		rulejs = {
			"description": "Patient must have active diagnosis of HER2-positive carcinoma of breast.",
			"type": "diagnosis",
			"include": True,
			"qualifier": "active",
			"inputs": [{
				"purl": "http://purl.bioontology.org/ontology/SNOMEDCT/427685000",
				"prefLabel": "HER2-positive carcinoma of breast",
				"description": "HER2-positive carcinoma of breast",
				"system": "snomedct",
				"code": "427685000"
			}]
		}
		profile = targetprofile.TargetProfile([rulejs])
		test = targetprofilediagnosisrulematcher.TargetProfileDiagnosisSNOMEDRuleMatcher(profile.rules[0])
		self.assertIsNone(test.match_for(self.patient))
		self.makeHer2Neg()
		self.assertIsNone(test.match_for(self.patient))
		self.makeHer2Pos()
		self.assertIsNotNone(test.match_for(self.patient))
		self.makeESRPos()
		self.assertIsNone(test.match_for(self.patient))
	
	def testBreastTumorHER2Neg(self):
		rulejs = {
			"description": "Patient must have active diagnosis of Human epidermal growth factor 2 negative carcinoma of breast.",
			"type": "diagnosis",
			"include": True,
			"qualifier": "active",
			"inputs": [{
				"purl": "http://purl.bioontology.org/ontology/SNOMEDCT/431396003",
				"prefLabel": "Human epidermal growth factor 2 negative carcinoma of breast",
				"description": "Human epidermal growth factor 2 negative carcinoma of breast",
				"system": "snomedct",
				"code": "431396003"
			}]
		}
		profile = targetprofile.TargetProfile([rulejs])
		test = targetprofilediagnosisrulematcher.TargetProfileDiagnosisSNOMEDRuleMatcher(profile.rules[0])
		self.assertIsNotNone(test.match_for(self.patient))
		self.makeHer2Pos()
		self.assertIsNone(test.match_for(self.patient))
		self.makeHer2Neg()
		self.assertIsNotNone(test.match_for(self.patient))
		self.makeESRPos()
		self.assertIsNotNone(test.match_for(self.patient))
	
	def testBreastTumorESRPos(self):
		rulejs = {
			"description": "Patient must have active diagnosis of Estrogen receptor positive tumor.",
			"type": "diagnosis",
			"include": True,
			"qualifier": "active",
			"inputs": [{
				"purl": "http://purl.bioontology.org/ontology/SNOMEDCT/416053008",
				"prefLabel": "Estrogen receptor positive tumor",
				"description": "Estrogen receptor positive tumor",
				"system": "snomedct",
				"code": "416053008"
			}]
		}
		profile = targetprofile.TargetProfile([rulejs])
		test = targetprofilediagnosisrulematcher.TargetProfileDiagnosisSNOMEDRuleMatcher(profile.rules[0])
		self.assertIsNone(test.match_for(self.patient))
		self.makeESRPos()
		self.assertIsNotNone(test.match_for(self.patient))
		self.makePGRPos(False)
		self.assertIsNotNone(test.match_for(self.patient))
		self.makeESRNeg()
		self.assertIsNone(test.match_for(self.patient))
		self.makeHer2Pos()
		self.assertIsNone(test.match_for(self.patient))
		self.makePGRPos()
		self.assertIsNone(test.match_for(self.patient))
	
	def testBreastTumorESRNeg(self):
		rulejs = {
			"description": "Patient must have active diagnosis of Estrogen receptor negative neoplasm.",
			"type": "diagnosis",
			"include": True,
			"qualifier": "active",
			"inputs": [{
				"purl": "http://purl.bioontology.org/ontology/SNOMEDCT/441117001",
				"prefLabel": "Estrogen receptor negative neoplasm",
				"description": "Estrogen receptor negative neoplasm",
				"system": "snomedct",
				"code": "441117001"
			}]
		}
		profile = targetprofile.TargetProfile([rulejs])
		test = targetprofilediagnosisrulematcher.TargetProfileDiagnosisSNOMEDRuleMatcher(profile.rules[0])
		self.assertIsNotNone(test.match_for(self.patient))
		self.makeHer2Pos()
		self.assertIsNotNone(test.match_for(self.patient))
		self.makeESRNeg()
		self.assertIsNotNone(test.match_for(self.patient))
		self.makeESRPos()
		self.assertIsNone(test.match_for(self.patient))
		self.makePGRPos(False)
		self.assertIsNone(test.match_for(self.patient))
	
	def testBreastTumorPGRPos(self):
		rulejs = {
			"description": "Patient must not have active diagnosis of Progesterone receptor positive tumor.",
			"type": "diagnosis",
			"include": False,
			"qualifier": "active",
			"inputs": [{
				"purl": "http://purl.bioontology.org/ontology/SNOMEDCT/416561008",
				"prefLabel": "Progesterone receptor positive tumor",
				"description": "Progesterone receptor positive tumor",
				"system": "snomedct",
				"code": "416561008"
			}]
		}
		profile = targetprofile.TargetProfile([rulejs])
		test = targetprofilediagnosisrulematcher.TargetProfileDiagnosisSNOMEDRuleMatcher(profile.rules[0])
		self.assertIsNone(test.match_for(self.patient))
		self.makeESRPos()
		self.assertIsNone(test.match_for(self.patient))
		self.makePGRPos(False)
		self.assertIsNotNone(test.match_for(self.patient))
		self.makeESRNeg()
		self.assertIsNone(test.match_for(self.patient))
		self.makeHer2Pos()
		self.assertIsNone(test.match_for(self.patient))
		self.makePGRPos()
		self.assertIsNotNone(test.match_for(self.patient))
	
	def testBreastTumorPGRNeg(self):
		rulejs = {
			"description": "Patient must have active diagnosis of Progesterone receptor negative neoplasm.",
			"type": "diagnosis",
			"include": True,
			"qualifier": "active",
			"inputs": [{
				"purl": "http://purl.bioontology.org/ontology/SNOMEDCT/441118006",
				"prefLabel": "Progesterone receptor negative neoplasm",
				"description": "Progesterone receptor negative neoplasm",
				"system": "snomedct",
				"code": "441118006"
			}]
		}
		profile = targetprofile.TargetProfile([rulejs])
		test = targetprofilediagnosisrulematcher.TargetProfileDiagnosisSNOMEDRuleMatcher(profile.rules[0])
		self.assertIsNotNone(test.match_for(self.patient))
		self.makeHer2Pos()
		self.assertIsNotNone(test.match_for(self.patient))
		self.makeESRNeg()
		self.assertIsNotNone(test.match_for(self.patient))
		self.makeESRPos()
		self.assertIsNotNone(test.match_for(self.patient))
		self.makePGRPos(False)
		self.assertIsNone(test.match_for(self.patient))
	
	def testBreastTumorHormonePos(self):
		rulejs = {
			"description": "Patient must have active diagnosis of Hormone receptor positive malignant neoplasm of breast.",
			"type": "diagnosis",
			"include": True,
			"qualifier": "active",
			"inputs": [{
				"purl": "http://purl.bioontology.org/ontology/SNOMEDCT/417181009",
				"prefLabel": "Hormone receptor positive malignant neoplasm of breast",
				"description": "Hormone receptor positive malignant neoplasm of breast",
				"system": "snomedct",
				"code": "417181009"
			}]
		}
		profile = targetprofile.TargetProfile([rulejs])
		test = targetprofilediagnosisrulematcher.TargetProfileDiagnosisSNOMEDRuleMatcher(profile.rules[0])
		self.assertIsNone(test.match_for(self.patient))
		# self.makeESRPos()
		# self.assertIsNone(test.match_for(self.patient))
		# self.makePGRPos(False)
		# self.assertIsNotNone(test.match_for(self.patient))
		# self.makeESRNeg()
		# self.assertIsNone(test.match_for(self.patient))
		# self.makeHER2Pos(False)
		# self.assertIsNone(test.match_for(self.patient))
		# self.makePGRPos()
		# self.assertIsNone(test.match_for(self.patient))


trialpatient.TrialPatientInfo.hookup(jsonserver.JSONServer(), 'none')

