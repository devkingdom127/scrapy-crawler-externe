from unittest import TestCase
from unittest.mock import patch, Mock

from api.controllers.run import post


class TestRunControllerPost(TestCase):

    @patch('api.controllers.run.Crawler')
    def test_post(self, crawler_mock):
        body = Mock()
        post(body=body)

        crawler_mock.run.assert_called_once_with(body)
