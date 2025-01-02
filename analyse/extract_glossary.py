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
                    }
                )


# Export to CSV


def export_to_csv(label):
    header = ["Word", "Translation", "Line", "Verse"]
    rows = []
    for word, translations in word_translations.items():
        data = translations[label]
        if len(data) > 1:
            for item in data:
                rows.append(
                    [
                        word,
                        item["translation"],
                        item["line"],
                        results[item["source"]]["source"],
                    ]
                )

    export_fn = config.reports_path / f"terms_with_multiple_translations_{label}.csv"
    with open(export_fn, "w") as file:
        writer = csv.writer(file)
        writer.writerow(header)  # write the header
        writer.writerows(rows)

    return export_fn


if __name__ == "__main__":
    label = "04_commentary_assisted"
    export_to_csv(label)
