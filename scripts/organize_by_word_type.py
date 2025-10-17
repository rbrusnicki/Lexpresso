#!/usr/bin/env python3
"""
Organize processed word data by word type instead of level.

This script reads all level-based JSON files and creates parallel
organization by word type (Noun, Verb, Adjective, etc.)
"""

import json
import os
from collections import defaultdict

def load_all_words():
    """Load all words from level-based JSON files"""
    processed_data_dir = os.path.join('..', 'processed_data', 'by_level')

    level_files = [
        'german_words_A1.json',
        'german_words_A2.json',
        'german_words_B1.json',
        'german_words_B2.json',
        'german_words_C1.json',
        'german_words_C2.json'
    ]

    all_words = []

    print("Loading words from level files...")
    print("=" * 60)

    for filename in level_files:
        filepath = os.path.join(processed_data_dir, filename)
        if not os.path.exists(filepath):
            print(f"  [SKIP] {filename} not found")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_words.extend(data['words'])
            print(f"  Loaded {len(data['words']):4} words from {filename}")

    print(f"\n  Total words loaded: {len(all_words)}")
    return all_words

def organize_by_word_type(all_words):
    """Group words by their word_type field"""
    words_by_type = defaultdict(list)

    for word in all_words:
        word_type = word.get('word_type', 'Article')
        words_by_type[word_type].append(word)

    return words_by_type

def save_by_word_type(words_by_type):
    """Save organized words to separate JSON files by type"""
    output_dir = os.path.join('..', 'processed_data', 'by_word_type')

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("Creating word type files...")
    print("=" * 60)

    # Sort word types alphabetically
    sorted_types = sorted(words_by_type.keys())

    total_words = 0

    for word_type in sorted_types:
        words = words_by_type[word_type]

        # Sort words by level, then by frequency (descending), then alphabetically
        level_order = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
        words.sort(key=lambda w: (
            level_order.get(w['level'], 99),
            -w.get('frequency', 0),
            w['word'].lower()
        ))

        # Create output data
        output_data = {
            'word_type': word_type,
            'words': words,
            'total_count': len(words),
            'level_distribution': {}
        }

        # Calculate level distribution
        level_counts = defaultdict(int)
        for word in words:
            level_counts[word['level']] += 1

        output_data['level_distribution'] = dict(sorted(level_counts.items()))

        # Save to file
        filename = f"{word_type.lower()}s.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n{word_type}s:")
        print(f"  File: by_word_type/{filename}")
        print(f"  Total words: {len(words)}")
        print(f"  Level distribution: {dict(level_counts)}")

        total_words += len(words)

    return output_dir, total_words, len(sorted_types)

def create_index_file(output_dir, words_by_type):
    """Create an index file summarizing all word types"""

    index_data = {
        'summary': {
            'total_words': sum(len(words) for words in words_by_type.values()),
            'total_word_types': len(words_by_type),
            'files_created': len(words_by_type)
        },
        'word_types': {}
    }

    # Add summary for each word type
    for word_type, words in sorted(words_by_type.items()):
        level_counts = defaultdict(int)
        for word in words:
            level_counts[word['level']] += 1

        index_data['word_types'][word_type] = {
            'total_count': len(words),
            'filename': f"{word_type.lower()}s.json",
            'level_distribution': dict(sorted(level_counts.items()))
        }

    # Save index file
    index_path = os.path.join(output_dir, '_index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"Index file created: by_word_type/_index.json")

def main():
    print("""
==================================================================
          Organize Word Data by Word Type
==================================================================
""")

    try:
        # Load all words from level files
        all_words = load_all_words()

        if not all_words:
            print("\n[ERROR] No words loaded. Make sure level files exist.")
            return

        # Organize by word type
        print("\n" + "=" * 60)
        print("Organizing words by type...")
        words_by_type = organize_by_word_type(all_words)
        print(f"Found {len(words_by_type)} word types")

        # Save to files
        output_dir, total_words, num_types = save_by_word_type(words_by_type)

        # Create index file
        create_index_file(output_dir, words_by_type)

        print("\n" + "=" * 60)
        print("ORGANIZATION COMPLETE!")
        print("=" * 60)
        print(f"\nCreated {num_types} word type files in processed_data/by_word_type/")
        print(f"Total words organized: {total_words}")
        print("\nFiles created:")
        for word_type in sorted(words_by_type.keys()):
            count = len(words_by_type[word_type])
            filename = f"{word_type.lower()}s.json"
            print(f"  - {filename:20} ({count:4} words)")

        print("\nEach file includes:")
        print("  * All words of that type across all levels")
        print("  * Sorted by level -> frequency -> alphabetically")
        print("  * Level distribution statistics")
        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
