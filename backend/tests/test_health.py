from fastapi.testclient import TestClient

from tests.test_base import TestBase


class TestHealth(TestBase):
    def test_health_endpoint(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
