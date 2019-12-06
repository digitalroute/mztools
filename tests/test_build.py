import unittest
import sys
import json
sys.path.append('..')
from mztools import build
from unittest.mock import patch, MagicMock
from argparse import Namespace

class TestBuild(unittest.TestCase):
    @patch('mztools.common.boto3')
    @patch('json.loads')
    def test_return_false_if_build_version_exists(self, mock_json, boto3):
        args = Namespace(**{ "version" : [ "0.0.1" ], "no_ec": "true"})
        payload = MagicMock()
        #payload.read.return_value.decode.return_value = '{ "available": [ "0.0.1" ]}'
        response = {}
        response['Payload'] = payload
        boto3.client().invoke.return_value = response

        mock_json.side_effect = [
            {'error': 'You are trying to build using the same version number again.\nPlease use another version number to build.'}
        ]

        result = build.run_build(args)
        self.assertEqual(result,False)

    @patch('mztools.build.sleep')
    @patch('mztools.build.SpinCursor')
    @patch('mztools.common.boto3')
    @patch('json.loads')
    def test_return_true_if_build_success(self, mock_json, boto3, spincursor, nosleep):
        args = Namespace(**{ "version" : [ "0.0.2" ], "no_ec": "true"})
        payload = MagicMock()
        response = {}
        response['Payload'] = payload
        boto3.client().invoke.return_value = response

        mock_json.side_effect = [
          # { 'available': [ "0.0.1" ] },
          { "buildId": "123:mockbuild" },
          { "buildStatus" : "BUILDING" },
          { "buildStatus" : "BUILDING" },
          { "buildStatus" : "BUILDING" },
          { "buildStatus" : "SUCCEEDED" }
        ]

        result = build.run_build(args)
        self.assertEqual(result,True)

    @patch('mztools.build.sleep')
    @patch('mztools.build.SpinCursor')
    @patch('mztools.common.boto3')
    @patch('json.loads')
    def test_return_false_if_build_failed(self, mock_json, boto3, spincursor, nosleep):
        args = Namespace(**{ "version" : [ "0.0.2" ], "no_ec": "true"})
        payload = MagicMock()
        response = {}
        response['Payload'] = payload
        boto3.client().invoke.return_value = response

        mock_json.side_effect = [
          # { 'available': [ "0.0.1" ] },
          { "buildId": "123:mockbuild" },
          { "buildStatus" : "BUILDING" },
          { "buildStatus" : "BUILDING" },
          { "buildStatus" : "BUILDING" },
          { "buildStatus" : "FAILED" }
        ]

        result = build.run_build(args)
        self.assertEqual(result,False)
