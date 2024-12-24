import sacrebleu


def evaluate_multiple_translations(references, hypotheses):
    # Calculate scores for entire corpus
    bleu = sacrebleu.corpus_bleu(hypotheses, references)
    chrf = sacrebleu.corpus_chrf(
        hypotheses, references, word_order=2, char_order=6  # Enable chrF++
    )  # Default char n-gram order

    return bleu.score, chrf.score


# Example with multiple sentences
references = [
    ["The nature of mind is clear light.", "Mind essence is luminous."],
    ["The Buddha taught emptiness.", "Emptiness was taught by the Buddha."],
]
hypotheses = ["The mind is naturally luminous.", "The Buddha explained emptiness."]

bleu_score, chrf_score = evaluate_multiple_translations(references, hypotheses)
print(f"Corpus BLEU Score: {bleu_score:.2f}")
print(f"Corpus chrF++ Score: {chrf_score:.2f}")
