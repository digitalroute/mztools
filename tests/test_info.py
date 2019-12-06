import unittest
import sys
sys.path.append('..')
from mztools import info
from unittest.mock import patch

class TestInfo(unittest.TestCase):
    @patch('mztools.common.boto3')
    def test_run_info(self, boto3):
        args = "anything"
        result = info.run_info(args)

        # The last call to boto3 get_parameter was for '/prod/ec/version'
        boto3.client().get_parameter.assert_called_with(Name='/prod/platform/version', WithDecryption=False)

        # The command returns true
        self.assertEqual(result,True)
