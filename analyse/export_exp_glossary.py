import csv
import json
from collections import defaultdict

import config

results = json.load(open(config.results_fn, "r"))


def if_en_translation_exists(en_word, label_data):
    for item in label_data:
        if en_word == item["translation"]:
            return True
    return False


output_path = config.reports_path / "glossary_with_multi_translations"
output_path.mkdir(exist_ok=True)

word_translations = defaultdict(lambda: defaultdict(list))
for text_id, data in results.items():
    if "glossary" not in data:
        continue
    for label, glossary in data["glossary"].items():
        for line, line_glossary in glossary.items():
            for bo_word, en_word in line_glossary.items():
                if if_en_translation_exists(en_word, word_translations[bo_word][label]):
                    continue
                word_translations[bo_word][label].append(
                    {
                        "translation": en_word,
                        "source": text_id,
                        "line": line,
                        "label": label,
                    }
                )


# Export to CSV


def export_to_csv(label):
    header = ["Word", "Translation", "Context", "Source", "Source Translation"]
    rows = []
    for word, translations in word_translations.items():
        data = translations[label]
        if len(data) < 5:
            continue
        for item in data:
            if item["label"] == "target_gt":
                soruce_trans = results[item["source"]]["target_gt"]
            else:
                soruce_trans = results[item["source"]]["target_pred"][item["label"]][
                    "translation"
                ]

            rows.append(
                [
                    word,
                    item["translation"],
                    item["line"],
                    results[item["source"]]["source"],
                    soruce_trans,
                ]
            )

    export_fn = output_path / f"{label}.csv"
    with open(export_fn, "w") as file:
        writer = csv.writer(file)
        writer.writerow(header)  # write the header
        writer.writerows(rows)

    return export_fn


if __name__ == "__main__":
    labels = results["1"]["glossary"].keys()
    for label in labels:
        export_to_csv(label)
