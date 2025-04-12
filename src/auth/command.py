from src.core import Command
from src.core import CommandContext
from src.auth.models import OAuthAuthorizationRequest
from bs4 import BeautifulSoup


class AuthorizeCommand(Command):
    def execute(self, context: CommandContext) -> CommandContext:
        params = OAuthAuthorizationRequest.from_config(context.config).model_dump(mode="json")
        context.last_response = context.session.get(str(context.config.authorize_url), params=params)
        return context


class SubmitLoginCommand(Command):
    def execute(self, context: CommandContext) -> CommandContext:
        data = {
            "UserName": context.config.username,
            "Password": context.config.password.get_secret_value(),
            "AuthMethod": "FormsAuthentication"
        }
        context.last_response = context.session.post(context.last_response.url, data=data)
        return context


class SubmitFormCommand(Command):
    def execute(self, context: CommandContext) -> CommandContext:
        soup = BeautifulSoup(context.last_response.text, "html.parser")
        if not (form := soup.find("form")):
            raise ValueError("No form found on page.")
        action_url = form["action"]
        inputs = {i["name"]: i.get("value", "") for i in form.find_all("input") if i.has_attr("name")}
        context.last_response = context.session.post(action_url, data=inputs)
        return context
