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

def parse_files_for_level(level_prefix, output_file):
    """Parse all files matching level_prefix (e.g., 'A1') and combine into one JSON file"""

    # Find all files matching the pattern in raw_data/levels/
    pattern = os.path.join('..', 'raw_data', 'levels', f"{level_prefix}_*.txt")
    files = sorted(glob.glob(pattern))

    # Also check for the single file without underscore
    single_file = os.path.join('..', 'raw_data', 'levels', f"{level_prefix}.txt")
    if os.path.exists(single_file):
        files.insert(0, single_file)

    if not files:
        return 0, []

    all_words = []
    level_from_prefix = level_prefix.upper() if level_prefix.upper() in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] else None

    # Parse each file
    for file_path in files:
        if os.path.getsize(file_path) == 0:
            print(f"  {os.path.basename(file_path):20} -> [EMPTY FILE]")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            parser = GermanWordParser()
            parser.feed(html_content)

            # Fill in missing levels
            for word_entry in parser.words:
                if not word_entry.get('level') or word_entry['level'] == '':
                    word_entry['level'] = level_from_prefix or 'Unknown'

            all_words.extend(parser.words)
            print(f"  {os.path.basename(file_path):20} -> {len(parser.words):4} words")
        except Exception as e:
            print(f"  [ERROR] {os.path.basename(file_path):20} -> {str(e)}")

    # Remove duplicates based on word and translation
    seen = set()
    unique_words = []
    duplicates = 0
    for word_entry in all_words:
        key = (word_entry['word'], word_entry['translation'])
        if key not in seen:
            seen.add(key)
            unique_words.append(word_entry)
        else:
            duplicates += 1

    # Create output data structure
    output_data = {
        'words': unique_words,
        'total_count': len(unique_words),
        'level': level_from_prefix or 'Unknown'
    }

    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    if duplicates > 0:
        print(f"  [INFO] Removed {duplicates} duplicate entries")

    return len(unique_words), files

def main():
    levels = ['A1', 'A2', 'B1', 'B2']

    print("Processing German word files...")
    print("=" * 60)

    total_words = 0

    for level in levels:
        output_file = os.path.join('..', 'processed_data', 'by_level', f"german_words_{level}.json")
        print(f"\n{level} Level:")
        count, files = parse_files_for_level(level, output_file)

        if count > 0:
            total_words += count
            print(f"  [TOTAL] {len(files)} file(s) -> {output_file:25} ({count:4} unique words)")
        else:
            print(f"  [NO FILES FOUND]")

    print("\n" + "=" * 60)
    print(f"Total words processed: {total_words}")

if __name__ == "__main__":
    main()
