import os
from dotenv import load_dotenv
from app.notifications.notifications import Notifications
import requests

load_dotenv()


def main():
    # Will send a notification to update each account
    headers = {
        "accept": "application/vnd.api+json",
        "Authorization": "Bearer " + os.getenv("FIREFLY_PERSONAL_ACCESS_TOKEN"),
        "Content-Type": "application/json",
    }
    firefly_url = os.getenv("FIREFLY_URL")
    account_request = requests.get(f"{firefly_url}/api/v1/accounts", headers=headers)
    accounts = account_request.json()["data"]
    accounts = list(
        filter(lambda account: account["attributes"]["type"] == "asset", accounts)
    )
    app_url = os.getenv("APP_URL")
    for account in accounts:
        account_id = account["id"]
        transactions_request = requests.get(
            f"{firefly_url}/api/v1/accounts/{account_id}/transactions?limit=1",
            headers=headers,
        )
        transactions = transactions_request.json()["data"]
        if len(transactions) == 0:
            raise Exception("No transactions for account {account_id}")
        last_transaction_date = transactions[0]["attributes"]["created_at"].split("T")[
            0
        ]
        link = f"{app_url}/update?date_until={date_until}&account_id={account['id']}"
        Notifications.send(f"{account['attributes']['name']}: {link}")


if __name__ == "__main__":
    main()
