from pathlib import Path

import claudette

data_path = Path(__file__).parent / "chonjuk"
alignment_fn = data_path / "chonjuk_translation.tsv"

model_name = claudette.models[1]


def claud_sonet_chat(prompt):
    claud_sonet = claudette.Chat(model_name)
    response = claud_sonet(prompt)
    return "".join([textblock.text for textblock in response.content])


auto_align_prompt = """
You are a translation expert. Analyze the following parallel text pairs and realign them to create better translation units while maintaining semantic completeness. Each realigned pair should:

Represent complete thoughts/sentences
Maintain proper context between source and target
Have similar length and complexity
Preserve the original meaning

Input format:
[Source text in Tibetan]\t[Target text in English]
(multiple lines)
Output format:
[Realigned source text]\t[Realigned target text]
(one aligned pair per line)"

Input:
{}
"""
