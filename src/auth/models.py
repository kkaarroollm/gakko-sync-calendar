from pydantic import BaseModel, HttpUrl

from src.core import GakkoConfig


class OAuthAuthorizationRequest(BaseModel):
    client_id: str
    redirect_uri: HttpUrl
    response_type: str = "id_token"
    scope: str = "openid profile"
    response_mode: str = "form_post"
    nonce: str = "secure-random-nonce"  # random string for security
    state: str = "secure-random-state"  # random string for security

    @classmethod
    def from_config(cls, config: "GakkoConfig") -> "OAuthAuthorizationRequest":
        return cls(client_id=config.client_id, redirect_uri=config.redirect_uri)
