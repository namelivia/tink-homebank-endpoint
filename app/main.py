import os
import csv
import time
from datetime import datetime
from app.storage.storage import TokenStorage
from tink_http_python.tink import Tink
from tink_http_python.exceptions import NoAuthorizationCodeException
from tink_http_python.transactions import Transactions

from fastapi import FastAPI, Query, Cookie, HTTPException
from fastapi.logger import logger
from fastapi.responses import RedirectResponse
import requests
import logging
from shutil import copyfile

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
    date_until: str = Cookie(default=None),
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
        transactions = tink.transactions().get()

    except NoAuthorizationCodeException:
        logger.error("No authorization code found")
        raise HTTPException(status_code=400, detail="No authorization code found")

    if date_until is None:
        raise HTTPException(status_code=400, detail="date_until cookie not found")

    below_target_date = False
    page_token = None
    # Generate CSV
    current_timestamp = int(time.time())
    csv_path = os.environ.get("CSV_PATH")
    file_name = f"{csv_path}/output_{current_timestamp}.csv"
    with open(file_name, "w") as f:
        writer = csv.writer(f, delimiter=";")
        while not below_target_date:
            for transaction in transactions.transactions:
                if not below_target_date:
                    transaction_date = transaction.dates.booked
                    below_target_date = transaction_date < date_until
                    if below_target_date:
                        logger.info("Transaction dates below target date, stopping")
                    category = "pending"
                    memo = "pending"
                    writer.writerow(
                        (
                            transaction_date,
                            transaction.descriptions.original,
                            memo,
                            Transactions.calculate_real_amount(
                                transaction.amount.value
                            ),
                            category,
                        )
                    )
            if not below_target_date:
                logger.info("Transaction dates above target date, continuing")
                next_page_token = transactions.next_page_token
                transactions = tink.transactions().get(pageToken=next_page_token)
    configuration_file_name = f"{csv_path}/output_{current_timestamp}.json"
    configuration_template_file_name = "templates/importer_configuration.json"
    copyfile(configuration_template_file_name, configuration_file_name)
    return {"Status": "OK"}


@app.get("/test_cookie")
def retrieve_cookie_value(date_until: str = Cookie(default=None)):
    if date_until is None:
        raise HTTPException(status_code=400, detail="date_until cookie not found")

    return {"date_until": date_until}


@app.get("/update")
def update_account(
    date_until: str = Query(
        ..., title="Date Until", description="Get data until this date"
    )
):
    try:
        datetime.strptime(date_until, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date format is not valid")
    try:
        tink = Tink(
            client_id=os.environ.get("TINK_CLIENT_ID"),
            client_secret=os.environ.get("TINK_CLIENT_SECRET"),
            redirect_uri=os.environ.get("TINK_CALLBACK_URI"),
            storage=TokenStorage(),
        )
        transactions = tink.transactions().get()
    except NoAuthorizationCodeException:
        link = tink.get_authorization_code_link()
    response = RedirectResponse(url=tink.get_authorization_code_link())
    response.set_cookie(key="date_until", value=date_until)
    return response
