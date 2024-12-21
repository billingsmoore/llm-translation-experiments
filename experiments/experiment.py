import json
import re
from typing import List


def parse_translations(text: str) -> List[str]:
    """
    Extract translations enclosed in <t> tags from text.

    Args:
        text (str): Input text containing translations in <t> tags

    Returns:
        List[str]: List of extracted translations

    Example:
        >>> text = '''
        Some text here
        <t>First translation</t>
        More text
        <t>Second translation</t>
        '''
        >>> parse_translations(text)
        ['First translation', 'Second translation']
    """
    # Pattern matches anything between <t> and </t>, non-greedy
    pattern = r"<t>(.*?)</t>"

    # Find all matches in the text
    translations = re.findall(pattern, text, re.DOTALL)

    # Strip whitespace from each translation
    translations = [t.strip() for t in translations]

    return " ".join(translations)


class Experiment:
    def __init__(self, exp_name, llm, prompt_generator, result_fn):
        self.llm = llm
        self.exp_name = exp_name
        self.prompt_generator = prompt_generator
        self.result_fn = result_fn

    def get_source_texts(self):
        results = json.load(open(self.result_fn, "r"))
        for text_id, data in results.items():
            yield text_id, data["source"]

    def save_result(self, text_id, response):
        results = json.load(open(self.result_fn, "r"))
        if "target_pred" not in results[text_id]:
            results[text_id]["target_pred"] = {}
        results[text_id]["target_pred"][self.exp_name] = {
            "output": response,
            "translation": parse_translations(response),
        }
        json.dump(results, open(self.result_fn, "w"), ensure_ascii=False, indent=2)

    def is_translated(self, text_id):
        results = json.load(open(self.result_fn, "r"))
        return (
            "target_pred" in results[text_id]
            and self.exp_name in results[text_id]["target_pred"]
        )

    def run_experiment(self, debug=False, testing=False):
        for source_text_id, source_text in self.get_source_texts():
            if self.is_translated(source_text_id):
                continue
            prompt = self.prompt_generator(source_text)
            response = self.llm(prompt)
            self.save_result(source_text_id, response)
            if debug:
                print(f"Source text ID: {source_text_id}")
                print(f"Source text: {source_text}")
                print("-" * 100)
                print(f"Prompt: {prompt}")
                print("-" * 100)
                print(f"Response: {response}")
                print("-" * 100)
                print(f"Translations: {parse_translations(response)}")

            if testing:
                break
