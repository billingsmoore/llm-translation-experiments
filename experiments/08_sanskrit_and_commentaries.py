import json
import re
from pathlib import Path

import claudette
from tqdm import tqdm

model_name = claudette.models[1]

data_path = Path(__file__).parent.parent / "data" / "chonjuk" / "combined_data.json"
data = json.loads(data_path.read_text())
results_path = Path(__file__).parent.parent / "data" / "results"
results_path.mkdir(exist_ok=True, parents=True)
translation_fn = results_path / "chonjuk_translation.json"
total_api_cost_call_fn = results_path / "total_api_call_cost.json"


def generate_prompt(tibetan_text, commentaries, sanskrit):
    return f"""In order to translate the Input Buddhist Tibetan text into English using the sanskrit version and Tibetan commentaries, provide the following:

A. Translation the sanskrit text
B. Complete translation of commentary 1
C. Complete translation of commentary 2
D. A combined summary of the commentaries
E. English translation of the Tibetan text (based on the sanskrit and the combined summary of the commentaries.) in <t> tags

Tibetan Text: {tibetan_text}

Commentary 1: {commentaries[0]}

Commentary 2: {commentaries[1]}

Sanskrit Text: {sanskrit}
    """


def parse_for_translation(llm_response):
    response_text = "".join([textblock.text for textblock in llm_response.content])
    pattern = r"<t>(.*?)</t>"
    translations = re.findall(pattern, response_text, re.DOTALL)
    translations = [t.strip() for t in translations]
    return " ".join(translations), response_text


def translate(tibetan_text, commentaries, sanskrit):
    prompt = generate_prompt(tibetan_text, commentaries, sanskrit)
    claud_sonet_chat = claudette.Chat(model_name)
    response = claud_sonet_chat(prompt)
    translation, response_text = parse_for_translation(response)

    return {
        "tibetan_text": tibetan_text,
        "translation": translation,
        "llm_response": response_text,
        "api_call_cost": claud_sonet_chat.cost,
    }


def load_translation(fn):
    if fn.exists():
        return json.loads(fn.read_text())
    return {}


def main():
    total_cost = 0
    translations = load_translation(translation_fn)
    for i, item in tqdm(enumerate(data[:3]), total=len(data[:3])):
        tibetan_text = item["bo"]
        if tibetan_text in translations:
            total_cost += translations[tibetan_text]["cost"]
            continue
        commentaries = [item["com_1"], item["com_2"]]
        sanskrit = item["sa"]
        translation = translate(tibetan_text, commentaries, sanskrit)
        translations[tibetan_text] = {
            "translation": translation["translation"],
            "llm_reponse": translation["llm_response"],
            "cost": translation["api_call_cost"],
        }
        total_cost += translation["api_call_cost"]

        if i % 2 == 0:
            json.dump(
                translations, translation_fn.open("w"), ensure_ascii=False, indent=2
            )

    print(f"Total cost: {total_cost}")
    json.dump(translations, translation_fn.open("w"), ensure_ascii=False, indent=2)
    json.dump(
        {"total_cost": total_cost},
        total_api_cost_call_fn.open("w"),
        ensure_ascii=False,
        indent=2,
    )


if __name__ == "__main__":
    main()
