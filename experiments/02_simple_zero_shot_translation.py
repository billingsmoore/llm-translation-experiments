import argparse
from pathlib import Path

from experiment import Experiment
from llm import claud_sonet_chat


# Define the translation prompt
def create_translation_prompt(tibetan_text):
    return f"""
Translate the following Buddhist Tibetan passage into English: {tibetan_text} English:

## Core Instructions
   - Enclose final English translation in <t> tags
"""


# Example usage
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--debug", action="store_true")
    arg_parser.add_argument("--testing", action="store_true")
    args = arg_parser.parse_args()

    exp_name = Path(__file__).stem
    result_fn = Path(__file__).parent / "results.json"

    exp = Experiment(
        exp_name, claud_sonet_chat, create_translation_prompt, str(result_fn)
    )
    exp.run_experiment(debug=args.debug, testing=args.testing)
