from pathlib import Path

from pydantic import FilePath, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class GakkoConfig(BaseSettings):
    client_id: str = "totally-not-a-client-id"
    username: str = "for-sure-not-a-username"
    password: SecretStr = SecretStr("definitely-not-a-password")
    authorize_url: HttpUrl = HttpUrl("https://adfs.pjwstk.edu.pl/adfs/oauth2/authorize")
    redirect_uri: HttpUrl = HttpUrl("https://gakko.pjwstk.edu.pl/signin-oidc")
    base_url: HttpUrl = HttpUrl("https://gakko.pjwstk.edu.pl/")
    default_timezone: str = "Europe/Warsaw"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="GAKKO_", env_file_encoding="utf-8")


class CalendarConfig(BaseSettings):
    credentials_path: FilePath = Path("token.json")
    calendar_id: str = "primary"


gakko_config = GakkoConfig()
