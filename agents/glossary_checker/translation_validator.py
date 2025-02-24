import json
import re
from pathlib import Path

from anthropic import Anthropic
from glossary_checker import GlossaryChecker


class TranslationValidator:
    """
    Validates translations against a glossary using an LLM to filter contextually relevant terms.
    """
    def __init__(self, glossary_checker, anthropic_api_key):
        """
        Initialize the TranslationValidator with a glossary checker and an API key for the LLM.

        Args:
            glossary_checker (GlossaryChecker): Instance of GlossaryChecker for term validation.
            anthropic_api_key (str): API key for accessing the Claude LLM.
        """        
        self.checker = glossary_checker
        self.client = Anthropic(api_key=anthropic_api_key)

    def load_aligned_file(self, file_path):
        """
        Load a tab-separated file containing aligned source and target segments.

        Args:
            file_path (str or Path): Path to the aligned file.

        Returns:
            aligned_pairs (list of tuples): List of (source, target) text pairs.
        """
        aligned_pairs = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split("\t")
                if len(parts) != 2:
                    print(f"Warning: Skipping malformed line: {line}")
                    continue

                source, target = parts
                aligned_pairs.append((source.strip(), target.strip()))

        return aligned_pairs

    def filter_terms_with_llm(self, source_text, found_terms):
        """
        Use an LLM to filter out glossary terms that are not used as nouns in the given context.

        Args:
            source_text (str): The source text containing the terms.
            found_terms (list of dict): Terms found by the glossary checker.

        Returns:
            list of dict: Filtered terms that are valid nouns/names in context.
        """
        if not found_terms:
            return []

        prompt = f"""Given the Tibetan text and a list of terms found in it, determine which terms are actually being used as nouns/names in this specific context.

Tibetan text: {source_text}

Found terms: {', '.join(term['source_term'] for term in found_terms)}

For each term, analyze if it's being used as a noun/name in this specific context. Consider:
1. The grammatical structure of the sentence
2. The presence of case markers
3. The overall meaning and context

Return your analysis as a JSON list in this format:
[{{"term": "term1", "is_noun": true/false, "explanation": "short explanation"}}, ...]"""

        message = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            json_match = re.search(r"\[.*\]", message.content[0].text, re.DOTALL)
            if not json_match:
                return []

            analysis = json.loads(json_match.group())

            filtered_terms = []
            for term in found_terms:
                for analysis_item in analysis:
                    if (
                        analysis_item["term"] == term["source_term"]
                        and analysis_item["is_noun"]
                    ):
                        term["grammar_analysis"] = analysis_item["explanation"]
                        filtered_terms.append(term)
                        break

            return filtered_terms

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing LLM response: {e}")
            return []

    def calculate_translation_score(self, found_terms):
        """
        Calculate a translation quality score based on glossary adherence.

        Args:
            found_terms (list of dict): Terms found in translation.

        Returns:
            float: Translation score as a percentage.
        """
        if not found_terms:
            return 0.0

        total_translations = 0
        correct_translations = 0

        for term in found_terms:
            for cat_data in term["categories"].values():
                if cat_data["translations"]:
                    total_translations += 1
                    if cat_data["translation_found"]:
                        correct_translations += 1

        return (
            (correct_translations / total_translations) * 100
            if total_translations > 0
            else 0.0
        )

    def validate_translation(self, aligned_file_path):
        """
        Validate translations by checking against a glossary and filtering terms with an LLM.

        Args:
            aligned_file_path (str or Path): Path to the aligned file.

        Returns:
            list of dict: Validation results for each translation pair.
        """
        # Load aligned texts
        aligned_pairs = self.load_aligned_file(aligned_file_path)

        results = []
        for line_num, (source, target) in enumerate(aligned_pairs, 1):
            # Check against glossary
            check_results = self.checker.check(source, target)

            # Filter terms using LLM
            filtered_terms = self.filter_terms_with_llm(source, check_results)

            # Calculate score
            score = self.calculate_translation_score(filtered_terms)

            # Store results
            results.append(
                {
                    "line_number": line_num,
                    "source": source,
                    "target": target,
                    "terms": filtered_terms,
                    "score": score,
                }
            )

        return results

    def save_results(self, results, output_path):
        """
        Save validation results to a JSON file.

        Args:
            results (list of dict): Processed validation results.
            output_path (str or Path): File path to save results.
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "summary": {
                        "total_lines": len(results),
                        "average_score": (
                            sum(r["score"] for r in results) / len(results)
                            if results
                            else 0
                        ),
                    },
                    "lines": results,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )


# Example usage:
if __name__ == "__main__":
    import os

    data_path = Path(__file__).parent / "data"

    # Initialize components
    glossary_path = data_path / "84000_glossary.json"
    checker = GlossaryChecker(glossary_path)
    validator = TranslationValidator(checker, os.getenv("ANTHROPIC_API_KEY"))

    # Process aligned file
    aligned_file = data_path / "aligned_translations.txt"
    results = validator.validate_translation(aligned_file)

    # Save results
    validator.save_results(results, data_path / "validation_results.json")

    # Print summary
    total_score = sum(r["score"] for r in results) / len(results)
    print(f"\nOverall translation score: {total_score:.2f}%")

    # Print example line analysis
    print("\nExample line analysis:")
    for term in results[0]["terms"]:
        print(f"\nTerm: {term['source_term']}")
        print(f"Grammar analysis: {term.get('grammar_analysis', 'Not available')}")
        for cat_name, cat_data in term["categories"].items():
            print(f"Category: {cat_name}")
            print(f"Expected translations: {cat_data['translations']}")
            print(f"Found in translation: {cat_data['translation_found']}")
