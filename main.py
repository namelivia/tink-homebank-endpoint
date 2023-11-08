import os
from storage.storage import TokenStorage
from tink_http_python.tink import Tink

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    storage = TokenStorage()
    storage.store_new_refresh_token_refresh_token("test")
    tink = Tink(
        client_id=os.environ.get("TINK_CLIENT_ID"),
        client_secret=os.environ.get("TINK_CLIENT_SECRET"),
        storage=TokenStorage(),
    )
    return {"Client": tink}
