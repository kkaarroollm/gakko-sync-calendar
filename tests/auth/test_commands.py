from unittest.mock import MagicMock, patch
from urllib.parse import urlencode

from src.auth.command import NavigateToLoginCommand, SubmitCredentialsCommand
from src.auth.models import OAuthAuthorizationRequest
from src.core import CommandContext


def test_navigate_to_login_calls_driver_get_with_oauth_url(mock_driver, mock_config):
    context = CommandContext(config=mock_config, driver=mock_driver)
    command = NavigateToLoginCommand()
    command.execute(context)

    mock_driver.get.assert_called_once()
    url_called = mock_driver.get.call_args[0][0]
    params = OAuthAuthorizationRequest.from_config(mock_config).model_dump(mode="json")
    expected_url = f"{mock_config.authorize_url}?{urlencode(params)}"
    assert url_called == expected_url


def test_submit_credentials_fills_form_and_submits(mock_driver, mock_config):
    context = CommandContext(config=mock_config, driver=mock_driver)

    mock_username = MagicMock()
    mock_password = MagicMock()
    mock_submit = MagicMock()

    with patch("src.auth.command.WebDriverWait") as mock_wait_cls:
        mock_wait = MagicMock()
        mock_wait_cls.return_value = mock_wait
        mock_wait.until.side_effect = [mock_username, True]
        mock_driver.find_element.side_effect = [mock_password, mock_submit]

        command = SubmitCredentialsCommand()
        command.execute(context)

    mock_username.clear.assert_called_once()
    mock_username.send_keys.assert_called_once_with(mock_config.username)
    mock_password.clear.assert_called_once()
    mock_password.send_keys.assert_called_once_with(mock_config.password.get_secret_value())
    mock_submit.click.assert_called_once()
