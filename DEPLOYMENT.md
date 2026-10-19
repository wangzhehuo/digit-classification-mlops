# Deployment Guide

## Verified Local Container Setup

The API has been tested locally in Docker with a model directory mounted read-only.

This setup requires Docker, DVC with Azure support, and authenticated access to the configured Azure remote. The original local MLflow database is not required when retrieving the model through DVC. Automated staging and production build and verification workflows have both passed.

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

## Automated Environment Delivery

The delivery workflow is defined in `.github/workflows/delivery.yml`.

| Trigger | GitHub environment | Environment configuration |
| --- | --- | --- |
| Push to staging after a merge | staging | APP_ENV=staging |
| Push to main after a merge | production | APP_ENV=production |

The staging environment permits the staging branch. The production environment permits the main branch.

Each environment has its own secrets:

- `APP_ENV`
- `AZURE_STORAGE_ACCOUNT`
- `AZURE_STORAGE_SAS_TOKEN`

The workflow performs code checks and tests, creates a temporary `.env` file, retrieves the selected model from Azure using DVC, and builds an image tagged with the environment and commit SHA.

The `.env` file contains APP_ENV and the container model path. Azure credentials are used separately for DVC access and are not included in the image.

A temporary container starts with the downloaded model mounted read-only. The workflow waits for the health endpoint to report a loaded model, then checks a sample prediction. Connection errors during startup are retried. Container state and logs are collected if the workflow fails.

The container and temporary credential configuration are removed during cleanup.

## Verified Delivery Results

- Model retrieval succeeded in a separate local clone with an independent DVC cache.
- The retrieved model loaded successfully and predicted 0 for a sample whose target was 0.
- Staging delivery passed Azure retrieval, image building, model loading, and sample prediction.
- Production delivery passed the same workflow using the production environment.
- The feature → dev → staging → main pull request path and required CI checks were exercised.

The image is built and tested on the GitHub runner. It is not published to a registry, and the temporary verification container is not a persistent hosted service.

## Remaining Validation and Operational Work

- Evaluate the candidate with cross-validation or additional independent data.
- Inspect per-class metrics and representative application inputs.
- Assess inference latency and resource requirements.
- Maintain valid Azure credentials and update environment secrets when needed.
- If persistent hosting is required later, configure image publishing, deployment, and monitoring.
