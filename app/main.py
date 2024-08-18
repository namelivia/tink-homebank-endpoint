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
from jinja2 import Template

logger.setLevel(logging.DEBUG)

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
    account_id: str = Cookie(default=None),
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
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTPError: {e}")
        logger.error(f"Response: {e.response.json()}")
        logger.error(f"Request data: {e.request.body}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if date_until is None:
        raise HTTPException(status_code=400, detail="date_until cookie not found")

    if account_id is None:
        raise HTTPException(status_code=400, detail="account_id cookie not found")

    below_target_date = False
    page_token = None
    # Generate CSV
    current_timestamp = int(time.time())
    csv_path = os.environ.get("CSV_PATH")
    file_name = f"{csv_path}/output_{current_timestamp}.csv"
    # For debuggin purposes, log all fields from the first transaction
    logger.info("First transaction:")
    logger.info(transactions.transactions[0].__dict__)
    summary = []
    with open(file_name, "w") as f:
        writer = csv.writer(f, delimiter=";")
        while not below_target_date:
            for transaction in transactions.transactions:
                if not below_target_date:
                    transaction_date = transaction.dates.booked
                    below_target_date = transaction_date < date_until
                    if below_target_date:
                        logger.info("Transaction dates below target date, stopping")
                    else:
                        writer.writerow(
                            (
                                account_id,
                                transaction_date,
                                transaction.descriptions.original,
                                transaction.identifiers.provider_transaction_id,
                                Transactions.calculate_real_amount(
                                    transaction.amount.value
                                ),
                                transaction.id,
                            )
                        )
                        summary.append(
                            {
                                "date": transaction_date,
                                "description": transaction.descriptions.original,
                                "amount": Transactions.calculate_real_amount(
                                    transaction.amount.value
                                ),
                            }
                        )
            if not below_target_date:
                logger.info("Transaction dates above target date, continuing")
                next_page_token = transactions.next_page_token
                transactions = tink.transactions().get(pageToken=next_page_token)
    configuration_file_name = f"{csv_path}/output_{current_timestamp}.json"
    configuration_template_file_name = "templates/importer_configuration.json"
    with open(configuration_template_file_name, "r") as template_file:
        template_content = template_file.read()
    template = Template(template_content)
    rendered_configuration = template.render(
        {
            "default_account_id": account_id,
        }
    )
    with open(configuration_file_name, "w") as configuration_file:
        configuration_file.write(rendered_configuration)
    return {"Status": "OK", "Summary": summary}


@app.get("/update")
def update_account(
    date_until: str = Query(
        ..., title="Date Until", description="Get data until this date"
    ),
    account_id: str = Query(
        ..., title="Account id", description="Id for the account to update"
    ),
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
    response.set_cookie(key="account_id", value=account_id)
    return response
