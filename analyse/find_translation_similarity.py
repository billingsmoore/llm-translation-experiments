import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import sacrebleu
from sacrebleu.metrics import BLEU, CHRF, TER


class TranslationPairAnalyzer:
    def __init__(self):
        self.bleu = BLEU()
        self.chrf = CHRF(word_order=2)
        self.ter = TER()

    def calculate_metrics(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """Calculate BLEU, chrF++, and TER scores for a translation pair."""
        refs = [reference]
        hyps = [hypothesis]

        bleu_score = self.bleu.corpus_score(hyps, [refs]).score / 100
        chrf_score = self.chrf.corpus_score(hyps, [refs]).score / 100
        ter_score = self.ter.corpus_score(hyps, [refs]).score / 100

        return {"bleu": bleu_score, "chrf": chrf_score, "ter": ter_score}

    def find_representative_pairs(
        self,
        translation_examples: List[Dict],
        llm_key: str = "01_zero_shot",
        n: int = 3,
        weights: Dict[str, float] = None,
    ) -> Dict:
        """Find n most similar, moderate, and dissimilar translation pairs."""
        if weights is None:
            weights = {"bleu": 1 / 3, "chrf": 1 / 3, "ter": 1 / 3}

        scored_examples = []
        for example in translation_examples:
            if "target_gt" in example and llm_key in example:
                metrics = self.calculate_metrics(example["target_gt"], example[llm_key])

                weighted_score = (
                    weights["bleu"] * metrics["bleu"]
                    + weights["chrf"] * metrics["chrf"]
                    + weights["ter"] * (1 - metrics["ter"])
                )

                scored_examples.append(
                    {
                        "source": example["Source"],
                        "human_translation": example["target_gt"],
                        "llm_translation": example[llm_key],
                        "weighted_score": weighted_score,
                        "metrics": metrics,
                    }
                )

        scored_examples.sort(key=lambda x: x["weighted_score"])
        n = min(n, len(scored_examples) // 3)
        mid_start = (len(scored_examples) - n) // 2

        return {
            "most_similar": scored_examples[-n:],
            "moderate": scored_examples[mid_start : mid_start + n],
            "most_dissimilar": scored_examples[:n],
        }


def generate_markdown_report(
    results: Dict,
    llm_key: str,
    weights: Dict[str, float],
    output_file: str = "translation_analysis.md",
):
    """Generate a markdown report of the translation analysis."""

    def format_example_md(example: Dict, index: int) -> str:
        return f"""
### Example {index}

#### Source Text (Tibetan)
```tibetan
{example['source']}
```

#### Human Translation
```
{example['human_translation']}
```

#### LLM Translation
```
{example['llm_translation']}
```

#### Similarity Metrics
- BLEU Score: {example['metrics']['bleu']:.3f}
- chrF++ Score: {example['metrics']['chrf']:.3f}
- TER Score: {example['metrics']['ter']:.3f}
- Weighted Similarity Score: {example['weighted_score']:.3f}

---"""

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    markdown_content = f"""# Translation Analysis Report
Generated on: {current_time}

## Analysis Parameters
- LLM Model/Prompt: `{llm_key}`
- Metric Weights:
  - BLEU: {weights['bleu']}
  - chrF++: {weights['chrf']}
  - TER: {weights['ter']}

## Most Similar Translation Pairs
These examples show the highest similarity between human and LLM translations:

"""

    for i, example in enumerate(results["most_similar"], 1):
        markdown_content += format_example_md(example, i)

    markdown_content += "\n\n## Moderately Similar Translation Pairs\n"
    markdown_content += (
        "These examples show moderate similarity between human and LLM translations:\n"
    )

    for i, example in enumerate(results["moderate"], 1):
        markdown_content += format_example_md(example, i)

    markdown_content += "\n\n## Most Dissimilar Translation Pairs\n"
    markdown_content += "These examples show the largest differences between human and LLM translations:\n"

    for i, example in enumerate(results["most_dissimilar"], 1):
        markdown_content += format_example_md(example, i)

    markdown_content += """
## Analysis Notes
1. The weighted similarity score combines BLEU, chrF++, and TER metrics:
   - Higher BLEU and chrF++ scores indicate better similarity
   - Lower TER scores indicate better similarity (inverted in weighted score)
   - Weighted score range: 0 (most dissimilar) to 1 (most similar)

2. These examples were selected from a larger dataset to represent different
   levels of translation similarity between human and LLM outputs.

3. The examples can be used to:
   - Analyze patterns in translation differences
   - Identify strengths and weaknesses of the LLM translation
   - Compare translation approaches for specific linguistic features
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    return output_file


# Example usage
if __name__ == "__main__":
    translations_fn = (
        Path(__file__).parent.parent / "reports" / "translations_comparison.csv"
    )
    with open(translations_fn, "r", newline="") as file:
        reader = csv.DictReader(file)
        translations = list(reader)

    # Technical translation focus
    weights = {"bleu": 0.7, "chrf": 0.2, "ter": 0.1}
    llm_key = "01_zero_shot"

    report_dir = Path(__file__).parent.parent / "reports"

    # Run analysis
    for llm_key in [k for k in translations[0].keys() if k.startswith("0")]:
        analyzer = TranslationPairAnalyzer()
        results = analyzer.find_representative_pairs(
            translations, llm_key=llm_key, n=10, weights=weights
        )

        # Generate markdown report
        output_file = report_dir / f"translation_analysis_{llm_key}.md"
        output_file = generate_markdown_report(results, llm_key, weights, output_file)
        print(f"Analysis report generated: {output_file}")
