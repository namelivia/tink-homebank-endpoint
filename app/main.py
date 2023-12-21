import os
import csv
import time
from app.storage.storage import TokenStorage
from tink_http_python.tink import Tink
from tink_http_python.exceptions import NoAuthorizationCodeException
from tink_http_python.transactions import Transactions

from fastapi import FastAPI, Query
from fastapi.logger import logger
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
        return {"Status": "ERROR"}

    # Hardcoded target date for now in Y-m-d format
    target_date = "2022-10-01"
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
                transaction_date = transaction.dates.booked
                below_target_date = transaction_date < target_date
                category = "pending"
                memo = "pending"
                writer.writerow(
                    (
                        transaction_date,
                        transaction.descriptions.original,
                        memo,
                        Transactions.calculate_real_amount(transaction.amount.value),
                        category,
                    )
                )
            if below_target_date:
                logger.info("Transaction dates below target date, stopping")
            else:
                logger.info("Transaction dates above target date, continuing")
                next_page_token = transactions.next_page_token
                transactions = tink.transactions().get(pageToken=next_page_token)
    configuration_file_name = f"{csv_path}/output_{current_timestamp}.json"
    configuration_template_file_name = "templates/importer_configuration.json"
    copyfile(configuration_template_file_name, configuration_file_name)
    return {"Status": "OK"}
