#!/usr/bin/env python3
"""
Reformat nouns to put article first.

Changes "Apfel, der" to "der Apfel"
Changes "Nähe, die" to "die Nähe"
Changes "Glas, das" to "das Glas"
"""

import json
import os
import re

def reformat_noun(german_word):
    """
    Reformat a German noun from "Noun, article" to "article Noun"

    Args:
        german_word: String like "Apfel, der" or "Nähe, die"

    Returns:
        Reformatted string like "der Apfel" or "die Nähe"
    """
    # Check if word contains comma (noun with article)
    if ',' not in german_word:
        return german_word

    # Split on comma
    parts = [part.strip() for part in german_word.split(',')]

    if len(parts) != 2:
        return german_word  # Not in expected format

    noun, article = parts

    # Check if second part is an article
    if article.lower() in ['der', 'die', 'das']:
        # Reformat to "article Noun"
        return f"{article} {noun}"

    # Not a noun format, return unchanged
    return german_word

def reformat_level_file(filepath):
    """Reformat nouns in a single level file"""

    # Load file
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    reformatted_count = 0

    # Process each word
    for word_entry in data['words']:
        # Only reformat nouns
        if word_entry.get('word_type') == 'Noun':
            original = word_entry['word']
            reformatted = reformat_noun(original)

            if original != reformatted:
                word_entry['word'] = reformatted
                reformatted_count += 1

    # Save back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return reformatted_count

def main():
    print("""
==================================================================
          Reformat Nouns (Article First)
==================================================================
""")

    # Process by_level files
    by_level_dir = os.path.join('..', 'processed_data', 'by_level')

    level_files = [
        'german_words_A1.json',
        'german_words_A2.json',
        'german_words_B1.json',
        'german_words_B2.json',
        'german_words_C1.json',
        'german_words_C2.json'
    ]

    print("\nReformatting nouns in by_level files...")
    print("=" * 70)

    total_reformatted = 0

    for filename in level_files:
        filepath = os.path.join(by_level_dir, filename)

        if not os.path.exists(filepath):
            print(f"\n[SKIP] {filename} not found")
            continue

        count = reformat_level_file(filepath)
        total_reformatted += count

        print(f"\n{filename}:")
        print(f"  Reformatted: {count} nouns")

    print("\n" + "=" * 70)
    print(f"Total nouns reformatted: {total_reformatted}")
    print("\nExample transformations:")
    print("  'Apfel, der'  -> 'der Apfel'")
    print("  'Nähe, die'   -> 'die Nähe'")
    print("  'Glas, das'   -> 'das Glas'")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
