#!/usr/bin/env python3
"""
Expand word pairs by splitting comma-separated values.

For example:
"der, die, das" = "who, which, this, that"

Becomes 12 pairs:
("der", "who"), ("der", "which"), ("der", "this"), ("der", "that"),
("die", "who"), ("die", "which"), ("die", "this"), ("die", "that"),
("das", "who"), ("das", "which"), ("das", "this"), ("das", "that")
"""

import json
import os
from collections import defaultdict

def expand_word_entry(word_entry):
    """
    Expand a single word entry into multiple pairs.

    For nouns: German side keeps article with noun (e.g., "Apfel, der" stays together)
    For other word types: Split both sides on commas

    Args:
        word_entry: Dictionary with 'word', 'translation', 'level', 'frequency', 'word_type'

    Returns:
        List of expanded word entries
    """
    # Create unique ID for original entry
    original_id = f"{word_entry['word']}|{word_entry['translation']}"

    # Check if this is a noun
    is_noun = word_entry.get('word_type', '') == 'Noun'

    # For nouns, don't split the German word (keep article with noun)
    if is_noun:
        german_parts = [word_entry['word']]  # Keep as single unit
    else:
        german_parts = [part.strip() for part in word_entry['word'].split(',')]

    # Always split English translations by comma
    english_parts = [part.strip() for part in word_entry['translation'].split(',')]

    # Create all combinations
    expanded_entries = []
    for german in german_parts:
        for english in english_parts:
            expanded_entry = {
                'word': german,
                'translation': english,
                'level': word_entry['level'],
                'frequency': word_entry['frequency'],
                'word_type': word_entry['word_type'],
                'original_id': original_id  # Track which original entry this came from
            }
            expanded_entries.append(expanded_entry)

    return expanded_entries

def expand_level_files():
    """Expand all level-based JSON files"""

    input_dir = os.path.join('..', 'processed_data', 'by_level')
    output_dir = os.path.join('..', 'processed_data', 'by_level_expanded')

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    level_files = [
        'german_words_A1.json',
        'german_words_A2.json',
        'german_words_B1.json',
        'german_words_B2.json',
        'german_words_C1.json',
        'german_words_C2.json'
    ]

    print("=" * 70)
    print("Expanding Word Pairs by Level")
    print("=" * 70)

    total_original = 0
    total_expanded = 0

    for filename in level_files:
        input_file = os.path.join(input_dir, filename)

        if not os.path.exists(input_file):
            print(f"\n[SKIP] {filename} not found")
            continue

        # Load original data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Expand all words
        expanded_words = []
        for word_entry in data['words']:
            expanded_entries = expand_word_entry(word_entry)
            expanded_words.extend(expanded_entries)

        # Create output data
        output_data = {
            'words': expanded_words,
            'total_count': len(expanded_words),
            'level': data['level'],
            'original_count': data['total_count']
        }

        # Save to output file
        output_file = os.path.join(output_dir, filename)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n{filename}:")
        print(f"  Original pairs: {data['total_count']:4}")
        print(f"  Expanded pairs: {len(expanded_words):4}")
        print(f"  Expansion ratio: {len(expanded_words) / data['total_count']:.1f}x")

        total_original += data['total_count']
        total_expanded += len(expanded_words)

    print("\n" + "=" * 70)
    print(f"Total original pairs: {total_original}")
    print(f"Total expanded pairs: {total_expanded}")
    print(f"Overall expansion:    {total_expanded / total_original:.1f}x")

    return output_dir

def expand_by_word_type(expanded_level_dir):
    """Create word type organization from expanded pairs"""

    print("\n" + "=" * 70)
    print("Organizing Expanded Pairs by Word Type")
    print("=" * 70)

    # Load all expanded words
    all_words = []

    level_files = [
        'german_words_A1.json',
        'german_words_A2.json',
        'german_words_B1.json',
        'german_words_B2.json',
        'german_words_C1.json',
        'german_words_C2.json'
    ]

    for filename in level_files:
        filepath = os.path.join(expanded_level_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_words.extend(data['words'])

    # Group by word type
    words_by_type = defaultdict(list)
    for word in all_words:
        word_type = word.get('word_type', 'Article')
        words_by_type[word_type].append(word)

    # Create output directory
    output_dir = os.path.join('..', 'processed_data', 'by_word_type_expanded')
    os.makedirs(output_dir, exist_ok=True)

    # Save each word type
    for word_type, words in sorted(words_by_type.items()):
        # Sort by level, frequency, then alphabetically
        level_order = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
        words.sort(key=lambda w: (
            level_order.get(w['level'], 99),
            -w.get('frequency', 0),
            w['word'].lower(),
            w['translation'].lower()
        ))

        # Calculate level distribution
        level_counts = defaultdict(int)
        for word in words:
            level_counts[word['level']] += 1

        # Create output data
        output_data = {
            'word_type': word_type,
            'words': words,
            'total_count': len(words),
            'level_distribution': dict(sorted(level_counts.items()))
        }

        # Save to file
        filename = f"{word_type.lower()}s.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n{word_type}s: {len(words)} pairs")
        print(f"  File: {filename}")
        print(f"  Levels: {dict(level_counts)}")

    # Create index file
    index_data = {
        'summary': {
            'total_words': sum(len(words) for words in words_by_type.values()),
            'total_word_types': len(words_by_type)
        },
        'word_types': {}
    }

    for word_type, words in sorted(words_by_type.items()):
        level_counts = defaultdict(int)
        for word in words:
            level_counts[word['level']] += 1

        index_data['word_types'][word_type] = {
            'total_count': len(words),
            'filename': f"{word_type.lower()}s.json",
            'level_distribution': dict(sorted(level_counts.items()))
        }

    index_path = os.path.join(output_dir, '_index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"Created {len(words_by_type)} word type files")
    print(f"Total expanded pairs: {index_data['summary']['total_words']}")

def main():
    print("""
==================================================================
          Expand Word Pairs (Split Comma-Separated Values)
==================================================================
""")

    try:
        # Expand level files
        expanded_level_dir = expand_level_files()

        # Organize by word type
        expand_by_word_type(expanded_level_dir)

        print("\n" + "=" * 70)
        print("EXPANSION COMPLETE!")
        print("=" * 70)
        print("\nNew folders created:")
        print("  - processed_data/by_level_expanded/")
        print("  - processed_data/by_word_type_expanded/")
        print("\nThese folders contain individual word pairs instead of")
        print("comma-separated multi-word entries.")
        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
