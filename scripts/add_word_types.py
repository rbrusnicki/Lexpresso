import re
import json
from html.parser import HTMLParser
import os
import glob

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
                if 'level' not in self.current_word:
                    self.current_word['level'] = ''
            elif self.in_frequency_cell:
                self.in_frequency_cell = False
                if all(k in self.current_word for k in ['word', 'translation', 'frequency']):
                    word = self.current_word['word'].strip()
                    word = re.sub(r'\s+', ' ', word)
                    self.current_word['word'] = word

                    if 'level' not in self.current_word:
                        self.current_word['level'] = ''

                    self.words.append(self.current_word.copy())
                    self.current_word = {}

def parse_word_type_files():
    """Parse all word type files and create a mapping of word -> word_type"""

    word_type_mapping = {}

    # Define word type categories and their file patterns
    word_types = {
        'Adjective': ['Adjetives_*.txt', 'Adjectives_*.txt'],  # Handle typo
        'Adverb': ['Adverbs*.txt'],
        'Conjunction': ['Conjunctions*.txt'],
        'Interjection': ['Interjections*.txt'],
        'Noun': ['Nouns_*.txt'],
        'Number': ['Numbers*.txt'],
        'Preposition': ['Prepositions*.txt'],
        'Pronoun': ['Pronoum*.txt'],  # Handle typo
        'Verb': ['Verbs_*.txt']
    }

    print("\nParsing word type files...")
    print("=" * 60)

    for word_type, patterns in word_types.items():
        files = []
        for pattern in patterns:
            # Look for files in raw_data/word_types/
            full_pattern = os.path.join('..', 'raw_data', 'word_types', pattern)
            files.extend(glob.glob(full_pattern))

        if not files:
            continue

        print(f"\n{word_type}s:")
        type_word_count = 0

        for file_path in sorted(files):
            if os.path.getsize(file_path) == 0:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                parser = GermanWordParser()
                parser.feed(html_content)

                # Add to mapping
                for word_entry in parser.words:
                    key = (word_entry['word'], word_entry['translation'])
                    word_type_mapping[key] = word_type
                    type_word_count += 1

                print(f"  {os.path.basename(file_path):25} -> {len(parser.words):4} words")
            except Exception as e:
                print(f"  [ERROR] {os.path.basename(file_path):25} -> {str(e)}")

        if type_word_count > 0:
            print(f"  [TOTAL] {word_type}s: {type_word_count} words")

    return word_type_mapping

def add_word_types_to_json(word_type_mapping):
    """Add word_type field to existing JSON files"""

    json_files = [
        os.path.join('..', 'processed_data', 'by_level', 'german_words_A1.json'),
        os.path.join('..', 'processed_data', 'by_level', 'german_words_A2.json'),
        os.path.join('..', 'processed_data', 'by_level', 'german_words_B1.json'),
        os.path.join('..', 'processed_data', 'by_level', 'german_words_B2.json')
    ]

    print("\n" + "=" * 60)
    print("Adding word types to JSON files...")
    print("=" * 60)

    for json_file in json_files:
        if not os.path.exists(json_file):
            print(f"\n{json_file}: [NOT FOUND]")
            continue

        # Load existing JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Add word_type to each word
        matched = 0
        unmatched = 0

        for word_entry in data['words']:
            key = (word_entry['word'], word_entry['translation'])
            if key in word_type_mapping:
                word_entry['word_type'] = word_type_mapping[key]
                matched += 1
            else:
                word_entry['word_type'] = 'Unknown'
                unmatched += 1

        # Save updated JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n{json_file}:")
        print(f"  Matched:   {matched:4} words")
        print(f"  Unmatched: {unmatched:4} words")
        print(f"  Total:     {data['total_count']:4} words")

def main():
    # Parse word type files
    word_type_mapping = parse_word_type_files()

    print(f"\n" + "=" * 60)
    print(f"Total unique word+translation pairs: {len(word_type_mapping)}")

    # Add word types to JSON files
    add_word_types_to_json(word_type_mapping)

    print("\n" + "=" * 60)
    print("Done! Word types have been added to all JSON files.")

if __name__ == "__main__":
    main()
