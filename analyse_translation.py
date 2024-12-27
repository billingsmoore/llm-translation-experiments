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


label = "target_gt"
for word, translations in word_translations.items():
    data = translations[label]
    if len(data) > 1:
        print(f"  {label}:")
        for item in data:
            print(
                f"    - {word} {item['translation']} ({item['source']}, {item['line']})"
            )
