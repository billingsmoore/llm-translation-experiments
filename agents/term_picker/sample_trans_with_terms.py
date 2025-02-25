import json
from pathlib import Path

combined_data_fn = (
    Path(__file__).parent.parent.parent / "data" / "chonjuk" / "combined_data.json"
)

data_path = Path(__file__).parent / "data"

# Load the translations
combined_data = json.loads(combined_data_fn.read_text())


def filter_tarns_with_term(data, term):
    """
    Filter translations containing a specific Tibetan term.
    
    Args:
        data (list): List of translation entries loaded from JSON.
        term (str): The Tibetan term to filter by.
    
    Returns:
        list: A list of dictionaries containing filtered translations.
    """
    filtered_translations = []
    for item in data:
        if not ((item["com_1"] or item["com_2"]) and (item["en_1"] or item["en_2"])):
            continue

        if term in item["bo"]:
            filtered_translations.append(
                {
                    "Tibetan": item["bo"],
                    "Sanskrit": item["sa"],
                    "English 1": item["en_1"],
                    "English 2": item["en_2"],
                    "Commentary 1": item["com_1"],
                    "Commentary 2": item["com_2"],
                }
            )
    return filtered_translations


def main():
    """
    Main function to filter translations for a predefined list of Tibetan terms
    and save results to JSON files if enough translations are found.
    """
    tibetan_terms = [
        "བྱང་ཆུབ་སེམས་",
        "སྡུག་བསྔལ་",
        "ཤེས་རབ་",
        "སྙིང་རྗེ་",
        "བླ་མ་",
        "སངས་རྒྱས་",
        "ཆོས་",
        "དགེ་འདུན་",
        "སྟོང་པ་ཉིད་",
        "དགེ་བ་",
        "སྡིག་པ་",
        "འཁོར་བ་",
        "མྱ་ངན་ལས་འདས་པ་",
        "བསམ་གཏན་",
        "ཕ་རོལ་ཏུ་ཕྱིན་པ་",
        "དབུ་མ་",
        "ཀུན་རྫོབ་",
        "དོན་དམ་",
        "རྟེན་འབྲེལ་",
        "བདག་མེད་",
    ]
    for term in tibetan_terms:
        filtered_translations = filter_tarns_with_term(combined_data, term)
        output_fn = data_path / f"{term}.json"
        print(len(filtered_translations))
        if len(filtered_translations) >= 10:
            json.dump(
                filtered_translations, output_fn.open("w"), ensure_ascii=False, indent=2
            )
            print(f"Save translations for {term} at {output_fn}.")
        else:
            print(f"Not enough translations found for {term}.")


if __name__ == "__main__":
    main()
