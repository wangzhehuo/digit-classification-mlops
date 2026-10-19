
# Handwritten Digit Classification App

A handwritten digit classification API developed as a DevOps and MLOps course project.

## Team

- Wang Zhe
- Zhan Jinhao

## Application

The application uses FastAPI and a trained Random Forest classifier to predict digits from 8 × 8 images.

Each prediction request contains 64 pixel values between 0 and 16.

Endpoints:

- `GET /health`: reports service health and whether a model is loaded.
- `POST /predict`: returns the predicted digit.
- `GET /docs`: interactive API documentation.

Invalid input returns HTTP 422. A valid prediction request returns HTTP 503 when no model is loaded.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `app/main.py` | API, input validation, and model loading |
| `tests/test_api.py` | Automated API tests |
| `ml/data_pipeline.py` | Dataset export and stored train/test split |
| `ml/train.py` | Baseline training with MLflow logging |
| `ml/train_tuned.py` | Tuned training with MLflow logging |
| `ml/README_data.md` | Dataset source and version history |
| `ml/README_experiments.md` | Experiment results and candidate selection |
| `data/digits.csv.dvc` | DVC dataset pointer |
| `model-export.dvc` | DVC selected-model pointer |
| `Dockerfile` | Container image definition |
| `.github/workflows/ci.yml` | Pull request and branch CI |
| `.github/workflows/delivery.yml` | Environment-specific build and verification |
| `DEPLOYMENT.md` | Model retrieval and container instructions |

## Local Setup

Use Python 3.12 and run commands from the repository root.

For Windows Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

To retrieve versioned data and models, install DVC with Azure support:

```bash
python -m pip install "dvc[azure]==3.67.1"
```

Azure authentication must be configured separately. Never commit credentials.

## Retrieve the Selected Model

With authenticated access to the configured Azure remote:

```bash
dvc pull model-export.dvc
```

The original local MLflow database is not required to retrieve the DVC-tracked model.

## Run the API Locally

In Windows Git Bash:

```bash
export MODEL_URI="$PWD/model-export"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:

- Health: http://127.0.0.1:8000/health
- API documentation: http://127.0.0.1:8000/docs

With the model loaded, the health response includes `"model_loaded": true`.

See [DEPLOYMENT.md](DEPLOYMENT.md) for Docker build and run instructions.

## Quality Checks

```bash
python -m ruff check app ml tests
python -m ruff format --check app ml tests
python -m pytest -q
```

The current suite contains 15 passing test cases covering:

- Health responses with and without a loaded model.
- Valid prediction requests, pixel boundaries, and forwarding to the model.
- Missing, malformed, incorrectly sized, and out-of-range inputs.
- Prediction requests when no model is loaded.

Automated API tests use a simulated model. Separate manual and delivery checks verified loading the selected real model and predicting a sample digit.

A test-client dependency deprecation warning was observed during local testing; it did not cause test failures.

## Data and Experiments

The project uses the scikit-learn handwritten digits dataset.

Two dataset versions are documented:

- v1: the original exported dataset.
- v2: the dataset with a stored, reproducible train/test split.

Training uses 1437 samples and evaluation uses 360 samples. Both training scripts read the versioned `split` column.

DVC stores dataset and model contents in Azure. Git tracks their small pointer files.

MLflow training runs log model hyperparameters, accuracy, Git commit SHA, DVC dataset hash, and trained models.

The latest verified comparison using the stored split is:

| Model | n_estimators | max_depth | Test accuracy |
| --- | --- | --- | --- |
| Baseline | 20 | 5 | 0.9222222222222223 |
| Tuned | 100 | None | 0.975 |

The tuned model is the current provisional production candidate. Accuracy measures the proportion of correctly classified digits. Further validation is required before real production use.

See [dataset documentation](ml/README_data.md) and [experiment documentation](ml/README_experiments.md) for details.

## Branching and CI

Changes follow this merge path:

```text
feature or fix branch → dev → staging → main
```

The dev, staging, and main branches require pull requests and passing status checks. Branch protection also requires the branch to be up to date and prevents administrators from bypassing the configured rules.

CI runs on:

- Pull requests targeting dev, staging, or main.
- Pushes to dev, staging, main, and the explicitly configured feature/docker-ci branch.
- Manual dispatch.

The required CI job, `Lint, tests and Docker build`, checks code, checks formatting, runs the full test suite, and builds the Docker image.

## Environment Delivery

After a merge updates staging or main, a separate delivery workflow runs:

| Branch | GitHub environment | APP_ENV |
| --- | --- | --- |
| staging | staging | staging |
| main | production | production |

Each environment provides these secrets:

- `APP_ENV`
- `AZURE_STORAGE_ACCOUNT`
- `AZURE_STORAGE_SAS_TOKEN`

The workflow:

1. Checks out the code and installs dependencies.
2. Runs linting, formatting checks, and tests.
3. Generates a temporary `.env` file from the environment configuration.
4. Downloads the selected model from Azure using DVC.
5. Builds a Docker image tagged with the environment and Git SHA.
6. Starts a temporary container with the model mounted read-only.
7. Verifies model loading and a sample prediction.
8. Removes the container and temporary credential configuration.

The full PR and CI path through staging and main has been exercised. Both staging and production delivery runs passed.

Delivery currently builds and verifies images on the GitHub runner. It does not publish images to a registry or maintain a publicly hosted service.

## Current Limitations

- Candidate selection is based on the recorded train/test evaluation; broader model validation remains pending.
- Azure access requires valid credentials with suitable permissions.
- Model retrieval and container startup must succeed for environment delivery to pass.
- A successful environment build and sample prediction do not establish readiness for real production traffic.
