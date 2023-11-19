import os
from app.storage.storage import TokenStorage
from tink_http_python.tink import Tink
from tink_http_python.exceptions import NoAuthorizationCodeException

from fastapi import FastAPI, Query
from logging import Logger

logger = Logger(__name__)

app = FastAPI()


@app.get("/")
def read_root(
    code: str = Query(
        ..., title="Authorization Code", description="The authorization code"
    ),
    credentials_id: str = Query(
        ..., title="Credentials ID", description="The credentials ID"
    ),
):
    # Store the authorization code
    storage = TokenStorage()
    storage.store_new_authorization_code(code)

    try:
        tink = Tink(
            client_id=os.environ.get("TINK_CLIENT_ID"),
            client_secret=os.environ.get("TINK_CLIENT_SECRET"),
            redirect_uri=os.environ.get("TINK_CALLBACK_URI"),
            storage=storage,
        )
    except NoAuthorizationCodeException:
        logger.error("No authorization code found")
        return {"Status": "ERROR"}

    return {"Status": "OK"}
