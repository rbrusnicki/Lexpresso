import re
import json
from html.parser import HTMLParser
import os

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
                # If level was not set, set it to empty string
                if 'level' not in self.current_word:
                    self.current_word['level'] = ''
            elif self.in_frequency_cell:
                self.in_frequency_cell = False
                # End of a complete word entry (level is optional)
                if all(k in self.current_word for k in ['word', 'translation', 'frequency']):
                    # Clean up the word field
                    word = self.current_word['word'].strip()
                    # Remove extra whitespace
                    word = re.sub(r'\s+', ' ', word)
                    self.current_word['word'] = word

                    # Ensure level exists (even if empty)
                    if 'level' not in self.current_word:
                        self.current_word['level'] = ''

                    self.words.append(self.current_word.copy())
                    self.current_word = {}

def parse_german_words(input_file, output_file):
    # Read the HTML file
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Infer level from filename
    level_from_filename = None
    filename_base = os.path.splitext(os.path.basename(input_file))[0]
    if filename_base.upper() in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        level_from_filename = filename_base.upper()

    # Parse the HTML
    parser = GermanWordParser()
    parser.feed(html_content)

    # If level is missing from HTML, use filename level
    for word_entry in parser.words:
        if not word_entry.get('level') or word_entry['level'] == '':
            word_entry['level'] = level_from_filename or 'Unknown'

    # Create output data structure
    output_data = {
        'words': parser.words,
        'total_count': len(parser.words),
        'level': parser.words[0]['level'] if parser.words else level_from_filename or 'Unknown'
    }

    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    return len(parser.words)

def main():
    # List of files to process
    files = [
        ('A1.txt', 'german_words_A1.json'),
        ('A2.txt', 'german_words_A2.json'),
        ('B1.txt', 'german_words_B1.json'),
        ('B2.txt', 'german_words_B2.json')
    ]

    total_words = 0
    results = []

    print("Processing German word files...\n")
    print("=" * 50)

    for input_file, output_file in files:
        if os.path.exists(input_file):
            try:
                count = parse_german_words(input_file, output_file)
                total_words += count
                results.append((input_file, output_file, count, 'Success'))
                print(f"[OK] {input_file:12} -> {output_file:25} ({count:4} words)")
            except Exception as e:
                results.append((input_file, output_file, 0, f'Error: {str(e)}'))
                print(f"[ERROR] {input_file:12} -> Error: {str(e)}")
        else:
            results.append((input_file, output_file, 0, 'File not found'))
            print(f"[ERROR] {input_file:12} -> File not found")

    print("=" * 50)
    print(f"\nTotal words processed: {total_words}")
    print(f"Files processed successfully: {sum(1 for r in results if r[3] == 'Success')}/{len(files)}")

if __name__ == "__main__":
    main()
