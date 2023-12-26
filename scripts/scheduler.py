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
    r = requests.get(f"{firefly_url}/api/v1/accounts", headers=headers)
    accounts = r.json()["data"]
    accounts = list(
        filter(lambda account: account["attributes"]["type"] == "asset", accounts)
    )
    app_url = os.getenv("APP_URL")
    for account in accounts:
        date_until = account["attributes"]["current_balance_date"].split("T")[0]
        link = f"{app_url}/update?date_until={date_until}&account_id={account['id']}"
        Notifications.send(f"{account['attributes']['name']}: {link}")


if __name__ == "__main__":
    main()
