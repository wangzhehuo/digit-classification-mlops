import csv
import subprocess

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def get_dvc_hash():
    with open("data/digits.csv.dvc") as file:
        for line in file:
            if line.strip().startswith("- md5:"):
                return line.split(":", 1)[1].strip()


def get_git_commit():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True,
    ).strip()


X_train = []
y_train = []
X_test = []
y_test = []

with open("data/digits.csv", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        features = [float(row[f"pixel_{i}"]) for i in range(64)]
        target = int(float(row["target"]))

        if row["split"] == "train":
            X_train.append(features)
            y_train.append(target)
        elif row["split"] == "test":
            X_test.append(features)
            y_test.append(target)
        else:
            raise ValueError(f"Invalid split value: {row['split']}")

if not X_train or not X_test:
    raise ValueError("Both training and test sets must contain samples.")

# Tuned model: change model parameters only.
n_estimators = 100
max_depth = None

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("RandomForest_Digits")

with mlflow.start_run(run_name="tuned_random_forest"):
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    mlflow.log_param("model_type", "tuned_random_forest")
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", str(max_depth))
    mlflow.log_param("dvc_data_hash", get_dvc_hash())
    mlflow.log_param("git_commit", get_git_commit())

    mlflow.log_metric("accuracy", accuracy)

    mlflow.sklearn.log_model(
        model,
        name="random_forest_model",
        skops_trusted_types=["sklearn.tree._tree.Tree"],
    )

    print("Training samples:", len(X_train))
    print("Test samples:", len(X_test))
    print("Tuned accuracy:", accuracy)
