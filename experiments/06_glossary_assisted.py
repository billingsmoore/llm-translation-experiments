import argparse
import json
from pathlib import Path

from experiment import Experiment
from llm import claud_sonet_chat

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
            glossary_text += f"{term}: {glossary[term]}\n"
    return glossary_text


# Define the translation prompt
def create_translation_prompt(tibetan_text, *args, **kwargs):
    return f"""
Translate the following Buddhist Tibetan text into English using the glossary provided.

## Core Instructions
1. Stricly refer to the glossary for the translation of key terms
2. For mulitple meanings of a term, choose the most appropriate one from the glossary
3. Enclose final English translation in <t> tags

Tibetan Text: {tibetan_text}

## Glossary
{get_text_glossary(tibetan_text)}
"""


# Example usage
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--test", action="store_true")
    args = arg_parser.parse_args()

    exp_name = Path(__file__).stem

    exp = Experiment(exp_name, claud_sonet_chat, create_translation_prompt)
    exp.run_experiment(test=args.test)
