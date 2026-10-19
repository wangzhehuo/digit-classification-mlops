import csv
from pathlib import Path

from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

data = load_digits()

indices = list(range(len(data.data)))

train_indices, test_indices = train_test_split(
    indices,
    test_size=0.2,
    random_state=42,
)

train_indices = set(train_indices)
test_indices = set(test_indices)

output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

output_path = output_dir / "digits.csv"

with output_path.open("w", newline="") as file:
    writer = csv.writer(file)

    header = [f"pixel_{i}" for i in range(data.data.shape[1])]
    header.extend(["target", "split"])
    writer.writerow(header)

    for index, (features, target) in enumerate(zip(data.data, data.target)):
        if index in train_indices:
            split = "train"
        else:
            split = "test"

        writer.writerow([*features, target, split])

print("Dataset saved to:", output_path)
print("Dataset shape:", (len(data.data), data.data.shape[1] + 2))
print("Training samples:", len(train_indices))
print("Test samples:", len(test_indices))
