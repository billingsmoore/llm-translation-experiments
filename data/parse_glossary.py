from pathlib import Path

from tqdm import tqdm

data_path = Path(__file__).parent / "chonjuk"
align_fn = data_path / "new_chonjuk_translation.tsv"
glossary_fn = data_path / "glossary.tsv"

alignment_segment_lines = []
glossary_lines = []

segments = align_fn.read_text().split("-" * 100)

for segment in tqdm(segments):
    if not segment.strip():
        continue
    alignment_segment_line, glossary = segment.split("Glossary:")

    alignment_segment_lines.append(alignment_segment_line.strip())
    glossary_lines.append(glossary.strip())

new_align_output = data_path / "new_chonjuk_translation_aligned.tsv"
new_align_output.write_text("\n".join(alignment_segment_lines))
glossary_fn.write_text("\n".join(glossary_lines))
