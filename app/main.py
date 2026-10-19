import os
from contextlib import asynccontextmanager

import mlflow.sklearn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    pixels: list[float,] = Field(min_length=64, max_length=64)


class PredictionResponse(BaseModel):
    digit: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = None
    model_uri = os.getenv("MODEL_URI")

    if model_uri:
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        app.state.model = mlflow.sklearn.load_model(model_uri)

    yield

    app.state.model = None


app = FastAPI(
    title="Handwritten Digit Classification API",
    lifespan=lifespan,
)


@app.get("/health")
def health(request: Request):
    return {
        "status": "ok",
        "model_loaded": request.app.state.model is not None,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest, request: Request):
    import math

    if any(
        not math.isfinite(pixel) or not 0 <= pixel <= 16 for pixel in payload.pixels
    ):
        raise HTTPException(
            status_code=422,
            detail="Each pixel must be a finite number between 0 and 16.",
        )

    model = request.app.state.model

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Prediction model is not loaded.",
        )

    prediction = model.predict([payload.pixels])

    return PredictionResponse(digit=int(prediction[0]))
