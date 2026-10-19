# Deployment Guide

## Verified Local Container Setup

The API has been tested locally in Docker with a model directory mounted read-only.

This setup requires Docker and access to the local MLflow tracking database and model artifacts. Automated staging and production delivery remain to be configured.

## Current Model Candidate

- Model: tuned Random Forest
- `n_estimators`: 100
- `max_depth`: None
- Model random state: 42
- Test accuracy: 0.975
- Training samples: 1437
- Test samples: 360
- Training code Git SHA: `a2e388537ef541410bd5c6c2c48ab1e3ccd390e8`
- DVC dataset hash: `8ed2c517d6dc8a4bf862b950bc73a50f`
- MLflow run ID: `73abd0e6e3a24639a708f5ce4a5e5380`
- MLflow model URI: `models:/m-b974534191434444a198ae3b33f0c4d2`
- Serialization format: skops

This model remains a provisional production candidate pending further validation.

## Prepare the Model

Run the following from the repository root in the project's Python environment:

```bash
python -m pip install -r requirements.txt
```

Download the model from the local MLflow store:

```bash
python -c "import mlflow; mlflow.set_tracking_uri('sqlite:///mlflow.db'); print(mlflow.artifacts.download_artifacts(artifact_uri='models:/m-b974534191434444a198ae3b33f0c4d2', dst_path='model-export'))"
```

Confirm that `model-export` contains `MLmodel` and `model.skops`.

This command requires the original local MLflow database and artifacts. A fresh Git clone alone does not include them. Portable model distribution for other machines and automated environments remains to be configured.

The exported model directory is excluded from Git and the Docker build context.

## Build the Image

```bash
docker build -t digit-classification-mlops:dev .
```

The image installs the runtime dependencies and runs the API as a non-root user. The model is supplied at runtime rather than included in the image.

## Run with the Model

From the repository root in Windows Git Bash:

```bash
MSYS_NO_PATHCONV=1 docker run --rm \
  -p 127.0.0.1:8001:8000 \
  --mount "type=bind,source=$(pwd -W)/model-export,target=/models/digits,readonly" \
  -e MODEL_URI=/models/digits \
  digit-classification-mlops:dev
```

The model directory is mounted read-only. Loading this local directory does not require the host MLflow database inside the container.

Stop the container with Ctrl+C.

## Verify the API

Open:

- Health endpoint: http://127.0.0.1:8001/health
- Interactive API documentation: http://127.0.0.1:8001/docs

With the model loaded, the health endpoint returns:

```json
{"status":"ok","model_loaded":true}
```

The `/predict` endpoint accepts a JSON object containing `pixels`: a list of 64 numeric values between 0 and 16.

Verified manual checks:

- The container started and reported `model_loaded: true`.
- A prediction request returned HTTP 200 with `{"digit": 0}` for the tested digit sample.

If MODEL_URI is not set, the service starts without a model. The health response reports `model_loaded: false`, and valid prediction requests return HTTP 503.

## Remaining Delivery Work

- Configure portable access to the selected model artifact.
- Configure staging and production GitHub environments and secrets.
- Add automated delivery stages triggered by merges to staging and main.
- Document and verify the complete commit, CI, staging, and production flow.
