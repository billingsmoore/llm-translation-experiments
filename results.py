import json
from pathlib import Path

data_path = Path("data") / "TM0876"
output_fn = data_path / "TM0876.tsv"
result_fn = "results.json"

assert output_fn.exists(), f"{output_fn} does not exist"

results = {}

with output_fn.open("r") as f:
    for i, segment_pair in enumerate(f.readlines()):
        print(segment_pair)
        bo_line, en_line = segment_pair.strip().split("\t")
        results[i] = {"source": bo_line, "target_gt": en_line}

json.dump(results, open(result_fn, "w"), ensure_ascii=False, indent=2)
