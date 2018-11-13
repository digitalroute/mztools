import unittest
import sys
sys.path.append('..')
from mztools import vcexport
from unittest.mock import patch, Mock
from _pytest.monkeypatch import MonkeyPatch

from argparse import Namespace

class TestVcexport(unittest.TestCase):
    def setUp(self):
     self.monkeypatch = MonkeyPatch()
     self.lambdaMock = Mock()
     self.lambdaMock.run_lambda.return_value = {
        "tarfile": "UGF4SGVhZGVyL2VtcHR5AAAAAAA="
     }

     self.monkeypatch.setattr('mztools.vcexport.run_lambda', lambda a,b: self.lambdaMock.run_lambda())
     self.monkeypatch.setattr('mztools.vcexport.untar_bytes', lambda a,b: True)

    @patch('getpass.getpass')
    @patch('os.listdir')
    def test_asks_for_password_if_not_in_arguments(self, listdir, getpass):
        args = Namespace(**{
            "environment": "test",
            "directory": ".",
            "overwrite": False,
            "excludesysdata": False,
            "includemeta": True,
            "user": "usernopasswd",
            "folders": [ "Examples" ]
        })
        listdir.return_value = []
        getpass.return_value = "thepass"


        result = vcexport.run_vcexport(args)

        self.assertEqual(getpass.called, True)
        self.assertEqual(result,True)

    @patch('getpass.getpass')
    @patch('os.listdir')
    def test_does_not_ask_for_passwd_if_given(self, listdir, getpass):
        args = Namespace(**{
            "environment": "test",
            "directory": ".",
            "overwrite": False,
            "excludesysdata": False,
            "includemeta": True,
            "user": "user/passwd",
            "folders": [ "Examples" ]
        })
        listdir.return_value = []
        getpass.return_value = "thepass"
        self.lambdaMock.reset_mock()

        result = vcexport.run_vcexport(args)

        self.assertEqual(self.lambdaMock.run_lambda.called, True)
        self.assertEqual(getpass.called, False)
        self.assertEqual(result,True)

    @patch('os.listdir')
    def test_aborts_when_exportdir_not_empty(self, listdir):
        args = Namespace(**{
            "environment": "test",
            "directory": ".",
            "overwrite": False,
            "excludesysdata": False,
            "includemeta": True,
            "user": "usernopasswd",
            "folders": [ "Examples" ]
        })
        listdir.return_value = ["Afile"]
        self.lambdaMock.reset_mock()

        result = vcexport.run_vcexport(args)

        self.lambdaMock.run_lambda.assert_not_called()
        self.assertEqual(result,False)
