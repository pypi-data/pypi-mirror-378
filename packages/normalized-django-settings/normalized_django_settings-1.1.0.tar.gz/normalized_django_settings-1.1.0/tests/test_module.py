#!python
"""
Testing the whole module
"""

from unittest import TestCase

import normalized_django_settings


class ModuleTest(TestCase):
	"""
	Tests for the module
	"""
	def test_dummy(self):
		"""
		Dummy test, checking for correct syntax
		"""

		normalized_django_settings
		self.assertEqual(True, True)  # add assertion here
