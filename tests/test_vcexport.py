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
     self.monkeypatch.setattr('mztools.vcexport.find_single_cluster', lambda a,b: "singlecluster")
     self.K8sexec_Mock = Mock()
     self.K8sexec_Mock.exec_pod_command.return_value = {
         "success": True,
         "stdout": [],
         "stderr": [ "/tmp/baz is the EXPORT_DIR" ],
         "pod_name": "mockpod",
     }
     self.monkeypatch.setattr('mztools.vcexport.K8sexec', lambda kops_state_bucket, kops_cluster_name: self.K8sexec_Mock)
     self.monkeypatch.setattr('mztools.vcexport.untar_bytes', lambda a,b: True)

    @patch('mztools.common.boto3')
    @patch('getpass.getpass')
    @patch('os.listdir')
    def test_asks_for_password_if_not_in_arguments(self, listdir, getpass, boto3):
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

    @patch('mztools.common.boto3')
    @patch('getpass.getpass')
    @patch('os.listdir')
    def test_does_not_ask_for_passwd_if_given(self, listdir, getpass, boto3):
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

        result = vcexport.run_vcexport(args)

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
        self.K8sexec_Mock.reset_mock()

        result = vcexport.run_vcexport(args)
        self.K8sexec_Mock.assert_not_called()
        self.assertEqual(result,False)
