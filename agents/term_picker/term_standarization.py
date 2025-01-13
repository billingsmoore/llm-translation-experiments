import json
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from claudette import Chat, models


@dataclass
class Context:
    tibetan: str
    english: str
    commentaries: List[str]
    sanskrit: Optional[str] = None


class AnalysisType(Enum):
    SEMANTIC = "semantic"
    TERM_GENERATION = "term_generation"
    EVALUATION = "evaluation"


class BuddhistTermAnalyzer:
    def __init__(self):
        # Use Claude 3.5 Sonnet
        self.model = models[1]  # claude-3-5-sonnet

        # Initialize different chats for different analysis types
        self.system_prompts = {
            AnalysisType.SEMANTIC: """You are an expert in Buddhist terminology analysis.
            You must ONLY respond with a valid JSON object, no other text.
            Never include any explanatory text before or after the JSON.

            Required JSON structure:
            {
                "semantic_fields": ["field1", "field2", ...],
                "usage_patterns": ["pattern1", "pattern2", ...],
                "technical_analysis": "string",
                "cultural_context": "string"
            }""",
            AnalysisType.TERM_GENERATION: """You are an expert Buddhist translator.
            You must ONLY respond with a valid JSON object, no other text.
            Never include any explanatory text before or after the JSON.

            Required JSON structure:
            {
                "academic": {
                    "terms": ["term1", "term2"],
                    "reasoning": "string"
                },
                "practitioner": {
                    "terms": ["term1", "term2"],
                    "reasoning": "string"
                },
                "general": {
                    "terms": ["term1", "term2"],
                    "reasoning": "string"
                }
            }""",
            AnalysisType.EVALUATION: """You are an expert evaluator of Buddhist translations.
            You must ONLY respond with a valid JSON object, no other text.
            Never include any explanatory text before or after the JSON.

            Required JSON structure:
            {
                "evaluations": {
                    "term": {
                        "technical_score": 0.0,
                        "cultural_score": 0.0,
                        "audience_score": 0.0,
                        "reasoning": "string"
                    }
                }
            }""",
        }

        # Initialize chats with respective system prompts
        self.chats = {
            analysis_type: Chat(self.model, sp=system_prompt)
            for analysis_type, system_prompt in self.system_prompts.items()
        }

    def create_semantic_prompt(self, tibetan_term: str, contexts: List[Dict]) -> str:
        return f"""
        Respond ONLY with a JSON object analyzing this term and contexts:

        Term: {tibetan_term}

        Contexts:
        {json.dumps(contexts, indent=2, ensure_ascii=False)}

        Remember: Return ONLY the JSON object with no other text."""

    def create_generation_prompt(
        self, tibetan_term: str, semantic_analysis: Dict
    ) -> str:
        return f"""
        Respond ONLY with a JSON object containing translation candidates:

        Term: {tibetan_term}

        Semantic Analysis:
        {json.dumps(semantic_analysis, indent=2, ensure_ascii=False)}

        Remember: Return ONLY the JSON object with no other text."""

    def create_evaluation_prompt(
        self, tibetan_term: str, candidates: Dict, semantic_analysis: Dict
    ) -> str:
        return f"""
        Respond ONLY with a JSON object evaluating these candidates:

        Term: {tibetan_term}

        Candidates:
        {json.dumps(candidates, indent=2, ensure_ascii=False)}

        Semantic Analysis:
        {json.dumps(semantic_analysis, indent=2, ensure_ascii=False)}

        Remember: Return ONLY the JSON object with no other text."""

    def analyze_term(self, tibetan_term: str, contexts: List[Dict]) -> Dict:
        """Main analysis pipeline using cached prompts"""

        # 1. Semantic Analysis with cache
        semantic_prompt = self.create_semantic_prompt(tibetan_term, contexts)
        semantic_response = self.chats[AnalysisType.SEMANTIC](semantic_prompt)
        semantic_analysis = json.loads(semantic_response.content[0].text)

        # 2. Term Generation with cache
        generation_prompt = self.create_generation_prompt(
            tibetan_term, semantic_analysis
        )
        generation_response = self.chats[AnalysisType.TERM_GENERATION](
            generation_prompt
        )
        candidates = json.loads(generation_response.content[0].text)

        # 3. Evaluation with cache
        evaluation_prompt = self.create_evaluation_prompt(
            tibetan_term, candidates, semantic_analysis
        )
        evaluation_response = self.chats[AnalysisType.EVALUATION](evaluation_prompt)
        evaluations = json.loads(evaluation_response.content[0].text)

        # Combine results
        return self.format_results(
            tibetan_term, semantic_analysis, candidates, evaluations
        )

    def format_results(
        self,
        tibetan_term: str,
        semantic_analysis: Dict,
        candidates: Dict,
        evaluations: Dict,
    ) -> Dict:
        """Format the final results"""
        return {
            "tibetan_term": tibetan_term,
            "recommendations": {
                "Academic": {
                    "term": candidates["academic"]["terms"][0],
                    "reasoning": candidates["academic"]["reasoning"],
                },
                "Practitioner": {
                    "term": candidates["practitioner"]["terms"][0],
                    "reasoning": candidates["practitioner"]["reasoning"],
                },
                "General": {
                    "term": candidates["general"]["terms"][0],
                    "reasoning": candidates["general"]["reasoning"],
                },
            },
            "analysis": semantic_analysis,
            "evaluations": evaluations["evaluations"],
        }


class TermStandardizationAgent:
    def __init__(self):
        self.analyzer = BuddhistTermAnalyzer()

    def select_best_terms(self, tibetan_term: str, contexts: List[Dict]) -> Dict:
        """Main entry point for term standardization"""
        results = self.analyzer.analyze_term(tibetan_term, contexts)
        return results


# Example usage
def main():
    from pathlib import Path

    # Initialize agent
    agent = TermStandardizationAgent()

    # Test input
    tibetan_term = "བྱང་ཆུབ་སེམས་"
    contexts_fn = Path(__file__).parent / "data" / f"{tibetan_term}.json"
    contexts = json.load(contexts_fn.open())

    # Process term
    results = agent.select_best_terms(tibetan_term, contexts)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
