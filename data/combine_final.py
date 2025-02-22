import csv
import json
from collections import OrderedDict
from pathlib import Path

data_path = Path(__file__).parent / "chonjuk"

commentaries_fn = data_path / "commentaries.json"
commentaries = json.loads(commentaries_fn.read_text())


def get_commentaries(bo_text, commentaries):
    """Get commentaries for a given segment."""
    segment_commentaries = ("", "")
    for segment in commentaries:
        if segment["root_segment"] == bo_text:
            segment_commentaries = segment["commentary_1"], segment["commentary_2"]

    if segment_commentaries == ("", ""):
        print(f"No commentaries found for {bo_text}")

    return segment_commentaries


en_aligned_better_fn = data_path / "chonjuk_trans_align_better.tsv"
en_aligned_fn = data_path / "chonjuk_trans_align_new.tsv"
sanskrit_aligned_fn = data_path / "sanskrit" / "aligned.tsv"


def load_translation(fn):
    """Load translation from file."""
    translation = []
    with open(fn) as file:
        reader = csv.reader(file, delimiter="\t")
        for row in reader:
            bo, en = row
            translation.append((bo.strip(), en.strip()))
    return translation


def load_sanskrit(fn):
    """Load translation from file."""
    sanskrit = []
    with open(fn) as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)
        for row in reader:
            if len(row) == 3:
                _, bo, sa = row

            elif len(row) == 2:
                _, bo = row
                sa = ""
            else:  # Skip invalid rows
                continue
            sanskrit.append((bo.strip(), sa.strip()))
    return sanskrit


en_aligned_better = load_translation(en_aligned_better_fn)
en_aligned = load_translation(en_aligned_fn)
sanskrit_aligned = load_sanskrit(sanskrit_aligned_fn)

print("sanskrit", len(sanskrit_aligned))
print("en_aligned", len(en_aligned))
print("en_aligned_better", len(en_aligned_better))


def get_translation(bo_text, translations):
    """Get translation for a given text."""
    for bo, en in translations:
        if bo == bo_text:
            return en
    return ""


# combine translations
combined_data = []

for bo, sk in sanskrit_aligned:
    segment_commentaries = get_commentaries(bo, commentaries)
    combined_data.append(
        {
            "bo": bo,
            "sa": sk,
            "en_1": get_translation(bo, en_aligned_better),
            "en_2": get_translation(bo, en_aligned),
            "com_1": segment_commentaries[0],
            "com_2": segment_commentaries[1],
        }
    )

combined_data_fn = data_path / "combined_data.json"
json.dump(combined_data, combined_data_fn.open("w"), ensure_ascii=False, indent=2)
