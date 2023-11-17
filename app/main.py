import os
from app.storage.storage import TokenStorage
from tink_http_python.tink import Tink

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
    logger.info(f"Authorization Code: {code}")
    logger.info(f"Credentials ID: {credentials_id}")
    storage = TokenStorage()
    storage.store_new_refresh_token_refresh_token(code)
    logger.info(f"Tink Client Id: {os.environ.get('TINK_CLIENT_ID')}")
    logger.info(f"Tink Client Secret: {os.environ.get('TINK_CLIENT_SECRET')}")
    return {"Status": "OK"}
