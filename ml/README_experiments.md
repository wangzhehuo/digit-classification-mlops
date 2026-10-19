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

## Update: Training with the Versioned Split

Both training scripts now read the `split` column from the versioned dataset directly, rather than generating the split during training.

The training and test sets contain 1437 and 360 samples respectively. The Random Forest `random_state` remains 42, and each model retains its previous hyperparameters.

### Verified Results

| Experiment | n_estimators | max_depth | Test accuracy | Test accuracy (%) |
| --- | --- | --- | --- | --- |
| Baseline using the stored split | 20 | 5 | 0.9222222222222223 | 92.22% |
| Tuned using the stored split | 100 | None | 0.975 | 97.50% |

Both experiments were rerun after committing the updated training scripts.

- Git SHA for both runs: `a2e388537ef541410bd5c6c2c48ab1e3ccd390e8`
- DVC dataset hash: `8ed2c517d6dc8a4bf862b950bc73a50f`

The dataset split membership is unchanged. However, the updated scripts load samples in CSV row order, whereas the previous scripts used the order returned by `train_test_split`. Training sample order can affect Random Forest results even with a fixed random state. The earlier results remain historical observations.

### Updated Production Candidate

This section supersedes the earlier production-candidate selection. The tuned model using the stored split is the current production candidate, with test accuracy of **97.50%**, approximately **5.28 percentage points** above the corresponding baseline.

Accuracy remains the chosen metric because it measures the proportion of handwritten digits classified correctly.

The selection remains provisional. Cross-validation or independent evaluation, per-class metrics, representative application inputs, and inference performance still need validation before production use.
