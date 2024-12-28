import argparse
import json
import re
from pathlib import Path
from typing import List

from tqdm import tqdm


def parse_translations(text: str) -> List[str]:
    pattern = r"<t>(.*?)</t>"
    translations = re.findall(pattern, text, re.DOTALL)
    translations = [t.strip() for t in translations]
    return " ".join(translations)


class Experiment:
    def __init__(self, exp_name, llm, prompt_generator):
        self.llm = llm
        self.exp_name = exp_name
        self.prompt_generator = prompt_generator
        self.result_fn = Path(__file__).parent.parent / "results.json"

        assert self.result_fn.exists(), f"Result file {self.result_fn} does not exist."

    def get_source_texts(self):
        results = json.load(open(self.result_fn, "r"))
        for text_id, data in tqdm(results.items()):
            yield text_id, data["source"]

    def save_result(self, text_id, prompt, response):
        results = json.load(open(self.result_fn, "r"))
        if "target_pred" not in results[text_id]:
            results[text_id]["target_pred"] = {}
        results[text_id]["target_pred"][self.exp_name] = {
            "prompt": prompt,
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

    def run_experiment(self, replace=False, test=False):
        for text_id, source_text in self.get_source_texts():
            if not replace and self.is_translated(text_id):
                continue
            prompt = self.prompt_generator(source_text, text_id)
            response = self.llm(prompt)
            self.save_result(text_id, prompt, response)

            if test:
                print(f"Source text ID: {text_id}")
                print(f"Source text: {source_text}")
                print("-" * 100)
                print(f"Prompt: {prompt}")
                print("-" * 100)
                print(f"Response: {response}")
                print("-" * 100)
                print(f"Translations: {parse_translations(response)}")
                break
