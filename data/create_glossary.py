import json
from pathlib import Path

glossary_tsv_path = Path(__file__).parent / "chonjuk" / "glossary.tsv"
glossary_json_path = Path(__file__).parent / "chonjuk" / "glossary.json"

glossary = glossary_tsv_path.read_text().split("\n")
glossary = [line.split("\t") for line in glossary if line.strip()]


def is_found_in_glossary_dict(glossary_dict, bo_term, en_trans):
    if bo_term not in glossary_dict:
        return False
    for item in glossary_dict[bo_term]:
        if item[0] == en_trans:
            return True
    return False


glossary_dict = {}
for line in glossary:
    bo_term, en_trans, en_definition = line
    bo_term = bo_term if bo_term.endswith("་") else bo_term + "་"
    print(bo_term)
    en_trans = en_trans.capitalize()
    if bo_term not in glossary_dict:
        glossary_dict[bo_term] = []
    if not is_found_in_glossary_dict(glossary_dict, bo_term, en_trans):
        glossary_dict[bo_term].append((en_trans, en_definition))

json.dump(glossary_dict, open(glossary_json_path, "w"), indent=2, ensure_ascii=False)
