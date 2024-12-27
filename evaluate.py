import json
from pathlib import Path

import sacrebleu

results_fn = Path(__file__).parent / "results.json"


def evaluate_multiple_translations(references, hypotheses):
    # Calculate scores for entire corpus
    bleu = sacrebleu.corpus_bleu(hypotheses, references)
    chrf = sacrebleu.corpus_chrf(
        hypotheses, references, word_order=2, char_order=6  # Enable chrF++
    )  # Default char n-gram order
    ter = sacrebleu.corpus_ter(hypotheses, references)

    return bleu.score, chrf.score, ter.score


def get_references_and_hypotheses(results, exp_name):
    references = []
    hypotheses = []
    for text_id, data in results.items():
        references.append([data["target_gt"]])
        hypotheses.append(data["target_pred"][exp_name]["translation"])
    return references, hypotheses


results = json.load(open(results_fn, "r"))

exp_name = "01_zero_shot_translation"
references, hypotheses = get_references_and_hypotheses(results, exp_name)
bleu_score, chrf_score, ter_score = evaluate_multiple_translations(
    references, hypotheses
)
print(exp_name)
print(f"Corpus BLEU Score: {bleu_score:.2f}")
print(f"Corpus chrF++ Score: {chrf_score:.2f}")
print(f"Corpus TER Score: {ter_score:.2f}")
print()

exp_name = "02_few_shot_translation_basic"
references, hypotheses = get_references_and_hypotheses(results, exp_name)
bleu_score, chrf_score, ter_score = evaluate_multiple_translations(
    references, hypotheses
)
print(exp_name)
print(f"Corpus BLEU Score: {bleu_score:.2f}")
print(f"Corpus chrF++ Score: {chrf_score:.2f}")
print(f"Corpus TER Score: {ter_score:.2f}")
