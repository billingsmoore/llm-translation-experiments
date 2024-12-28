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
1.1 བདེ་གཤེགས་ (Sugata)
1.2 ཆོས་ཀྱི་སྐུ་ (dharmakāya)
1.3 མངའ་ (possess)
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


text_ids = [
    "3",
    "4",
    "5",
    "8",
    "10",
    "13",
    "17",
    "18",
    "19",
    "22",
    "25",
    "26",
    "33",
    "36",
    "39",
    "40",
    "41",
    "42",
    "43",
    "44",
    "47",
    "49",
    "50",
    "51",
    "52",
    "53",
    "58",
    "59",
    "63",
    "64",
    "65",
    "67",
    "68",
    "72",
    "76",
    "78",
    "79",
    "81",
    "82",
    "86",
    "89",
    "92",
    "96",
    "97",
    "98",
    "99",
    "103",
    "105",
    "106",
    "107",
    "108",
    "111",
    "113",
    "115",
    "116",
    "117",
    "121",
    "125",
    "129",
    "134",
    "137",
    "138",
    "142",
    "144",
    "152",
    "158",
    "167",
    "172",
    "180",
    "181",
    "185",
    "187",
    "188",
    "190",
    "192",
    "193",
    "195",
    "197",
    "200",
    "202",
    "204",
    "207",
    "209",
    "212",
    "213",
    "215",
    "217",
    "218",
    "220",
    "221",
    "222",
    "223",
    "224",
    "225",
    "232",
    "235",
    "236",
    "238",
    "240",
    "242",
    "243",
    "245",
    "248",
    "250",
    "258",
    "260",
    "264",
    "265",
    "267",
    "269",
    "270",
    "271",
    "272",
    "273",
    "277",
    "280",
    "283",
    "285",
    "287",
    "288",
    "289",
    "290",
    "291",
    "293",
    "295",
    "298",
    "300",
    "304",
    "307",
    "309",
    "310",
    "311",
    "312",
    "314",
    "315",
    "318",
    "321",
    "322",
    "325",
    "328",
    "329",
    "331",
    "335",
    "336",
    "339",
    "340",
    "342",
    "345",
    "348",
    "351",
    "354",
    "355",
    "364",
    "368",
    "374",
    "376",
    "378",
    "380",
    "381",
    "382",
    "388",
    "395",
    "398",
    "399",
    "402",
    "403",
    "404",
    "410",
    "413",
    "414",
    "415",
    "416",
    "423",
    "425",
    "430",
    "432",
    "437",
    "439",
    "440",
    "445",
    "448",
    "449",
    "450",
    "451",
    "452",
    "453",
    "454",
    "458",
    "464",
    "465",
    "466",
    "467",
    "468",
    "471",
    "472",
    "485",
    "488",
    "489",
    "491",
    "492",
    "497",
    "498",
    "510",
    "513",
    "514",
    "518",
    "520",
    "525",
    "530",
    "531",
    "535",
    "536",
    "538",
    "544",
    "546",
    "547",
    "552",
    "553",
    "554",
    "556",
    "558",
    "561",
    "564",
    "565",
    "566",
    "567",
    "569",
    "571",
    "573",
    "574",
    "575",
    "576",
    "580",
    "581",
    "583",
    "584",
    "586",
    "592",
    "594",
    "603",
    "605",
    "606",
    "607",
    "608",
    "609",
    "610",
    "611",
    "612",
    "613",
    "614",
    "616",
    "617",
    "619",
    "621",
    "622",
    "623",
    "629",
    "634",
    "647",
    "649",
    "652",
    "654",
    "655",
    "656",
    "657",
    "661",
    "662",
    "663",
    "664",
    "665",
    "666",
    "667",
    "668",
    "670",
    "671",
    "672",
    "674",
    "675",
    "678",
    "680",
    "681",
    "682",
    "683",
    "686",
    "688",
    "689",
    "696",
    "700",
    "704",
    "705",
    "707",
    "712",
    "713",
    "716",
    "717",
    "720",
    "721",
    "722",
    "724",
    "725",
    "730",
    "731",
    "733",
    "735",
    "737",
    "741",
    "743",
    "749",
    "752",
    "755",
    "756",
    "757",
    "760",
    "761",
    "763",
    "764",
    "766",
    "768",
    "769",
    "771",
    "773",
    "774",
    "777",
    "778",
    "779",
    "780",
    "787",
    "792",
    "794",
    "796",
    "799",
    "801",
    "807",
    "808",
    "812",
    "813",
    "814",
    "815",
    "817",
    "818",
    "826",
    "830",
    "832",
    "836",
]


def extract_glossary():
    for text_id in tqdm(results):
        if text_id not in text_ids:
            continue
        if is_glossary_extracted(text_id):
            continue
        source, target = get_source_and_target(text_id)
        prompt = generate_prompt(source, target)
        output = claud_sonet_chat(prompt)
        glossary = parse_glossary(output)
        save_glossary(text_id, glossary)
        # for exp_name, llm_translation in get_experiments_translation(text_id):
        #     if is_glossary_extracted(text_id, exp_name=exp_name):
        #         continue
        #     prompt = generate_prompt(source, llm_translation)
        #     output = claud_sonet_chat(prompt)
        #     glossary = parse_glossary(output)
        # save_glossary(text_id, glossary, exp_name=exp_name)
        json.dump(results, open(results_fn, "w"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    extract_glossary()
