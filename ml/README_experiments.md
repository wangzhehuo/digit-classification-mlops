# Experiment Summary

## Objective and Evaluation Metric

The objective is to classify handwritten digits correctly using a Random Forest classifier.

The chosen metric is **accuracy**, defined as the number of correct predictions divided by the total number of predictions. It directly measures how often the model predicts the correct digit, making it an understandable measure of performance for this classification task. Accuracy treats each incorrect prediction equally; per-class performance should also be checked before production use.

## Experiment Setup

Both experiments used the same dataset version and train/test split:

- Training samples: **1437**
- Test samples: **360**
- Train/test split random state: **42**
- Random Forest random state: **42**
- DVC dataset hash: `8ed2c517d6dc8a4bf862b950bc73a50f`

Using the same data and split makes the results directly comparable.

## Results

| Experiment | n_estimators | max_depth | Test accuracy | Test accuracy (%) |
| --- | --- | --- | --- | --- |
| Baseline | 20 | 5 | 0.9388888888888889 | 93.89% |
| Tuned | 100 | None | 0.9722222222222222 | 97.22% |

`max_depth=None` means that no explicit maximum tree depth was set.

The tuned model improved test accuracy by approximately **3.33 percentage points** compared with the baseline.

## Code and Data Provenance

| Experiment | Recorded Git SHA | DVC dataset hash |
| --- | --- | --- |
| Baseline | `7a6cb426182fe5e0ae0e5833d1fc4fb909a16973` | `8ed2c517d6dc8a4bf862b950bc73a50f` |
| Tuned | `f038bd23fb4ffbd9ac605c8f702c0d2fa63c36e5` | `8ed2c517d6dc8a4bf862b950bc73a50f` |

The training scripts use MLflow to log hyperparameters, accuracy, the Git commit SHA, the DVC dataset hash, and the trained model.

## Current Production Candidate

The **tuned Random Forest** is the current production candidate because it achieved higher accuracy on the same test set using the same dataset version.

This is a provisional selection, not confirmation that the model is ready for production. The comparison is based on a single train/test split. Before promotion, further validation should include:

- Cross-validation or an additional independent evaluation dataset.
- A confusion matrix and per-class precision, recall, and F1 scores.
- Evaluation on representative inputs from the application.
- Inference latency, model size, and application integration checks.

These checks are proposed next steps; their results are not established by the experiments reported here.
