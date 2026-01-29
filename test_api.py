from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
#test1
def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert 'message' in response.json()
#test2
def test_predict_valid_input():
    response = client.get("/predict/delays",
                          params={"arrival_airport": "PDX",
                                  "local_dep_time": "17:30",
                                  "local_arr_time": "19:30"
                                  }
                          )

    assert response.status_code == 200
    assert 'average_dep_delay_min' in response.json()
#test3
def test_predict_invalid_input():
    response = client.get("/predict/delays",
                          params={"arrival_airport": "PDX344",
                                  "local_dep_time": "17:30",
                                  "local_arr_time": "19:30"
                                  }
                          )
    assert response.status_code == 404
    assert "Arrival airport not found" in response.json()["detail"]


