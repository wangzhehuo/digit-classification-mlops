import pytest
from fastapi.testclient import TestClient

from app.main import app


class FakeModel:
    def __init__(self, digit=0):
        self.digit = digit
        self.received = None

    def predict(self, samples):
        self.received = samples
        return [self.digit]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("MODEL_URI", raising=False)

    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.parametrize("loaded", [False, True])
def test_health(client, loaded):
    app.state.model = FakeModel() if loaded else None

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model_loaded": loaded,
    }


@pytest.mark.parametrize(
    "pixels, digit",
    [
        ([0] * 64, 0),
        ([16] * 64, 9),
        ([0.5, 15.5] * 32, 4),
    ],
)
def test_predict_valid_input(client, pixels, digit):
    model = FakeModel(digit)
    app.state.model = model

    response = client.post("/predict", json={"pixels": pixels})

    assert response.status_code == 200
    assert response.json() == {"digit": digit}
    assert model.received == [pixels]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"pixels": None},
        {"pixels": []},
        {"pixels": [0] * 63},
        {"pixels": [0] * 65},
        {"pixels": [-1] + [0] * 63},
        {"pixels": [17] + [0] * 63},
        {"pixels": ["invalid"] + [0] * 63},
    ],
)
def test_predict_rejects_invalid_input(client, payload):
    model = FakeModel()
    app.state.model = model

    response = client.post("/predict", json=payload)

    assert response.status_code == 422
    assert model.received is None


@pytest.mark.parametrize("pixel", [0, 16])
def test_predict_without_model(client, pixel):
    response = client.post(
        "/predict",
        json={"pixels": [pixel] * 64},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Prediction model is not loaded.",
    }
