import difflib
import re
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple

import pandas as pd


class TranslationConsistencyChecker:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.term_translations = defaultdict(set)
        self.translation_terms = defaultdict(set)
        self.context_dict = defaultdict(list)
        self._process_data()

    def _process_data(self):
        """Process the dataframe and build lookup dictionaries."""
        for _, row in self.df.iterrows():
            term = row["Word"]
            translation = row["Translation"]
            context = row["Line"]

            self.term_translations[term].add(translation)
            self.translation_terms[translation].add(term)
            self.context_dict[term].append(
                {"translation": translation, "context": context, "verse": row["Verse"]}
            )

    def check_one_to_many_mappings(self) -> Dict[str, Set[str]]:
        """Find terms that have multiple translations."""
        return {
            term: translations
            for term, translations in self.term_translations.items()
            if len(translations) > 1
        }

    def check_many_to_one_mappings(self) -> Dict[str, Set[str]]:
        """Find translations that are used for multiple terms."""
        return {
            translation: terms
            for translation, terms in self.translation_terms.items()
            if len(terms) > 1
        }

    def analyze_capitalization_consistency(self) -> Dict[str, List[str]]:
        """Check for inconsistent capitalization in translations."""
        capitalization_issues = defaultdict(list)

        for term in self.term_translations:
            translations = self.term_translations[term]
            lowercase_map = defaultdict(set)

            for trans in translations:
                lowercase_map[trans.lower()].add(trans)

            for lower_trans, variants in lowercase_map.items():
                if len(variants) > 1:
                    capitalization_issues[term] = list(variants)

        return dict(capitalization_issues)

    def analyze_context_consistency(self, term: str) -> List[dict]:
        """Analyze how a term is translated in different contexts."""
        contexts = self.context_dict[term]
        analysis = []

        for i, ctx1 in enumerate(contexts):
            for ctx2 in contexts[i + 1 :]:
                if ctx1["translation"] != ctx2["translation"]:
                    similarity = difflib.SequenceMatcher(
                        None, ctx1["context"], ctx2["context"]
                    ).ratio()

                    analysis.append(
                        {
                            "term": term,
                            "translation1": ctx1["translation"],
                            "context1": ctx1["context"],
                            "translation2": ctx2["translation"],
                            "context2": ctx2["context"],
                            "context_similarity": similarity,
                        }
                    )

        return analysis

    def generate_report(self) -> dict:
        """Generate a comprehensive consistency analysis report."""
        report = {
            "one_to_many_mappings": self.check_one_to_many_mappings(),
            "many_to_one_mappings": self.check_many_to_one_mappings(),
            "capitalization_issues": self.analyze_capitalization_consistency(),
            "context_analysis": {},
        }

        # Analyze context for terms with multiple translations
        for term in report["one_to_many_mappings"]:
            report["context_analysis"][term] = self.analyze_context_consistency(term)

        return report


def print_report(report: dict):
    """Pretty print the consistency analysis report."""
    print("=== Translation Consistency Analysis Report ===\n")

    print("1. Terms with Multiple Translations:")
    for term, translations in report["one_to_many_mappings"].items():
        print(f"  {term}: {', '.join(translations)}")

    print("\n2. Translations Used for Multiple Terms:")
    for translation, terms in report["many_to_one_mappings"].items():
        print(f"  {translation}: {', '.join(terms)}")

    print("\n3. Capitalization Inconsistencies:")
    for term, variants in report["capitalization_issues"].items():
        print(f"  {term}: {', '.join(variants)}")

    print("\n4. Context Analysis for Inconsistent Translations:")
    for term, analyses in report["context_analysis"].items():
        if analyses:
            print(f"\n  Term: {term}")
            for analysis in analyses:
                print(
                    f"    Context Pair (similarity: {analysis['context_similarity']:.2f}):"
                )
                print(f"    - '{analysis['translation1']}' in: {analysis['context1']}")
                print(f"    - '{analysis['translation2']}' in: {analysis['context2']}")


# Usage example
if __name__ == "__main__":
    # Read the CSV file
    df = pd.read_csv(sys.argv[1])

    # Create checker instance
    checker = TranslationConsistencyChecker(df)

    # Generate and print report
    report = checker.generate_report()
    print_report(report)
