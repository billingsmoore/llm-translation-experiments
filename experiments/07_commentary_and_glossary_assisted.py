import argparse
import json
from pathlib import Path

from experiment import Experiment
from llm import claud_sonet_chat

results_fn = Path(__file__).parent.parent / "results.json"


def load_commentaries():
    results = json.load(open(results_fn, "r"))

    commentaries = {}
    for text_id, data in results.items():
        commentaries[text_id] = [data["commentary_1"], data["commentary_2"]]

    return commentaries


commentaries = load_commentaries()

import argparse

glossary_fn = Path(__file__).parent.parent / "data" / "chonjuk" / "glossary.json"
glossary = json.load(open(glossary_fn, "r"))


def find_key_terms(text: str):
    prompt = f"""
Find the key terms in the following Buddhist Tibetan passage:

## Core Instructions
- do not translate the key terms
- follow the format: key-term: term1, term2, term3, ...

## Example Response Format:
text: བདེ་གཤེགས་ཆོས་ཀྱི་སྐུ་མངའ་སྲས་བཅས་དང་། །ཕྱག་འོས་ཀུན་ལའང་གུས་པར་ཕྱག་འཚལ་ཏེ། །བདེ་གཤེགས་སྲས་ཀྱི་སྡོམ་ལ་འཇུག་པ་ནི།
key-terms: བདེ་གཤེགས་, ཆོས་ཀྱི་སྐུ་ མངའ་, སྲས་, ཕྱག་འོས་, སྡོམ་, འཇུག་པ་

text: {text}
key-terms:
"""
    response = claud_sonet_chat(prompt)
    key_terms = []
    for line in response.split("\n"):
        if "key-terms" in line:
            key_terms = [term.strip() for term in line.split(":")[1].strip().split(",")]
            break
    return key_terms


def get_text_glossary(text: str):
    key_terms = find_key_terms(text)
    glossary_text = ""
    for term in key_terms:
        if term in glossary:
            glossary_text += f"{term}:\n"
            for en_trans, en_def in glossary[term]:
                glossary_text += f"\t- {en_trans}\n"
    return glossary_text


def generate_prompt(tibetan_text, text_id, *args, **kwargs):
    text_commentaries = commentaries[text_id]
    return f"""
In order to translate the Input Buddhist Tibetan text into English using Tibetan commentaries, do the following:
1. Translate and summarize each commentary
2. Combine the meaning of the commentaries
3. Translate the Input text in accordance to the combine meaning of the commentaries.
4. Stricly refer to the glossary for the translation of key terms
5. For mulitple meanings of a term, choose the most appropriate one from the glossary
6. While translating the Tibetan verse into English, keeping its four-line structure and rhythm while ensuring natural readability and coherent meaning
6. Enclose final English translation in <t> tags

Input: {tibetan_text}

Commentary 1: {text_commentaries[0]}

Commentary 2: {text_commentaries[1]}

Glossary:
{get_text_glossary(tibetan_text)}
"""


# Example usage
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--test", action="store_true")
    args = arg_parser.parse_args()

    exp_name = Path(__file__).stem

    exp = Experiment(exp_name, claud_sonet_chat, generate_prompt)
    exp.run_experiment(test=args.test)
