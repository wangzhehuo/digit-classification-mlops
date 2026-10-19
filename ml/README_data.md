# Dataset Documentation

## Dataset Source

This project uses the handwritten digits dataset provided by scikit-learn through `sklearn.datasets.load_digits`.

The dataset contains 1,797 samples. Each sample has 64 pixel features representing an 8 × 8 handwritten digit image, and one target label from 0 to 9.

The dataset is exported to:

`data/digits.csv`

The dataset file is tracked with DVC rather than Git. Git stores the corresponding `.dvc` pointer file, while the actual dataset is stored in the configured Azure DVC remote.

## Dataset Version 1

Git tag:

`dataset-v1`

Git commit:

`dd1cf9b`

Version 1 is the first usable dataset version.

It contains:

- 1,797 samples
- 64 pixel feature columns
- 1 target column
- 65 columns in total

The data is exported directly from `load_digits` without changing the samples or pixel values.

## Dataset Version 2

Git tag:

`dataset-v2`

Git commit:

`1135397`

Version 2 keeps all 1,797 samples and their original pixel values.

A `split` column is added to store a reproducible training and test split:

- Training samples: 1,437
- Test samples: 360
- Test size: 20%
- Random state: 42

Version 2 therefore contains 66 columns in total:

- 64 pixel feature columns
- 1 target column
- 1 split column

The purpose of this change is to make the exact train/test split part of the versioned dataset instead of creating a new split every time the model is trained.

## DVC Versioning

The dataset is tracked with DVC.

Git tracks:

`data/digits.csv.dvc`

The actual `data/digits.csv` file is excluded from Git and stored through the configured Azure DVC remote.

The two dataset versions can be identified by the Git tags `dataset-v1` and `dataset-v2`.
