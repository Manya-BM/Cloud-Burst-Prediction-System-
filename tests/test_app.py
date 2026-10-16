import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

client = app.test_client()
GOOD = {"MinTemp": 18, "MaxTemp": 28, "Humidity9am": 90, "Humidity3pm": 85,
        "Pressure3pm": 1002, "WindGustSpeed": 60, "Temp3pm": 24}

def test_pages():
    for url in ["/", "/dashboard", "/about"]:
        assert client.get(url).status_code == 200

def test_predict_valid():
    r = client.post("/api/predict", json=GOOD)
    assert r.status_code == 200 and r.get_json()["risk"] in ["Low", "Moderate", "High"]

def test_predict_invalid():
    r = client.post("/api/predict", json={**GOOD, "Humidity3pm": 500})
    assert r.status_code == 400 and "Humidity3pm" in r.get_json()["fields"]
