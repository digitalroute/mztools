import unittest
import sys
sys.path.append('..')
from mztools import vcimport
from unittest.mock import patch, Mock
from _pytest.monkeypatch import MonkeyPatch

from argparse import Namespace

class TestVcexport(unittest.TestCase):
    def setUp(self):
     self.monkeypatch = MonkeyPatch()
     self.monkeypatch.setattr('mztools.vcimport.find_single_cluster', lambda a,b: "singlecluster")
     kube_mock = Mock()
     kube_mock.exec_pod_command.return_value = {
         "success": True,
         "stdout": [],
         "stderr": [ "/tmp/baz is the IMPORT_DIR" ],
         "pod_name": "mockpod",
     }
     self.monkeypatch.setattr('mztools.vcimport.K8sexec', lambda kops_state_bucket, kops_cluster_name: kube_mock)
     self.monkeypatch.setattr('mztools.vcimport.tar_directory', lambda a: True)

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
            "environment": "test",
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
