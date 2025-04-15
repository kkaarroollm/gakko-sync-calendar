import pytest

from src.auth.command import AuthorizeCommand, SubmitFormCommand, SubmitLoginCommand
from src.auth.models import OAuthAuthorizationRequest
from src.core import CommandContext
from tests.utils.response_fakes import fake_response


def test_authorize_command_sets_last_response(mock_session, mock_config):
    mock_session.get.return_value = fake_response(text="authorized")

    context = CommandContext(config=mock_config, session=mock_session)
    command = AuthorizeCommand()
    command.execute(context)

    mock_session.get.assert_called_once_with(
        str(mock_config.authorize_url),
        params=OAuthAuthorizationRequest.from_config(mock_config).model_dump(mode="json"),
    )


def test_submit_login_command_sets_last_response(mock_session, mock_config):
    context = CommandContext(config=mock_config, session=mock_session)
    context.last_response = fake_response(url="https://login.page", text="login form")

    mock_session.post.return_value = fake_response(text="after login")

    command = SubmitLoginCommand()
    command.execute(context)

    mock_session.post.assert_called_once_with(
        "https://login.page",
        data={
            "UserName": mock_config.username,
            "Password": mock_config.password.get_secret_value(),
            "AuthMethod": "FormsAuthentication",
        },
    )


def test_submit_form_command_parses_form_and_sets_last_response(mock_session, mock_config):
    html = """
    <form action="/submit">
        <input type="hidden" name="token" value="abc123" />
        <input name="btn" value="GO" />
    </form>
    """
    context = CommandContext(config=mock_config, session=mock_session)
    context.last_response = fake_response(text=html)

    mock_session.post.return_value = fake_response(text="submitted")

    command = SubmitFormCommand()
    command.execute(context)

    mock_session.post.assert_called_once_with("/submit", data={"token": "abc123", "btn": "GO"})


def test_submit_form_command_raises_if_no_form(mock_session, mock_config):
    html = "<html><body><p>No form here</p></body></html>"
    context = CommandContext(config=mock_config, session=mock_session)
    context.last_response = fake_response(text=html)

    command = SubmitFormCommand()
    with pytest.raises(ValueError, match=command.NO_FORM_ERROR):
        command.execute(context)
