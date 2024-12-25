import argparse
from pathlib import Path

from experiment import Experiment
from llm import claud_sonet_chat


# Define the translation prompt
def create_translation_prompt(tibetan_text):
    return f"""
# Efficient Tibetan Translation Prompt

You are an expert Tibetan Buddhist text translator. Provide literal English translations following these guidelines:

## Core Instructions
1. For each Tibetan line:
   - Break down key terms and particles
   - Note essential grammatical structures
   - Enclose final English translation in <t> tags
   - Add only critical technical notes

2. Required elements:
   - Preserve Sanskrit terms (e.g., dharmakāya)
   - Keep consistent term translations
   - Maintain technical precision

## Example Format:

Input:
བདེ་གཤེགས་ཆོས་ཀྱི་སྐུ་མངའ་སྲས་བཅས་དང་། །ཕྱག་འོས་ཀུན་ལའང་གུས་པར་ཕྱག་འཚལ་ཏེ། །བདེ་གཤེགས་སྲས་ཀྱི་སྡོམ་ལ་འཇུག་པ་ནི། །ལུང་བཞིན་མདོར་བསྡུས་ནས་ནི་བརྗོད་པར་བྱ། །

Key terms:
བདེ་གཤེགས་(Sugata), ཆོས་ཀྱི་སྐུ་(dharmakāya), སྲས་(Offspring), ཕྱག་འཚལ་(Prostrate)

<t>
I prostrate with respect to the sugatas, Who have the dharmakaya, and their offspring, And also to all worthy of veneration. I'll teach in brief, according to the scriptures, The way to enter the bodhisattva's vows.</t>

Input:
{tibetan_text}
"""


# Example usage
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--test", action="store_true")
    args = arg_parser.parse_args()

    exp_name = Path(__file__).stem
    result_fn = Path(__file__).parent / "results.json"

    exp = Experiment(
        exp_name,
        claud_sonet_chat,
        create_translation_prompt,
    )
    exp.run_experiment(test=args.test)
