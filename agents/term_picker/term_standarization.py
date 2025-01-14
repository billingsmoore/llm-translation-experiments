import json
from dataclasses import dataclass
from datetime import datetime
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
        self.total_api_calls_cost = 0
        self.token_usage = {}

        # Initialize different chats for different analysis types
        self.system_prompts = {
            AnalysisType.SEMANTIC: """You are an expert in Buddhist terminology analysis with deep knowledge of Sanskrit and Tibetan.
            Analyze the given term through a systematic philological approach.
            You must ONLY respond with a valid JSON object, no other text.
            Never include any explanatory text before or after the JSON.

            Required JSON structure:
            {
                "sanskrit_analysis": {
                    "term": "string",  # Sanskrit equivalent
                    "morphology": "string",  # Morphological breakdown
                    "literal_meaning": "string",  # Literal meaning in Sanskrit
                    "technical_usage": "string"  # Technical usage in Sanskrit Buddhist literature
                },
                "tibetan_mapping": {
                    "term": "string",  # Tibetan term
                    "morphology": "string",  # Morphological breakdown of Tibetan
                    "translation_strategy": "string",  # How Tibetan translates the Sanskrit
                    "semantic_extension": "string"  # Any semantic changes or extensions in Tibetan
                },
                "commentary_insights": [
                    {
                        "source": "string",  # Which commentary
                        "explanation": "string",  # Key explanation
                        "technical_points": ["string"]  # Technical clarifications
                    }
                ],
                "english_renderings": [
                    {
                        "translation": "string",
                        "accuracy_score": number,  # 1-10
                        "captures_sanskrit": boolean,
                        "captures_tibetan": boolean,
                        "notes": "string"
                    }
                ],
                "semantic_synthesis": {
                    "core_meaning": "string",  # Core meaning synthesized from all sources
                    "technical_usage": ["string"],  # List of technical usages found in context
                    "connotative_aspects": ["string"]  # Important connotations and implications
                },
                "usage_examples": [
                    {
                        "source_text": "string",  # Original context
                        "usage_type": "string",  # How term is used here
                        "commentary_explanation": "string"  # What commentary says about this usage
                    }
                ]
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
        Analyze this Buddhist term following these steps:

        Target Term: {tibetan_term}

        Analysis Process:
        1. First analyze the Sanskrit source:
           - Identify the Sanskrit equivalent
           - Break down its morphology
           - Understand its literal and technical meanings

        2. Map to Tibetan:
           - Analyze how Tibetan translates the Sanskrit
           - Note any semantic extensions or modifications
           - Understand the translation strategy

        3. Study the commentaries:
           - Extract key explanations
           - Note technical clarifications
           - Identify special usages explained

        4. Evaluate English translations:
           - Compare against Sanskrit and Tibetan meanings
           - Assess accuracy and completeness
           - Note which aspects are captured/missed

        5. Synthesize understanding:
           - Combine insights from all sources
           - Document technical usage patterns
           - Note important connotations

        Contexts:
        {json.dumps(contexts, indent=2, ensure_ascii=False)}

        Important:
        - Base analysis strictly on provided contexts
        - Use commentaries to resolve ambiguities
        - Pay special attention to technical terms in commentaries
        - Note when English translations diverge from Sanskrit/Tibetan
        - Document specific usage examples from the context

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

    def _track_usage(self, analysis_type: AnalysisType, response):
        cost = self.chats[analysis_type].cost
        self.total_api_calls_cost += cost
        self.token_usage[str(analysis_type)] = {
            "token_usage": repr(response.usage),
            "api_call_cost": cost,
        }

    def analyze_term(self, tibetan_term: str, contexts: List[Dict]) -> Dict:
        """Main analysis pipeline using cached prompts"""

        # 1. Semantic Analysis with cache
        semantic_prompt = self.create_semantic_prompt(tibetan_term, contexts)
        semantic_response = self.chats[AnalysisType.SEMANTIC](semantic_prompt)
        self._track_usage(AnalysisType.SEMANTIC, semantic_response)
        semantic_analysis = json.loads(semantic_response.content[0].text)

        # 2. Term Generation with cache
        generation_prompt = self.create_generation_prompt(
            tibetan_term, semantic_analysis
        )
        generation_response = self.chats[AnalysisType.TERM_GENERATION](
            generation_prompt
        )
        self._track_usage(AnalysisType.TERM_GENERATION, generation_response)
        semantic_analysis = json.loads(semantic_response.content[0].text)
        candidates = json.loads(generation_response.content[0].text)

        # 3. Evaluation with cache
        evaluation_prompt = self.create_evaluation_prompt(
            tibetan_term, candidates, semantic_analysis
        )
        evaluation_response = self.chats[AnalysisType.EVALUATION](evaluation_prompt)
        self._track_usage(AnalysisType.EVALUATION, evaluation_response)
        evaluations = json.loads(evaluation_response.content[0].text)

        # Combine results
        return self.format_results(
            tibetan_term,
            semantic_analysis,
            candidates,
            evaluations,
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
            "total_api_calls_cost": self.total_api_calls_cost,
            "token_usage": self.token_usage,
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
    date_time = datetime.now().strftime("%Y%m%d%H%M%S")
    results_path = Path(__file__).parent / "results"
    results_path.mkdir(exist_ok=True, parents=True)
    result_fn = results_path / f"{tibetan_term}_{date_time}.json"
    json.dump(results, result_fn.open("w"), indent=2, ensure_ascii=False)
    print(f"Results saved to: {result_fn}")


if __name__ == "__main__":
    main()
