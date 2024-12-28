import json
from difflib import SequenceMatcher as SM

import config

verses_en_fn = config.data_path / "chonjuk-en-better.txt"

results = json.load(open(config.results_fn, "r"))
verses_en = verses_en_fn.read_text().split("\n")
verses_en_nocase = [verse.strip().lower() for verse in verses_en]


counter = 0
for text_id in results:
    target_gt = results[text_id]["target_gt"]
    target_gt = target_gt.lower()
    if target_gt in verses_en_nocase:
        continue

    matched = False
    for i, verse_en in enumerate(verses_en_nocase):
        if SM(None, target_gt, verse_en).ratio() > 0.9:
            # results[text_id]["target_gt"] = verses_en[i]
            matched = True
            break

    if not matched:
        # print(target_gt)
        counter += 1

print(len(results), counter)
