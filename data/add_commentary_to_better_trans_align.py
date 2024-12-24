from pathlib import Path

data_path = Path(__file__).parent / "chonjuk"
align_fn = data_path / "chonjuk_trans_align_better.tsv"
commentary_1_fn = data_path / "chonjuk_commentary_1.csv"
commentary_2_fn = data_path / "chonjuk_commentary_2.csv"


def load_commentary(fn):
    commentary = {}
    for line in fn.read_text().split("\n"):
        if line.startswith("Root"):
            continue
        if not line.strip():
            continue

        root, commentary_text = line.split(",", 1)
        commentary[root] = commentary_text
    return commentary


commentary_1 = load_commentary(commentary_1_fn)
commentary_2 = load_commentary(commentary_2_fn)

alignment_segment_lines = []

for segment in align_fn.read_text().splitlines():
    if not segment.strip():
        continue

    bo, en = segment.split("\t")
    commentary_1_text = commentary_1.get(bo.strip(), "")
    commentary_2_text = commentary_2.get(bo.strip(), "")

    alignment_segment_lines.append(
        f"{bo}\t{en}\t{commentary_1_text}\t{commentary_2_text}"
    )

new_align_output = data_path / "chonjuk_trans_align_better_with_commentary.tsv"

# add cols name
alignment_segment_lines.insert(0, "BO\tEN\tCommentary 1\tCommentary 2")
new_align_output.write_text("\n".join(alignment_segment_lines))
