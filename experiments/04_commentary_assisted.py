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


def generate_prompt(tibetan_text, text_id):
    text_commentaries = commentaries[text_id]
    return f"""
In order to translate the Input Buddhist Tibetan text into English using Tibetan commentaries, do the following:
1. Translate and summarize each commentary
2. Combine the meaning of the commentaries
3. Translate the Input text in accordance to the combine meaning of the commentaries.

Core Instructions
Enclose final English translation in <t> tags

Input: {tibetan_text}

Commentary 1: {text_commentaries[0]}

Commentary 2: {text_commentaries[1]}
"""


# Example usage
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--test", action="store_true")
    arg_parser.add_argument("--replace", action="store_true")
    args = arg_parser.parse_args()

    exp_name = Path(__file__).stem
    result_fn = Path(__file__).parent / "results.json"

    exp = Experiment(
        exp_name,
        claud_sonet_chat,
        generate_prompt,
    )
    exp.run_experiment(replace=args.replace, test=args.test)
