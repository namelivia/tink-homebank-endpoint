import os
from tink_http_python.tink import Tink
from tink_http_python.exceptions import NoAuthorizationCodeException
from app.storage.storage import TokenStorage
from dotenv import load_dotenv
from app.notifications.notifications import Notifications

load_dotenv()


def main():
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
        Notifications.send(link)


if __name__ == "__main__":
    main()
