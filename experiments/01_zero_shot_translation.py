from pathlib import Path

from experiment import Experiment
from llm import claud_sonet_chat


# Define the translation prompt
def create_translation_prompt(tibetan_text):
    return f"""
# Efficient Tibetan Translation Prompt

You are an expert Tibetan Buddhist text translator. Provide literal English translations following these guidelines:

## Core Instructions
1. For each Tibetan line:
   - Break down key terms and particles
   - Note essential grammatical structures
   - Enclose final English translation in <t> tags
   - Add only critical technical notes

2. Required elements:
   - Preserve Sanskrit terms (e.g., dharmakāya)
   - Use [brackets] for implied words
   - Keep consistent term translations
   - Maintain technical precision

## Example Format:

Input:
བདེ་གཤེགས་ཆོས་ཀྱི་སྐུ་མངའ་སྲས་བཅས་དང་།།

Key terms:
བདེ་གཤེགས་(Well-gone One), ཆོས་ཀྱི་སྐུ་(dharmakāya), སྲས་(heirs)

<t>The Well-gone Ones who possess the dharmakāya, together with [their] heirs, and</t>

## Multiple Line Example:

བདེ་གཤེགས་ཆོས་ཀྱི་སྐུ་མངའ་སྲས་བཅས་དང་།།
ཕྱག་འོས་ཀུན་ལའང་གུས་པས་ཕྱག་འཚལ་ཏེ།།

Key terms:
- Line 1: བདེ་གཤེགས་(Well-gone One), ཆོས་ཀྱི་སྐུ་(dharmakāya)
- Line 2: ཕྱག་འཚལ་(bow), གུས་པས་(respectfully)

<t>The Well-gone Ones who possess the dharmakāya, together with [their] heirs, and</t>
<t>To all those worthy of respect, I reverently bow.</t>

Remember:
- Each translation must use <t> tags
- Include only essential analysis
- Focus on accuracy over style
- Note only crucial technical terms

Input:
{tibetan_text}
"""


# Define a function to test translation prompts
def test_translation_prompt():
    # Create the prompt
    exp_name = Path(__file__).stem
    result_fn = Path(__file__).parent / "results.json"
    exp = Experiment(
        exp_name, claud_sonet_chat, create_translation_prompt, str(result_fn)
    )
    exp.run_experiment(debug=True, testing=True)


# Example usage
if __name__ == "__main__":
    test_translation_prompt()
