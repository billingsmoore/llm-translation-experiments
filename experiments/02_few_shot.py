import argparse
from pathlib import Path

from experiment import Experiment
from llm import claud_sonet_chat


# Define the translation prompt
def create_translation_prompt(tibetan_text, *args, **kwargs):
    return f"""
Translate the following Buddhist Tibetan passage into English using the exampels: {tibetan_text}

Examples:
བདེ་གཤེགས་ཆོས་ཀྱི་སྐུ་མངའ་སྲས་བཅས་དང་། །ཕྱག་འོས་ཀུན་ལའང་གུས་པར་ཕྱག་འཚལ་ཏེ། །བདེ་གཤེགས་སྲས་ཀྱི་སྡོམ་ལ་འཇུག་པ་ནི། །ལུང་བཞིན་མདོར་བསྡུས་ནས་ནི་བརྗོད་པར་བྱ། །	I prostrate with respect to the sugatas, Who have the dharmakaya, and their offspring, And also to all worthy of veneration. I'll teach in brief, according to the scriptures, The way to enter the bodhisattva's vows.
ཕའམ་ཡང་ན་མ་ཡང་རུང་། །སུ་ལ་འདི་འདྲའི་ཕན་སེམས་ཡོད། །ལྷ་དང་དྲང་སྲོང་རྣམས་ཀྱང་རུང་། །ཚངས་པ་ལ་ཡང་འདི་ཡོད་དམ། །	Who has such altruism as this? Does even a father or a mother? Or do the gods or else the rishis? Do even Brahmas harbor this?
བྱང་ཆུབ་སྙིང་པོར་མཆིས་ཀྱི་བར། །སངས་རྒྱས་རྣམས་ལ་སྐྱབས་སུ་མཆི། །ཆོས་དང་བྱང་ཆུབ་སེམས་དཔའ་ཡི། །ཚོགས་ལའང་དེ་བཞིན་སྐྱབས་སུ་མཆི། །	Until I reach enlightenment's essence, I go for refuge to the buddhas. I go for refuge to the dharma And sangha of bodhisattvas too.

## Core Instructions
   - Enclose final English translation in <t> tags
"""


# Example usage
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--test", action="store_true")
    args = arg_parser.parse_args()

    exp_name = Path(__file__).stem

    exp = Experiment(
        exp_name,
        claud_sonet_chat,
        create_translation_prompt,
    )
    exp.run_experiment(test=args.test)
