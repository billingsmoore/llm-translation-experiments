import json
from pathlib import Path

from tqdm import tqdm

from experiments.llm import claud_sonet_chat

results_fn = Path(__file__).parent / "results.json"
results = json.load(open(results_fn, "r"))


def get_source_and_target(text_id):
    return results[text_id]["source"], results[text_id]["target_gt"]


def get_experiments_translation(text_id):
    for exp_name, pred in results[text_id]["target_pred"].items():
        yield exp_name, pred["translation"]


def generate_prompt(source, translation):
    return f"""
# Glossary Extraction Prompt

Extract Tibetan to English Glossary from the following translation:
Tibetan: {source} English: {translation}

## Core Instructions
- Find the English term used to each Tibetan term from the English translation
- Ignore Tibetan terms that are not translated to English
- DO NOT create a new translation for missing translation of Tibetan term
- Each Tibetan term should only have one English translation term in the Glossary
- Create a set of glossary for each Tibetan line separately
- Follow the example response format
- Do not include any additional information

## Example Response Format:
1 བདེ་གཤེགས་ཆོས་ཀྱི་སྐུ་མངའ་སྲས་བཅས་དང་།
1.1 Glossary: བདེ་གཤེགས་ (Sugata), ཆོས་ཀྱི་སྐུ་ (dharmakāya), མངའ་ (possess), སྲས་ (offspring)
2 །ཕྱག་འོས་ཀུན་ལའང་གུས་པར་ཕྱག་འཚལ་ཏེ།
2.1 Glossary: ཕྱག་འོས་ (worthy of veneration),
3 །བདེ་གཤེགས་སྲས་ཀྱི་སྡོམ་ལ་འཇུག་པ་ནི།
3.1 བདེ་གཤེགས་ (Sugata), སྲས་ (offspring), སྡོམ་ (vows), འཇུག་པ་ (enter)
"""


def parse_glossary(text):
    """
    Parse Tibetan text with glossary into a dictionary format.

    Args:
        text (str): Multi-line string containing numbered Tibetan text and glossary

    Returns:
        dict: Dictionary with Tibetan text as keys and glossary dictionaries as values
    """
    # Initialize result dictionary
    result = {}

    # Split text into lines and remove empty lines
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]

    current_text = ""

    for line in lines:
        # If line starts with number but no decimal (main text)
        if line[0].isdigit() and "." not in line:
            # Remove number and period from start of line
            current_text = line.split(" ", 1)[1].strip()
            result[current_text] = {}

        # If line starts with number and decimal (glossary)
        elif "." in line.split(" ")[0]:
            # Skip the glossary label
            glossary_items = line.split(":", 1)[1].strip()

            # Split items by comma and process each
            items = [item.strip() for item in glossary_items.split(",")]

            for item in items:
                # Remove parentheses and split by space
                tibetan, english = item.strip().split("(")
                tibetan = tibetan.strip()
                english = english.rstrip(")").strip()

                # Add to dictionary
                result[current_text][tibetan] = english

    return result


def save_glossary(text_id, glossary, exp_name=None):
    if exp_name:
        results[text_id]["glossary"][exp_name] = glossary
    else:
        if "glossary" not in results[text_id]:
            results[text_id]["glossary"] = {}
        results[text_id]["glossary"]["target_gt"] = glossary


def is_glossary_extracted(text_id, exp_name=None):
    if not exp_name:
        return (
            "glossary" in results[text_id]
            and "target_gt" in results[text_id]["glossary"]
        )
    else:
        return exp_name in results[text_id]["glossary"]


def extract_glossary():
    for text_id in tqdm(results):
        if is_glossary_extracted(text_id):
            continue
        source, target = get_source_and_target(text_id)
        prompt = generate_prompt(source, target)
        output = claud_sonet_chat(prompt)
        glossary = parse_glossary(output)
        save_glossary(text_id, glossary)
        for exp_name, llm_translation in get_experiments_translation(text_id):
            if is_glossary_extracted(text_id, exp_name=exp_name):
                continue
            prompt = generate_prompt(source, llm_translation)
            output = claud_sonet_chat(prompt)
            glossary = parse_glossary(output)
            save_glossary(text_id, glossary, exp_name=exp_name)
        json.dump(results, open(results_fn, "w"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    extract_glossary()
