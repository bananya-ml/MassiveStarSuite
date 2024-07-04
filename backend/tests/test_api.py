from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_predict_id():
    response = client.post(
        "/predict/id",
        json={"source_id": "4111834567779557376"}
    )
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_predict_coordinates():
    response = client.post(
        "/predict/coordinates",
        json={"ra": 256.5229102004341, "dec": -26.580565130784702}
    )
    assert response.status_code == 200
    assert "prediction" in response.json()

if __name__ == "__main__":
    test_predict_id()
    test_predict_coordinates()
    print("All tests passed!")