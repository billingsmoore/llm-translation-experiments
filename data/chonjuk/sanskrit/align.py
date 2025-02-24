def extract_numbered_lines(text):
    """Extract lines with their line numbers from the text."""
    lines = {}
    for line in text.strip().split("\n"):
        # Look for lines starting with numbers
        if line and line[0].isdigit():
            # Extract the number and content
            parts = line.split(".", 1)
            if len(parts) == 2:
                line_num = int(parts[0])
                content = parts[1].strip()
                lines[line_num] = content
    return lines


def align_texts_to_tsv(tibetan_text, sanskrit_text, output_file):
    """Align Tibetan and Sanskrit texts and save to TSV file."""
    # Extract numbered lines from both texts
    tibetan_text = tibetan_text.replace("\ufeff", "")
    sanskrit_text = sanskrit_text.replace("\ufeff", "")
    tibetan_lines = extract_numbered_lines(tibetan_text)
    sanskrit_lines = extract_numbered_lines(sanskrit_text)

    # Get all line numbers
    all_line_nums = sorted(set(tibetan_lines.keys()) | set(sanskrit_lines.keys()))

    # Create TSV content
    tsv_lines = ["Line\tTibetan\tSanskrit"]  # Header
    for num in all_line_nums:
        tibetan = tibetan_lines.get(num, "")
        sanskrit = sanskrit_lines.get(num, "")
        tsv_lines.append(f"{num}\t{tibetan}\t{sanskrit}")

    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(tsv_lines))


from pathlib import Path

tibetan_text = (Path(__file__).parent / "tibetan.txt").read_text()
sanskrit_text = (Path(__file__).parent / "sanskrit.txt").read_text()


# Run the alignment
align_texts_to_tsv(tibetan_text, sanskrit_text, "aligned.tsv")
