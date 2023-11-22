from tink_http_python.authentication.storage import Storage
from tink_http_python.exceptions import (
    NoRefreshTokenException,
    NoAuthorizationCodeException,
)


class TokenStorage(Storage):
    def __init__(self):
        self.refresh_token = None
        self.atuhorization_code = None

    def store_new_refresh_token_refresh_token(self, new_refresh_token) -> None:
        self.refresh_token = new_refresh_token

    def retrieve_refresh_token(self) -> str:
        if self.refresh_token is None:
            raise NoRefreshTokenException("Refresh token is not set")
        return self.refresh_token

    def retrieve_authorization_code(self) -> str:
        if self.authorization_code is None:
            raise NoAuthorizationCodeException("Authorization code is not set")
        return self.authorization_code

    def store_new_authorization_code(self, new_authorization_code: str) -> str:
        self.authorization_code = new_authorization_code
