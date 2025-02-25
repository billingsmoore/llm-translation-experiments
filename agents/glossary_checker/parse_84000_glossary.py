import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Dict, List, Set


def is_similar_or_subset(
    text1: str, text2: str, similarity_threshold: float = 0.8
) -> bool:
    """
    Check if two text strings are either similar or one is a subset of the other.

    Args:
        text1 (str): First text string to compare.
        text2 (str): Second text string to compare.
        similarity_threshold (float): Threshold for similarity ratio (default is 0.8).

    Returns:
        bool: True if the texts are similar or one is a subset of the other, otherwise False.
    """
    # Check if one text is completely contained within the other
    if text1 in text2 or text2 in text1:
        return True

    # Check similarity ratio for other cases
    ratio = SequenceMatcher(None, text1, text2).ratio()
    return ratio >= similarity_threshold


def add_definition(definitions: Set[str], new_def: str) -> Set[str]:
    """
    Add a new definition to the set while removing similar or subset definitions.
    Retains the longer definition when overlap is detected.

    Args:
        definitions (Set[str]): Existing set of definitions.
        new_def (str): New definition to be added.

    Returns:
        Set[str]: Updated set of definitions with redundant ones removed.
    """
    # Remove any existing definitions that are similar/subset
    defs_to_remove = set()
    should_add = True

    for existing_def in definitions:
        if is_similar_or_subset(existing_def, new_def):
            # Keep the longer definition
            if len(new_def) > len(existing_def):
                defs_to_remove.add(existing_def)
            else:
                should_add = False
                break

    # Remove similar/subset definitions
    definitions -= defs_to_remove

    # Add new definition if it should be added
    if should_add:
        definitions.add(new_def)

    return definitions


def parse_glossary_xml(xml_file: str) -> Dict:
    """
    Parse a glossary XML file and group data by Tibetan terms.
    Filters out similar definitions, keeping the most complete ones.

    Args:
        xml_file (str): Path to the XML file containing glossary data.

    Returns:
        Dict: A dictionary containing Tibetan terms mapped to their types, translations, and definitions.
    """
    namespace = {"ns": "http://read.84000.co/ns/1.0"}

    tree = ET.parse(xml_file)
    root = tree.getroot()

    terms = defaultdict(
        lambda: defaultdict(lambda: {"translations": set(), "definitions": set()})
    )

    for term in root.findall(".//ns:term", namespace):
        tibetan_elem = term.find("ns:tibetan", namespace)
        if tibetan_elem is None or not tibetan_elem.text:
            continue

        tibetan = tibetan_elem.text.strip()

        term_type = term.find("ns:type", namespace)
        if term_type is None or not term_type.text:
            continue

        term_type = term_type.text.strip()

        # Get translations
        for translation in term.findall("ns:translation", namespace):
            if translation is not None and translation.text:
                terms[tibetan][term_type]["translations"].add(translation.text.strip())

        # Get definitions and handle similarity/subsets
        for ref in term.findall("ns:ref", namespace):
            definition = ref.find("ns:definition", namespace)
            if definition is not None and definition.text:
                def_text = definition.text.strip()
                terms[tibetan][term_type]["definitions"] = add_definition(
                    terms[tibetan][term_type]["definitions"], def_text
                )

    # Convert sets to sorted lists for JSON serialization
    result = {}
    for tibetan, type_data in terms.items():
        result[tibetan] = {}
        for term_type, data in type_data.items():
            result[tibetan][term_type] = {
                "translations": sorted(data["translations"]),
                "definitions": sorted(data["definitions"]),
            }

    return result


def save_to_json(terms: Dict, output_file: str) -> None:
    """
    Save parsed glossary data to a JSON file.

    Args:
        terms (Dict): Parsed Tibetan terms and their associated data.
        output_file (str): Path to the output JSON file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(terms, f, ensure_ascii=False, indent=2)


def main():
    """
    Main function to parse glossary XML and save the output as JSON.
    Handles file errors and reports parsing progress.
    """
    input_xml = "data/84000_glossary.xml"
    output_json = "data/84000_glossary.json"

    try:
        print(f"Parsing {input_xml}...")
        terms = parse_glossary_xml(input_xml)
        print(f"Found {len(terms)} unique Tibetan terms")

        print(f"Saving to {output_json}...")
        save_to_json(terms, output_json)
        print("Done!")

    except FileNotFoundError:
        print(f"Error: Could not find the input file '{input_xml}'")
    except ET.ParseError:
        print("Error: Invalid XML file")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
