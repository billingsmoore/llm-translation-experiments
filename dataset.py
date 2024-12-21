import re
from pathlib import Path

data_path = Path("data") / "TM0876"
bo_text_fn = data_path / "TM0876-bo.txt"
en_text_fn = data_path / "TM0876-en.txt"

assert bo_text_fn.is_file()
assert en_text_fn.is_file()

bo_lines = bo_text_fn.read_text().strip().split("\n")
en_lines = en_text_fn.read_text().strip().split("\n")

assert len(bo_lines) == len(en_lines)


def clean_en_text(text):
    text = re.sub(r"\d", "", text)
    return text.strip()


output_fn = data_path / "TM0876.tsv"
with output_fn.open("w") as f:
    for bo_line, en_line in zip(bo_lines, en_lines):
        if not bo_line.strip() or not en_line.strip():
            continue
        en_line = clean_en_text(en_line)
        f.write(f"{bo_line}\t{en_line}\n")
