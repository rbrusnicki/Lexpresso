import json
import shutil
import os

def split_by_count(input_file, output_file1, output_file2, level1, level2, split_ratio=0.5):
    """
    Split a JSON file into two based on word count.
    Words are sorted by frequency (descending), then split at the ratio.
    Default: Top 50% go to level1, bottom 50% go to level2
    """

    # Load the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Sort words by frequency (descending) to get most frequent first
    sorted_words = sorted(data['words'], key=lambda x: x['frequency'], reverse=True)

    # Calculate split point
    split_index = int(len(sorted_words) * split_ratio)

    # Split words
    words_level1 = sorted_words[:split_index]
    words_level2 = sorted_words[split_index:]

    # Update levels
    for word in words_level1:
        word['level'] = level1

    for word in words_level2:
        word['level'] = level2

    # Create output data
    output_data1 = {
        'words': words_level1,
        'total_count': len(words_level1),
        'level': level1
    }

    output_data2 = {
        'words': words_level2,
        'total_count': len(words_level2),
        'level': level2
    }

    # Write output files
    with open(output_file1, 'w', encoding='utf-8') as f:
        json.dump(output_data1, f, ensure_ascii=False, indent=2)

    with open(output_file2, 'w', encoding='utf-8') as f:
        json.dump(output_data2, f, ensure_ascii=False, indent=2)

    # Calculate frequency ranges for reporting
    freq1_max = max([w['frequency'] for w in words_level1]) if words_level1 else 0
    freq1_min = min([w['frequency'] for w in words_level1]) if words_level1 else 0
    freq2_max = max([w['frequency'] for w in words_level2]) if words_level2 else 0
    freq2_min = min([w['frequency'] for w in words_level2]) if words_level2 else 0

    return len(words_level1), len(words_level2), (freq1_max, freq1_min), (freq2_max, freq2_min)

def main():
    print("Rebalancing and splitting levels by frequency...")
    print("=" * 60)

    # First, combine A1 and A2, then split them evenly
    print("\nRebalancing A1 + A2")
    print("  Combining A1 and A2, then splitting evenly by frequency")

    # Backup original files
    shutil.copy('german_words_A1.json', 'german_words_A1_backup.json')
    shutil.copy('german_words_A2.json', 'german_words_A2_backup.json')
    print("\n  Backups created:")
    print("    - german_words_A1_backup.json")
    print("    - german_words_A2_backup.json")

    # Load both A1 and A2
    with open('german_words_A1.json', 'r', encoding='utf-8') as f:
        a1_data = json.load(f)
    with open('german_words_A2.json', 'r', encoding='utf-8') as f:
        a2_data = json.load(f)

    # Combine all words
    all_a_words = a1_data['words'] + a2_data['words']
    total_a_words = len(all_a_words)

    # Sort by frequency (descending)
    sorted_a_words = sorted(all_a_words, key=lambda x: x['frequency'], reverse=True)

    # Split 50/50
    split_index = len(sorted_a_words) // 2
    new_a1_words = sorted_a_words[:split_index]
    new_a2_words = sorted_a_words[split_index:]

    # Update levels
    for word in new_a1_words:
        word['level'] = 'A1'
    for word in new_a2_words:
        word['level'] = 'A2'

    # Calculate frequency ranges
    a1_freq_max = max([w['frequency'] for w in new_a1_words])
    a1_freq_min = min([w['frequency'] for w in new_a1_words])
    a2_freq_max = max([w['frequency'] for w in new_a2_words])
    a2_freq_min = min([w['frequency'] for w in new_a2_words])

    # Save new A1 and A2
    with open('german_words_A1.json', 'w', encoding='utf-8') as f:
        json.dump({
            'words': new_a1_words,
            'total_count': len(new_a1_words),
            'level': 'A1'
        }, f, ensure_ascii=False, indent=2)

    with open('german_words_A2.json', 'w', encoding='utf-8') as f:
        json.dump({
            'words': new_a2_words,
            'total_count': len(new_a2_words),
            'level': 'A2'
        }, f, ensure_ascii=False, indent=2)

    print(f"\n  Results:")
    print(f"    A1: {len(new_a1_words):4} words (frequency {a1_freq_max}-{a1_freq_min})")
    print(f"    A2: {len(new_a2_words):4} words (frequency {a2_freq_max}-{a2_freq_min})")
    print(f"    Total: {total_a_words:4} words")

    print("\n" + "=" * 60)

    # Split B2 into C1 and C2 (50/50 by count, sorted by frequency)
    print("\nSplitting B2 -> C1 + C2")
    print("  Top 50% (most frequent) -> C1")
    print("  Bottom 50% (less frequent) -> C2")

    c1_count, c2_count, c1_freq_range, c2_freq_range = split_by_count(
        'german_words_B2.json',
        'german_words_C1.json',
        'german_words_C2.json',
        'C1',
        'C2',
        0.5
    )

    print(f"\n  Results:")
    print(f"    C1: {c1_count:4} words (frequency {c1_freq_range[0]}-{c1_freq_range[1]})")
    print(f"    C2: {c2_count:4} words (frequency {c2_freq_range[0]}-{c2_freq_range[1]})")
    print(f"    Total: {c1_count + c2_count:4} words")

    # Split B1 into B1 and B2
    print("\n" + "=" * 60)
    print("\nSplitting old B1 -> new B1 + new B2")
    print("  Top 50% (most frequent) -> B1")
    print("  Bottom 50% (less frequent) -> B2")

    # First, backup the original B1
    shutil.copy('german_words_B1.json', 'german_words_B1_backup.json')
    print("\n  Backup created: german_words_B1_backup.json")

    b1_count, b2_count, b1_freq_range, b2_freq_range = split_by_count(
        'german_words_B1_backup.json',
        'german_words_B1.json',
        'german_words_B2.json',
        'B1',
        'B2',
        0.5
    )

    print(f"\n  Results:")
    print(f"    B1: {b1_count:4} words (frequency {b1_freq_range[0]}-{b1_freq_range[1]})")
    print(f"    B2: {b2_count:4} words (frequency {b2_freq_range[0]}-{b2_freq_range[1]})")
    print(f"    Total: {b1_count + b2_count:4} words")

    print("\n" + "=" * 60)
    print("Done! All level files created/updated:")
    print("  - german_words_A1.json")
    print("  - german_words_A2.json")
    print("  - german_words_B1.json")
    print("  - german_words_B2.json")
    print("  - german_words_C1.json")
    print("  - german_words_C2.json")
    print("\nBackup files saved:")
    print("  - german_words_A1_backup.json")
    print("  - german_words_A2_backup.json")
    print("  - german_words_B1_backup.json")

if __name__ == "__main__":
    main()
