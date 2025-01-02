import csv
import json

import config

results = json.load(open(config.results_fn, "r"))
headers = ["Source", "target_gt"] + list(results["1"]["target_pred"].keys())

rows = []
for _, data in results.items():
    row = [data["source"], data["target_gt"]]
    for exp_name in headers[2:]:
        if exp_name in data["target_pred"]:
            translation = data["target_pred"][exp_name]["translation"]
            # translation = translation.replace("\n", " ")
            row.append(translation)
        else:
            row.append("")
    rows.append(row)

output_fn = config.reports_path / "translations.csv"
with open(output_fn, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)
