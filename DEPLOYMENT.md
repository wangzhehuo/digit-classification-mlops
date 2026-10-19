# Deployment Guide

## Verified Local Container Setup

The API has been tested locally in Docker with a model directory mounted read-only.

This setup requires Docker, DVC with Azure support, and authenticated access to the configured Azure remote. The original local MLflow database is not required when retrieving the model through DVC. Automated staging and production delivery remain to be configured.

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

The selected model directory is tracked with DVC and stored in the configured Azure remote.

- DVC pointer: `model-export.dvc`
- Model directory hash: `58e12a972fd9f3b000b2e5dfbcfe44eb.dir`
- Exported files: 6

On a machine with DVC Azure support installed and Azure authentication configured, run from the repository root:

```bash
dvc pull model-export.dvc
```

This retrieves the model version referenced by the checked-out Git commit. The original local MLflow database is not required for this download.

Confirm that `model-export` contains `MLmodel` and `model.skops`.

Git tracks the small `model-export.dvc` pointer. The model directory itself is excluded from Git and the Docker build context, and its contents are stored through DVC in Azure.

### Original MLflow Export

The model was originally exported from the local MLflow store using:

```bash
python -c "import mlflow; mlflow.set_tracking_uri('sqlite:///mlflow.db'); print(mlflow.artifacts.download_artifacts(artifact_uri='models:/m-b974534191434444a198ae3b33f0c4d2', dst_path='model-export'))"
```

This original export command requires the local MLflow database and artifacts. Other machines should use the DVC pull command above.

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

- Configure and verify Azure authentication and DVC model retrieval in automated environments.
- Configure staging and production GitHub environments and secrets.
- Add automated delivery stages triggered by merges to staging and main.
- Document and verify the complete commit, CI, staging, and production flow.
