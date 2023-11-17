from .test_base import client


class TestApp:
    def test_endpoint(self, client):
        response = client.get(
            "/?code=my_token&credentialsId=my_credentials_id&credentials_id=my_credentials_id"
        )
        assert response.status_code == 200
        assert response.json() == {"Status": "OK"}
        # http://my.endpoint?
