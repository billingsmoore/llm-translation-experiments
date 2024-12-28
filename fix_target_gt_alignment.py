import json
from difflib import SequenceMatcher as SM

from tqdm import tqdm

import config

verses_en_fn = config.data_path / "chonjuk-en-better.txt"

results = json.load(open(config.results_fn, "r"))
verses_en = verses_en_fn.read_text().split("\n")
verses_en_nocase = [verse.strip().lower() for verse in verses_en]

skip_text_ids = [93, 214, 313, 447, 459, 615, 795, 828, 463, 8, 19]


counter = 0
for text_id in tqdm(results):
    if int(text_id) in skip_text_ids:
        continue
    target_gt = results[text_id]["target_gt"]
    if target_gt.lower() in verses_en_nocase:
        continue

    matched = False
    for i, verse_en in enumerate(verses_en_nocase):
        if SM(None, target_gt.lower(), verse_en).ratio() > 0.4:
            results[text_id]["target_gt"] = verses_en[i]
            print(text_id)
            print(verses_en[i])
            print(target_gt)
            matched = True
            break

    if not matched:
        # print(target_gt)
        counter += 1

print(len(results), counter)

json.dump(results, open(config.results_fn, "w"), indent=2, ensure_ascii=False)
