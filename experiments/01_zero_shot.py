import argparse
from pathlib import Path

from experiment import Experiment
from llm import claud_sonet_chat


# Define the translation prompt
def create_translation_prompt(tibetan_text, *args, **kwargs):
    return f"""
Translate the following Buddhist Tibetan passage into English: {tibetan_text} English:

## Core Instructions
   - Enclose final English translation in <t> tags
"""


# Example usage
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--test", action="store_true")
    args = arg_parser.parse_args()

    exp_name = Path(__file__).stem

    exp = Experiment(exp_name, claud_sonet_chat, create_translation_prompt)
    exp.run_experiment(test=args.test)
