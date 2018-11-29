import unittest
import sys
sys.path.append('..')
from mztools import vcimport
from base64 import standard_b64decode

from unittest.mock import patch, Mock
from _pytest.monkeypatch import MonkeyPatch

from argparse import Namespace

class TestVcimport(unittest.TestCase):
    def setUp(self):
     self.monkeypatch = MonkeyPatch()
     self.lambdaMock = Mock()
     self.lambdaMock.run_lambda.return_value = {
        "mzsh_stdout": "OK\n"
     }

     self.monkeypatch.setattr('mztools.vcimport.run_lambda', lambda a,b: self.lambdaMock.run_lambda())
     self.monkeypatch.setattr('mztools.vcimport.tar_directory', lambda a: standard_b64decode("UGF4SGVhZGVyL2VtcHR5AAAAAAA="))
     self.monkeypatch.setattr('mztools.vcimport.get_parameter', lambda a: "value")
     self.monkeypatch.setattr('mztools.vcimport.s3_put_bytes', lambda a,b: "s3://dummybucket/dummyobj")

    @patch('mztools.common.boto3')
    @patch('getpass.getpass')
    @patch('os.listdir')
    def test_asks_for_password_if_not_in_arguments(self, listdir, getpass, boto3):
        args = Namespace(**{
            "environment": ["test"],
            "directory": ".",
            "overwrite": False,
            "excludesysdata": False,
            "includemeta": True,
            "user": "usernopasswd",
            "folders": [ "Examples" ],
            "message": None,
            "dryrun": False
        })
        listdir.return_value = []
        getpass.return_value = "thepass"


        result = vcimport.run_vcimport(args)

        self.assertEqual(getpass.called, True)
        self.assertEqual(result,True)

    @patch('mztools.common.boto3')
    @patch('getpass.getpass')
    @patch('os.listdir')
    def test_does_not_ask_for_passwd_if_given(self, listdir, getpass, boto3):
        args = Namespace(**{
            "environment": ["test"],
            "directory": ".",
            "overwrite": False,
            "user": "user/passwd",
            "folders": [ "Examples" ],
            "message": None,
            "dryrun": False
        })
        listdir.return_value = []
        getpass.return_value = "thepass"

        result = vcimport.run_vcimport(args)

        self.assertEqual(getpass.called, False)
        self.assertEqual(result,True)

    @patch('getpass.getpass')
    @patch('os.listdir')
    @patch('sys.exit')
    def test_aborts_when_env_ambiguous(self, mock_exit, listdir, getpass):
        args = Namespace(**{
            "environment": ["test", "dev"],
            "directory": ".",
            "overwrite": False,
            "user": "user/passwd",
            "folders": [ "Examples" ],
            "message": None,
            "dryrun": False
        })
        listdir.return_value = []
        getpass.return_value = "thepass"

        result = vcimport.run_vcimport(args)

        mock_exit.assert_has_calls([
            unittest.mock.call(1)
        ])
