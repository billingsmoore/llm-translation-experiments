import csv
import json
from collections import defaultdict

import config

results = json.load(open(config.results_fn, "r"))
labels = results["1"]["glossary"].keys()


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


glossary_multiple_terms_counts = []
for word, translations in word_translations.items():
    glossary_line = {"word": word}
    for label in labels:
        if label == "target_gt" and len(translations[label]) <= 2:
            break
        glossary_line[label] = len(translations[label])

    if len(glossary_line) > 1:
        glossary_multiple_terms_counts.append(glossary_line)

# Total counts by label
total_counts = defaultdict(int)
for line in glossary_multiple_terms_counts:
    for label in labels:
        if label in line:
            total_counts[label] += line[label]

print("Total counts by label:")
print(total_counts)


# Export to CSV
export_fn = config.reports_path / "glossary_multiple_terms_counts.csv"
with open(export_fn, "w", newline="") as file:
    fieldnames = glossary_multiple_terms_counts[0].keys()
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(glossary_multiple_terms_counts)
