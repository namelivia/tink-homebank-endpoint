from .test_base import client
from mock import patch, Mock


class TestApp:
    @patch("app.main.Tink.transactions")
    def test_endpoint(self, m_transactions, client):
        m_transactions.get.return_value = []
        response = client.get(
            "/?code=my_token&credentialsId=my_credentials_id&credentials_id=my_credentials_id"
        )
        assert response.status_code == 200
        assert response.json() == {"Status": "OK", "Transaction": {}}
        # http://my.endpoint?
