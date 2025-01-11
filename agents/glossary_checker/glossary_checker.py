import json
from pathlib import Path
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring


class GlossaryChecker:
    def __init__(self, glossary_path):
        self.glossary = self._load_glossary(glossary_path)
        self._build_term_mappings()

    def _load_glossary(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _normalize_tibetan_term(self, text):
        """Normalize Tibetan text by removing common punctuation."""
        text = text.replace("།", "")
        if text.endswith("་"):
            text = text[:-1]
        return text

    def get_tibetan_syllables(self, text):
        """Split Tibetan text into syllables."""
        text = text.replace("།", "")
        syllables = []
        for chunk in text.split():
            chunk = chunk.strip()
            syllables.extend(chunk.split("་"))
        return syllables

    def _build_term_mappings(self):
        """Build mappings for terms, including their semantic categories and definitions."""
        self.term_info = {}  # Store complete term information
        self.terms = set()  # Normalized terms for matching

        for term, data in self.glossary.items():
            normalized_term = self._normalize_tibetan_term(term)
            self.terms.add(normalized_term)

            # Initialize term info with original form
            self.term_info[normalized_term] = {"original_term": term, "categories": {}}

            # Store data by semantic category
            for category, cat_data in data.items():
                if isinstance(cat_data, dict):
                    self.term_info[normalized_term]["categories"][category] = {
                        "translations": cat_data.get("translations", []),
                        "definitions": cat_data.get("definitions", []),
                    }

    def extract_terms(self, text):
        """Extract terms based on Tibetan syllable matching."""
        text_syllables = self.get_tibetan_syllables(text)
        found_terms = []

        i = 0
        while i < len(text_syllables):
            longest_match = None
            for j in range(len(text_syllables), i, -1):
                possible_term = "་".join(text_syllables[i:j])
                if possible_term in self.terms:
                    longest_match = possible_term
                    break

            if longest_match:
                found_terms.append(longest_match)
                i += len(longest_match.split("་"))
            else:
                i += 1

        return found_terms

    def check(self, source_text, translation_text):
        """Check source text and translation against the glossary with category information."""
        results = []
        found_terms = self.extract_terms(source_text)

        for term in found_terms:
            term_data = self.term_info[term]

            result = {
                "source_term": term_data["original_term"],
                "normalized_term": term,
                "categories": {},
                "found_in_source": True,
                "found_in_translation": False,
            }

            # Check translations for each semantic category
            for category, cat_data in term_data["categories"].items():
                result["categories"][category] = {
                    "translations": cat_data["translations"],
                    "definitions": cat_data["definitions"],
                    "translation_found": False,
                }

                # Check if any expected translations appear
                for trans in cat_data["translations"]:
                    if trans in translation_text:
                        result["categories"][category]["translation_found"] = True
                        result["found_in_translation"] = True
                        break

            results.append(result)

        return results

    def results_to_xml(self, results, source_text, translation_text, pretty_print=True):
        """Convert checker results to XML format.

        Args:
            results: List of result dictionaries from check()
            source_text: Original source text that was checked
            translation_text: Translation text that was checked
            pretty_print: Whether to format the XML with proper indentation

        Returns:
            str: XML string representation of the results
        """
        # Create root element
        root = Element("glossary_check")

        # Add text information
        texts = SubElement(root, "texts")
        source = SubElement(texts, "source")
        source.text = source_text
        translation = SubElement(texts, "translation")
        translation.text = translation_text

        # Add found terms
        terms = SubElement(root, "terms")

        for result in results:
            term = SubElement(terms, "term")

            # Add term information
            source_term = SubElement(term, "source_term")
            source_term.text = result["source_term"]

            norm_term = SubElement(term, "normalized_term")
            norm_term.text = result["normalized_term"]

            found_status = SubElement(term, "found_status")
            SubElement(found_status, "in_source").text = str(result["found_in_source"])
            SubElement(found_status, "in_translation").text = str(
                result["found_in_translation"]
            )

            # Add categories
            categories = SubElement(term, "categories")
            for cat_name, cat_data in result["categories"].items():
                category = SubElement(categories, "category")
                category.set("type", cat_name)

                # Add translations
                translations = SubElement(category, "translations")
                translations.set("found", str(cat_data["translation_found"]))
                for trans in cat_data["translations"]:
                    trans_elem = SubElement(translations, "translation")
                    trans_elem.text = trans

                # Add definitions
                definitions = SubElement(category, "definitions")
                for defn in cat_data["definitions"]:
                    defn_elem = SubElement(definitions, "definition")
                    defn_elem.text = defn

        # Convert to string with pretty printing if requested
        if pretty_print:
            xml_str = minidom.parseString(
                tostring(root, encoding="unicode")
            ).toprettyxml(indent="  ")
            # Remove empty lines from pretty printed output
            xml_str = "\n".join([line for line in xml_str.split("\n") if line.strip()])
            return xml_str

        return tostring(root, encoding="unicode")


# Example usage:
if __name__ == "__main__":
    glossary_path = Path(__file__).parent / "data" / "84000_glossary.json"
    checker = GlossaryChecker(glossary_path)

    source = "བདེ་གཤེགས་ཆོས་ཀྱི་སྐུ་མངའ་སྲས་བཅས་དང་། །ཕྱག་འོས་ཀུན་ལའང་གུས་པར་ཕྱག་འཚལ་ཏེ། །བདེ་གཤེགས་སྲས་ཀྱི་སྡོམ་ལ་འཇུག་པ་ནི། །ལུང་བཞིན་མདོར་བསྡུས་ནས་ནི་བརྗོད་པར་བྱ། །"
    translation = "I prostrate with respect to the sugatas, Who have the dharmakaya, and their offspring, And also to all worthy of veneration. I'll teach in brief, according to the scriptures, The way to enter the bodhisattva's vows."

    # Get check results
    results = checker.check(source, translation)

    # Convert to XML and print
    xml_output = checker.results_to_xml(results, source, translation)
    print(xml_output)
