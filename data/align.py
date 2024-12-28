from pathlib import Path

import claudette
from tqdm import tqdm

data_path = Path(__file__).parent / "chonjuk"
old_align_fn = data_path / "chonjuk_trans_align_better.tsv"
root_en = data_path / "chonjuk-en.txt"
algin_fn = data_path / "chonjuk_trans_align_new.tsv"

verses_bo = [
    verse.split("\t")[0].strip()
    for verse in old_align_fn.read_text().strip().splitlines()
]
verses_en = [
    line for line in root_en.read_text().strip().splitlines() if line.strip() != ""
]

model_name = claudette.models[1]


def claud_sonet_chat(prompt):
    claud_sonet = claudette.Chat(model_name)
    response = claud_sonet(prompt)
    return "".join([textblock.text for textblock in response.content])


auto_align_prompt = """
You are a translation expert. Post-correct the Target English text by removing parts which is not the translation of the source Tibetan text.

Do not change the original meaning of the source text.
Do not split the tibetan text into multiple parts.

Input format:
[Source Tibetan text]\t[Poor translation Target English text]

Output format:
[Same Source Tibetan text]\tt[Post-corrected target English text]

Input:
{}
"""


def get_rough_alignments():
    def get_en_verse(verses_en, i):
        i = i * 2
        context_len = 1
        if i < context_len:
            left_i = 0
        else:
            left_i = i - context_len

        return " ".join(verses_en[left_i : i + context_len + 1])

    lines = []
    for i, verse_bo in enumerate(verses_bo):
        verse_bo = verse_bo.strip()
        root_en_verse = get_en_verse(verses_en, i)
        lines.append(f"{verse_bo}\t{root_en_verse}")
    return lines


def parse_output(output):
    output_lines = output.strip().split("\n")
    for line in output_lines:
        if "\t" not in line:
            continue
        yield line


def align():
    rough_aligned_lines = get_rough_alignments()
    with algin_fn.open("w") as f:
        for i in tqdm(range(len(rough_aligned_lines))):
            output = claud_sonet_chat(auto_align_prompt.format(rough_aligned_lines[i]))
            f.write(output + "\n")


if __name__ == "__main__":
    align()
