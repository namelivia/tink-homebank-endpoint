from tink_http_python.authentication.storage import Storage


class TokenStorage(Storage):
    def __init__(self):
        self.refresh_token = ""
        self.atuhorization_code = ""

    def store_new_refresh_token_refresh_token(self, new_refresh_token) -> None:
        self.refresh_token = new_refresh_token

    def retrieve_refresh_token(self) -> str:
        return self.refresh_token

    def retrieve_authorization_code(self) -> str:
        return self.authorization_code

    def store_new_authorization_code(self, new_authorization_code: str) -> str:
        self.authorization_code = new_authorization_code
