from urllib.parse import urlencode

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from src.auth.models import OAuthAuthorizationRequest
from src.core import Command, CommandContext


class NavigateToLoginCommand(Command):
    """Navigate to the ADFS OAuth authorize endpoint.
    The browser follows the redirect chain to the ADFS login form automatically."""

    def execute(self, context: CommandContext) -> CommandContext:
        params = OAuthAuthorizationRequest.from_config(context.config).model_dump(mode="json")
        authorize_url = f"{context.config.authorize_url}?{urlencode(params)}"
        context.driver.get(authorize_url)
        return context


class SubmitCredentialsCommand(Command):
    """Fill in the ADFS login form and submit.
    The browser handles all subsequent redirects (hidden form posts, token exchange) automatically."""

    TIMEOUT: int = 15

    def execute(self, context: CommandContext) -> CommandContext:
        wait = WebDriverWait(context.driver, self.TIMEOUT)

        username_field = wait.until(expected_conditions.presence_of_element_located((By.ID, "userNameInput")))
        password_field = context.driver.find_element(By.ID, "passwordInput")
        submit_button = context.driver.find_element(By.ID, "submitButton")

        username_field.clear()
        username_field.send_keys(context.config.username)
        password_field.clear()
        password_field.send_keys(context.config.password.get_secret_value())
        submit_button.click()

        wait.until(expected_conditions.url_contains(str(context.config.base_url).rstrip("/")))

        return context
