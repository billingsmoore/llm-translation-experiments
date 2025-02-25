import json
from pathlib import Path

import claudette
from tqdm import tqdm

model_name = claudette.models[1]
claud_sonet = claudette.Chat(model_name)


def claud_sonet_chat(prompt):
    """
    Generate a response from the Claude model using the given prompt.
    
    Args:
        prompt (str): The text prompt to send to the Claude model.
    
    Returns:
        str: The generated response as a single concatenated string.
    """
    claud_sonet = claudette.Chat(model_name)
    response = claud_sonet(prompt)
    return "".join([textblock.text for textblock in response.content])


def combine_definitions(definitions):
    """
    Combine multiple definitions into a single, clear, and concise definition.
    
    Args:
        definitions (list of str): A list of definitions to be merged.
    
    Returns:
        str: A single refined definition that captures all key information without redundancy.
    """
    prompt = f"""Please combine these definitions into a single, clear, and concise definition
    that captures all important information without redundancy:
    {json.dumps(definitions, indent=2)}

    The combined definition should be comprehensive but concise."""

    return claud_sonet_chat(prompt)


def remove_duplicate_translations(translations):
    """
    Remove duplicate translations from a list while preserving the original order.
    
    Args:
        translations (list of str): A list of translations where duplicates need to be removed.
    
    Returns:
        list: A list of unique translations in their original order.
    """
    seen = set()
    return [x for x in translations if not (x.lower() in seen or seen.add(x.lower()))]


def process_entry(entry_data):
    """
    Process a single glossary entry by combining definitions and removing duplicate translations.
    
    Args:
        entry_data (dict): Dictionary containing translation and definition data for a term.
    
    Returns:
        dict: A processed entry with optimized translations and definitions.
    """
    processed_entry = {}

    for entry_type, data in entry_data.items():  # e.g., "term", "place", "person", etc.
        processed_entry[entry_type] = {
            "translations": remove_duplicate_translations(data["translations"]),
            "definitions": [],
        }

        # Combine definitions using Claude
        if len(data["definitions"]) > 1:
            combined_definition = combine_definitions(data["definitions"])
            processed_entry[entry_type]["definitions"] = [combined_definition]
        else:
            processed_entry[entry_type]["definitions"] = data["definitions"].copy()

    return processed_entry


def process_glossary(input_glossary):
    """
    Process an entire glossary by optimizing each entry.
    
    Args:
        input_glossary (dict): Dictionary containing glossary terms and their associated data.
    
    Returns:
        dict: A processed glossary with refined definitions and unique translations.
    """
    processed_glossary = {}

    for term, entry_data in tqdm(input_glossary.items()):
        processed_glossary[term] = process_entry(entry_data)

    return processed_glossary


def save_glossary(glossary, filename):
    """
    Save the processed glossary to a JSON file.
    
    Args:
        glossary (dict): The processed glossary data.
        filename (str or Path): The file path where the glossary should be saved.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    glossary_fn = Path(__file__).parent / "data" / "84000_glossary.json"
    glossary = json.loads(glossary_fn.read_text())
    optimized_glossary = process_glossary(glossary)

    # Save the processed glossary
    optimized_glossary_fn = glossary_fn.with_name("optimized_glossary.json")
    save_glossary(optimized_glossary, optimized_glossary_fn)
