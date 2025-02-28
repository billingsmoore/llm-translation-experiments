import json
from pathlib import Path

data_path = Path("data") / "chonjuk"
align_fn = data_path / "chonjuk_trans_align_better_with_commentary.tsv"
result_fn = "results.json"

# assert align_fn.exists()

# results = {}

# for i, segment_pair in enumerate(align_fn.read_text().splitlines()):
#     # skip header
#     if i == 0:
#         continue

#     parts = segment_pair.split("\t")
#     if len(parts) == 2:
#         bo_line, en_line = parts
#         commentry_1, commentry_2 = "", ""
#     elif len(parts) == 3:
#         bo_line, en_line, commentry_1 = parts
#         commentry_2 = ""
#     else:
#         bo_line, en_line, commentry_1, commentry_2 = parts
#     results[i] = {
#         "source": bo_line,
#         "target_gt": en_line,
#         "commentary_1": commentry_1,
#         "commentary_2": commentry_2,
#     }

# json.dump(results, open(result_fn, "w"), ensure_ascii=False, indent=2)

## Delete exp glossary
exp_name = "06_glossary_assisted"
results = json.load(open(result_fn, "r"))
for text_id, data in results.items():
    if "glossary" in data and exp_name in data["glossary"]:
        del data["glossary"][exp_name]

    if "target_pred" in data and exp_name in data["target_pred"]:
        del data["target_pred"][exp_name]
json.dump(results, open(result_fn, "w"), ensure_ascii=False, indent=2)
