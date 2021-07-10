import unittest
from unittest.mock import patch

from api.helpers.utils.exceptions import UnconfiguredEnvironmentVariableException
from api.helpers.utils.rollbar import init_rollbar


class TestRollbar(unittest.TestCase):

    def setUp(self):
        self.mock_development_env = patch("api.helpers.utils.rollbar.env", "development")
        self.mock_staging_env = patch("api.helpers.utils.rollbar.env", "staging")
        self.start_url = 'http://fake-website.fr'

    @patch("api.helpers.utils.rollbar.report_message")
    @patch('api.helpers.utils.rollbar.init')
    @patch('api.helpers.utils.rollbar.get_rollbar_token')
    def test_it_does_not_call_rollbar_if_no_token_on_development_env(self, mo_rollbar_token, mock_init, __):
        mo_rollbar_token.return_value = None
        with self.mock_development_env:
            init_rollbar(self.start_url)

        mock_init.assert_not_called()

    @patch("api.helpers.utils.rollbar.report_message")
    @patch('api.helpers.utils.rollbar.init')
    @patch('api.helpers.utils.rollbar.get_rollbar_token')
    def test_it_raises_an_exception_if_no_token_set_for_non_development_env(self, mo_rollbar_token, _, __):
        mo_rollbar_token.return_value = None
        with self.mock_staging_env:
            with self.assertRaises(UnconfiguredEnvironmentVariableException):
                init_rollbar(self.start_url)

    @patch("api.helpers.utils.rollbar.report_message")
    @patch('api.helpers.utils.rollbar.init')
    @patch('api.helpers.utils.rollbar.get_rollbar_token')
    def test_it_calls_rollbar_if_everything_is_set(self, mo_rollbar_token, mo_init, mo_message):
        with self.mock_staging_env:
            mo_rollbar_token.return_value = "faketoken"
            init_rollbar(self.start_url)

        mo_init.assert_called_once_with("faketoken", "staging")
        mo_message.assert_called()
