import unittest
import sys
sys.path.append('..')
from mztools import log

from unittest.mock import patch, Mock
from _pytest.monkeypatch import MonkeyPatch

from argparse import Namespace

class TestLog(unittest.TestCase):
    def setUp(self):
     self.monkeypatch = MonkeyPatch()

    @patch('mztools.common.boto3')
    def test_returns_last_stream_events(self, boto3):
        args = Namespace(**{
            "environment": "test",
        })

        boto3.client().describe_log_streams.return_value = {
            "logStreams": [
                {
                    "logStreamName": "logstreamname",
                    "lastEventTimestamp": 123000
                },
                {
                    "logStreamName": "olderlogstream",
                    "lastEventTimestamp": 100000
                }
            ]
        }
        boto3.client().get_log_events.return_value = {
            "events": [
                {
                    "message": "all your base are belong to us",
                    "timestamp": 123000
                 }
            ]
        }
        result = log.run_log(args)
        boto3.client().get_log_events.assert_called_with(logGroupName='/test/platform', logStreamName='logstreamname', startFromHead=False)

        self.assertEqual(result,True)
