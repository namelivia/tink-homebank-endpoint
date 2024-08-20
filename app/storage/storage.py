from tink_http_python.authentication.storage import Storage
from tink_http_python.exceptions import (
    NoRefreshTokenException,
    NoAuthorizationCodeException,
)
import logging

logger = logging.getLogger(__name__)


class TokenStorage(Storage):
    def __init__(self):
        self.authorization_code = None

    def retrieve_authorization_code(self) -> str:
        if self.authorization_code is None:
            raise NoAuthorizationCodeException("Authorization code is not set")
        return self.authorization_code

    def store_new_authorization_code(self, new_authorization_code: str) -> str:
        self.authorization_code = new_authorization_code
