import unittest
import sys
sys.path.append('..')
from mztools import deploy
from unittest.mock import patch
from argparse import Namespace

class TestDeploy(unittest.TestCase):

    @patch('mztools.common.boto3')
    def test_return_false_if_already_deployed(self, boto3):
        args = Namespace(**{
            "no_ec": "true",
            "test": False,
            "promote": False,
            "dev": [ "0.0.1" ],
            "reset": False
        })
        boto3.client().get_parameter.return_value = { 'Parameter': { 'Value': '0.0.1' } }
        result = deploy.run_deploy(args)
        self.assertEqual(result, False)
