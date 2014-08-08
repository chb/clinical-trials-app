#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from patient import Patient


class TestPatient(unittest.TestCase):
	
	def test_initialization(self):
		with self.assertRaises(Exception) as context:
			Patient()		# no id must raise
		
		pat = Patient('x')
		self.assertEqual('female', pat.gender)
		
		pat.country = "USA"
		self.assertEqual("USA", pat.country)
		self.assertEqual("USA", pat.location)
		pat.city = "Boston"
		self.assertEqual("Boston, USA", pat.location)
		pat.country = None
		self.assertEqual("Boston", pat.location)
		pat.region = "MA"
		self.assertEqual("Boston, MA", pat.location)

	
