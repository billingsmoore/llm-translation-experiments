import json
from pathlib import Path

trans_fn = (
    Path(__file__).parent.parent.parent
    / "data"
    / "chonjuk"
    / "chonjuk_trans_align_better_with_commentary.tsv"
)

data_path = Path(__file__).parent / "data"

# Load the translations
translations = trans_fn.read_text().strip().split("\n")


def filter_tarns_with_term(translations, term):
    """Filter translations with terms."""
    filtered_translations = []
    for translation in translations:
        source, target, *commentaries = translation.split("\t")
        if term in source:
            filtered_translations.append(
                {
                    "bo": source,
                    "en": target,
                    "commentaries": commentaries,
                    "sanskrit": "",
                }
            )
    return filtered_translations


def main():
    tibetan_terms = [
        "བྱང་ཆུབ་སེམས་",
        "སྡུག་བསྔལ་",
        "ཤེས་རབ་",
        "སྙིང་རྗེ་",
        "བླ་མ་",
        "སངས་རྒྱས་",
        "ཆོས་",
        "དགེ་འདུན་",
        "སྟོང་པ་ཉིད་",
        "དགེ་བ་",
        "སྡིག་པ་",
        "འཁོར་བ་",
        "མྱ་ངན་ལས་འདས་པ་",
        "བསམ་གཏན་",
        "ཕ་རོལ་ཏུ་ཕྱིན་པ་",
        "དབུ་མ་",
        "ཀུན་རྫོབ་",
        "དོན་དམ་",
        "རྟེན་འབྲེལ་",
        "བདག་མེད་",
    ]
    for term in tibetan_terms:
        filtered_translations = filter_tarns_with_term(translations, term)
        output_fn = data_path / f"{term}.json"
        print(len(filtered_translations))
        if len(filtered_translations) >= 10:
            json.dump(filtered_translations, output_fn.open("w"), ensure_ascii=False)
            print(f"Save translations for {term} at {output_fn}.")
        else:
            print(f"Not enough translations found for {term}.")


if __name__ == "__main__":
    main()
