import os
from app.storage.storage import TokenStorage
from tink_http_python.tink import Tink
from tink_http_python.exceptions import NoAuthorizationCodeException
from tink_http_python.transactions import Transactions

from fastapi import FastAPI, Query
from fastapi.logger import logger
import requests
import logging

# Show logs in gunicorn
gunicorn_logger = logging.getLogger("gunicorn.error")
logger.handlers = gunicorn_logger.handlers

# Enable debug logging for urllib3
requests_logger = logging.getLogger("requests.packages.urllib3")
requests_logger.setLevel(logging.DEBUG)
requests_logger.propagate = True


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
        try:
            transactions = tink.transactions().get()
        except requests.exceptions.HTTPError as e:
            logger.error("Error when making the request")
            logger.error("Request details:")
            logger.error(e.request.__dict__)
            logger.error("Response details:")
            logger.error(e.response.__dict__)
            exit(1)

    except NoAuthorizationCodeException:
        logger.error("No authorization code found")
        return {"Status": "ERROR"}

    transaction = transactions[0]
    return {"Status": "OK", "Transaction": transaction.descriptions.original}
