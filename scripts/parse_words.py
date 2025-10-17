import re
import json
from html.parser import HTMLParser

class GermanWordParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.words = []
        self.current_word = {}
        self.current_field = None
        self.capture_data = False
        self.in_word_cell = False
        self.in_translation_cell = False
        self.in_level_cell = False
        self.in_frequency_cell = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get('class', '')

        if 'cell word' in class_name:
            self.in_word_cell = True
            self.current_field = 'word'
            self.current_word['word'] = ''
        elif 'cell translation' in class_name:
            self.in_translation_cell = True
            self.current_field = 'translation'
            self.current_word['translation'] = ''
        elif 'cell level' in class_name:
            self.in_level_cell = True
            self.current_field = 'level'
        elif 'cell frequency' in class_name:
            self.in_frequency_cell = True
            self.current_field = 'frequency'

    def handle_data(self, data):
        data = data.strip()
        if not data or data in ['<!---->', '<!---->']:
            return

        if self.in_word_cell and data:
            # Accumulate word data (including article info)
            if self.current_word.get('word'):
                self.current_word['word'] += data
            else:
                self.current_word['word'] = data

        elif self.in_translation_cell and data:
            self.current_word['translation'] = data

        elif self.in_level_cell and data:
            self.current_word['level'] = data

        elif self.in_frequency_cell and data:
            self.current_word['frequency'] = int(data)

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.in_word_cell:
                self.in_word_cell = False
            elif self.in_translation_cell:
                self.in_translation_cell = False
            elif self.in_level_cell:
                self.in_level_cell = False
            elif self.in_frequency_cell:
                self.in_frequency_cell = False
                # End of a complete word entry
                if all(k in self.current_word for k in ['word', 'translation', 'level', 'frequency']):
                    # Clean up the word field
                    word = self.current_word['word'].strip()
                    # Remove extra whitespace
                    word = re.sub(r'\s+', ' ', word)
                    self.current_word['word'] = word

                    self.words.append(self.current_word.copy())
                    self.current_word = {}

def parse_german_words(input_file, output_file):
    # Read the HTML file
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse the HTML
    parser = GermanWordParser()
    parser.feed(html_content)

    # Create output data structure
    output_data = {
        'words': parser.words,
        'total_count': len(parser.words),
        'level': 'A1' if parser.words else 'Unknown'
    }

    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully parsed {len(parser.words)} words from {input_file}")
    print(f"Output saved to {output_file}")

    # Display first few entries as preview
    print("\nFirst 5 entries:")
    for i, word in enumerate(parser.words[:5], 1):
        print(f"{i}. {word['word']} -> {word['translation']}")

if __name__ == "__main__":
    input_file = "A1.txt"
    output_file = "german_words_A1.json"

    parse_german_words(input_file, output_file)
