import csv
from pathlib import Path

from sklearn.datasets import load_digits


data = load_digits()

output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

output_path = output_dir / "digits.csv"

with output_path.open("w", newline="") as file:
    writer = csv.writer(file)

    header = [f"pixel_{i}" for i in range(data.data.shape[1])]
    header.append("target")
    writer.writerow(header)

    for features, target in zip(data.data, data.target):
        writer.writerow([*features, target])

print("Dataset saved to:", output_path)
print("Dataset shape:", (len(data.data), data.data.shape[1] + 1))
