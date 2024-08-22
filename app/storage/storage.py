from tink_http_python.authentication.storage import Storage
from tink_http_python.exceptions import (
    NoAccessTokenException,
    NoAuthorizationCodeException,
)
import logging

logger = logging.getLogger(__name__)


class TokenStorage(Storage):
    def __init__(self):
        self.authorization_code = None
        self.access_token = None

    def retrieve_authorization_code(self) -> str:
        if self.authorization_code is None:
            raise NoAuthorizationCodeException("Authorization code is not set")
        return self.authorization_code

    def store_new_authorization_code(self, new_authorization_code: str) -> str:
        self.authorization_code = new_authorization_code

    def retrieve_access_token(self) -> str:
        if self.access_token is None:
            raise NoAccessTokenException("Access token is not set")
        return self.access_token

    def store_new_access_token(self, new_access_token: str) -> str:
        self.access_token = new_access_token
