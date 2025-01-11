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

Extract Tibetan to English Glossary of Jargon terms from the following translation:
Tibetan: {source} English: {translation}

## Core Instructions
- Find the English term used to each Tibetan term from the English translation
- Ignore Tibetan terms that are not translated to English
- DO NOT create a new translation for missing translation of Tibetan term
- Each Tibetan term should only have one English translation term in the Glossary
- Create a set of glossary for each Tibetan line separately
- Do not include any additional information

## Example Response Format:
1 བདེ་གཤེགས་ཆོས་ཀྱི་སྐུ་མངའ་སྲས་བཅས་དང་།
1.1 བདེ་གཤེགས་ (Sugata)
1.2 ཆོས་ཀྱི་སྐུ་ (dharmakāya)
1.4 སྲས་ (offspring)
2 །ཕྱག་འོས་ཀུན་ལའང་གུས་པར་ཕྱག་འཚལ་ཏེ།
2.1 ཕྱག་འོས་ (worthy of veneration)
3 །བདེ་གཤེགས་སྲས་ཀྱི་སྡོམ་ལ་འཇུག་པ་ནི།
3.1 བདེ་གཤེགས་ (Sugata)
3.2 སྲས་ (offspring)
3.3 སྡོམ་ (vows)
3.4 འཇུག་པ་ (enter, follow)
"""


def parse_glossary(text):
    lines = text.strip().split("\n")
    glossary = {}
    current_main_line = None

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Check if this is a main line (starts with number without decimal)
        if line[0].isdigit() and "." not in line.split()[0]:
            # Extract the actual text (remove the line number)
            text = " ".join(line.split()[1:])
            current_main_line = text
            glossary[current_main_line] = {}

        # Check if this is a glossary entry (starts with number.number)
        elif "." in line.split()[0]:
            # Only process if we have a current main line
            if current_main_line is not None:
                # Split the line into parts
                parts = line.split()
                # Remove the number
                parts = parts[1:]

                # Extract the Tibetan word
                tibetan_word = parts[0]

                # Get the meaning part (everything in parentheses)
                meaning_text = " ".join(parts[1:]).strip("()")

                # Split meanings by comma and strip whitespace
                meanings = [m.strip() for m in meaning_text.split(",")]

                # If there's only one meaning, store as string
                # If multiple meanings, store as list
                final_meaning = meanings[0] if len(meanings) == 1 else meanings

                # Add to the dictionary
                glossary[current_main_line][tibetan_word] = final_meaning

    return glossary


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
        source, target = get_source_and_target(text_id)
        if not is_glossary_extracted(text_id):
            prompt = generate_prompt(source, target)
            output = claud_sonet_chat(prompt)
            glossary = parse_glossary(output)
            save_glossary(text_id, glossary)
        for exp_name, llm_translation in get_experiments_translation(text_id):
            if exp_name != "07_commentary_and_glossary_assisted":
                continue
            if is_glossary_extracted(text_id, exp_name=exp_name):
                continue
            prompt = generate_prompt(source, llm_translation)
            output = claud_sonet_chat(prompt)
            glossary = parse_glossary(output)
            save_glossary(text_id, glossary, exp_name=exp_name)
        json.dump(results, open(results_fn, "w"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    extract_glossary()
