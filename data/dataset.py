import re
from collections import deque
from pathlib import Path

data_path = Path(__file__).parent / "chonjuk"
bo_text_fn = data_path / "chonjuk-bo.txt"
en_text_fn = data_path / "chonjuk-en.txt"
root_stanzas_fn = data_path / "chonjuk_root_stanzas.txt"

assert bo_text_fn.is_file()
assert en_text_fn.is_file()
assert root_stanzas_fn.is_file()

bo_lines = bo_text_fn.read_text().strip().split("\n")
en_lines = en_text_fn.read_text().strip().split("\n")
root_stanzas = root_stanzas_fn.read_text().replace("\ufeff", "").strip().split("\n")

assert len(bo_lines) == len(en_lines)
assert len(root_stanzas)

print(len(bo_lines), len(en_lines), len(root_stanzas))


def clean_en_text(text):
    text = re.sub(r"\d", "", text)
    return text.strip()


alignment_in_stanza = []

bo_line_start = 0
n_parts_per_root_stanza = [
    len(root_stanza.replace("།", "").strip().split()) for root_stanza in root_stanzas
]

for i, line in enumerate(bo_lines, 1):
    parts = line.replace("།", "").strip().split()
    if len(parts) > 4:
        print(i, len(parts), line)

exit()

for n_parts in n_parts_per_root_stanza:
    bo_stanza = ""
    en_stanza = ""
    n_parts_collected = 0
    for i in range(bo_line_start, len(bo_lines)):
        bo_line = bo_lines[i]
        en_line = en_lines[i]
        if not bo_line.strip() or not en_line.strip():
            continue
        n_parts_collected += len(bo_line.split())
        en_stanza += clean_en_text(en_line) + " "
        bo_stanza += bo_line + " "
        bo_line_start += 1
        if n_parts_collected == n_parts:
            break

    if bo_stanza and en_stanza:
        alignment_in_stanza.append((bo_stanza.strip(), en_stanza.strip()))

print(len(alignment_in_stanza))


output_fn = data_path / "chonjuk_stanza_translation.tsv"
with output_fn.open("w") as f:
    for bo_line, en_line in alignment_in_stanza:
        if not bo_line.strip() or not en_line.strip():
            continue
        en_line = clean_en_text(en_line)
        f.write(f"{bo_line}\t{en_line}\n")
