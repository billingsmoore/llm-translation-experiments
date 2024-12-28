import json

import sacrebleu

import config


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


def get_all_exp_names(results):
    text_ids = list(results.keys())
    return results[text_ids[0]]["target_pred"].keys()


def evaluate(results):
    for exp_name in get_all_exp_names(results):
        references, hypotheses = get_references_and_hypotheses(results, exp_name)
        bleu_score, chrf_score, ter_score = evaluate_multiple_translations(
            references, hypotheses
        )
        print(exp_name)
        print(f"Corpus BLEU Score: {bleu_score:.2f}")
        print(f"Corpus chrF++ Score: {chrf_score:.2f}")
        print(f"Corpus TER Score: {ter_score:.2f}")
        print()


if __name__ == "__main__":
    results = json.load(open(config.results_fn, "r"))
    evaluate(results)
