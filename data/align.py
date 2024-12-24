from pathlib import Path

import claudette
from tqdm import tqdm

data_path = Path(__file__).parent / "chonjuk"
commentary_fn = data_path / "chonjuk_commentary.csv"
root_en = data_path / "new_chonjuk-en-root.txt"
algin_fn = data_path / "chonjuk_trans_com.tsv"

segment_pairs = commentary_fn.read_text().strip().split("\n")[1:]
verses_en = [
    verse.replace("\n", " ") for verse in root_en.read_text().strip().split("\n\n")
]


model_name = claudette.models[1]


def claud_sonet_chat(prompt):
    claud_sonet = claudette.Chat(model_name)
    response = claud_sonet(prompt)
    return "".join([textblock.text for textblock in response.content])


auto_align_prompt = """
You are a translation expert. Post-correct the Target English text by removing parts which is not the translation of the source Tibetan text. Also greate a glossary terms for the following text.

Do not change the original meaning of the source text.
Do not split the tibetan text into multiple parts.

Input format:
[Source Tibetan text]\t[Poor translation Target English text]

Output format:
[Same Source Tibetan text]\tt[Post-corrected target English text]
Glossary:
[Term in Tibetan]\t[Term in English]\t[Definition for English term]
(multiple lines)

Input:
{}
"""


def get_rough_alignments():
    def get_en_verse(verses_en, i):
        context_len = 1
        if i < context_len:
            left_i = 0
        else:
            left_i = i - context_len

        return " ".join(verses_en[left_i : i + context_len + 1])

    lines = []
    for i, segment_pair in enumerate(segment_pairs):
        root, cmt = segment_pair.split(",")
        if cmt.strip() == "":
            continue
        root_en_verse = get_en_verse(verses_en, i)
        lines.append(f"{root}\t{root_en_verse}")
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
            # if i == 3:
            #     break
            output = claud_sonet_chat(auto_align_prompt.format(rough_aligned_lines[i]))
            f.write(output + "\n")
            f.write("-" * 100 + "\n")


if __name__ == "__main__":
    align()
