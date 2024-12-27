import argparse
from pathlib import Path

from experiment import Experiment
from llm import claud_sonet_chat


# Define the translation prompt
def create_translation_prompt(tibetan_text, *args, **kwargs):
    return f"""
# Translation Instructions

For each Tibetan Buddhist text passage, follow this chain of reasoning:

## 1. Initial Scan
"This is a [genre] text from [tradition/period]. Key terms: [...]. Main topic appears to be [...]"

## 2. Structure Analysis
- Main verb + tense
- Case markers
- Sentence pattern
- Honorifics Y/N

## 3. Key Terms Check
For each technical term:
"[Term] means [...] in general, but here context suggests [...]. Standard translation is [...]"

## 4. Context Review
"Text section: [...]. Assumes reader knows: [...]. Target audience: [...]"

## 5. Translation Process
1. Word-order draft: "[Tibetan order translation]"
2. English rewrite: "[Natural English]"
3. Technical check: "Terms consistent? Context clear? Notes needed?"

## Quick Reference
- Ambiguity? List options, choose best, note why
- Cultural terms? Translate/transliterate + note if needed
- Technical terms? Use standard translations
- Register? Match source formality
- Unclear? Mark for review

## Final Check
- Meaning accurate?
- Terms consistent?
- Context clear?
- Notes complete?

Think: "[Original intent] → [English equivalent] → [Reader understanding]"

## Outout Translation Format:
- Enclose final English translation in <t> tags, like <t>English translation</t>

Input:
{tibetan_text}

Output:
"""


# Example usage
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--test", action="store_true")
    args = arg_parser.parse_args()

    exp_name = Path(__file__).stem

    exp = Experiment(exp_name, claud_sonet_chat, create_translation_prompt)
    exp.run_experiment(test=args.test)
