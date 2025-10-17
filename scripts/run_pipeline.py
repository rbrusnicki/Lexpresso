#!/usr/bin/env python3
"""
Main pipeline script for processing German word data.

This script orchestrates the complete data processing pipeline:
1. Parse raw HTML files and combine words by level
2. Add word types (noun, verb, adjective, etc.) to the data
3. Split and rebalance levels for optimal learning progression
4. Organize words by word type for redundant access

Usage:
    python run_pipeline.py
"""

import os
import sys
import subprocess

def run_script(script_name, description):
    """Run a Python script and print status"""
    print("\n" + "=" * 70)
    print(f"STEP: {description}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, script_name],
        capture_output=False,
        text=True
    )

    if result.returncode != 0:
        print(f"\n[ERROR] {script_name} failed with return code {result.returncode}")
        sys.exit(1)

    print(f"\n[SUCCESS] {description} completed!")
    return result.returncode

def main():
    print("""
==================================================================
     German Word Learning App - Data Processing Pipeline
==================================================================
""")

    # Change to scripts directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    try:
        # Step 1: Parse and combine word files by level
        run_script(
            'parse_combined_words.py',
            'Parsing and combining words by level (A1, A2, B1, B2)'
        )

        # Step 2: Add word types
        run_script(
            'add_word_types.py',
            'Adding word types (Noun, Verb, Adjective, etc.)'
        )

        # Step 3: Split and rebalance levels
        run_script(
            'split_levels.py',
            'Rebalancing A1/A2 and splitting B1/B2/C1/C2'
        )

        # Step 4: Reformat nouns (article first)
        run_script(
            'reformat_nouns.py',
            'Reformatting nouns to put article first (der Apfel)'
        )

        # Step 5: Organize by word type
        run_script(
            'organize_by_word_type.py',
            'Organizing words by word type (Noun, Verb, etc.)'
        )

        # Step 6: Expand word pairs (split comma-separated values)
        run_script(
            'expand_pairs.py',
            'Expanding word pairs by splitting multi-word entries'
        )

        print("\n" + "=" * 70)
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nLevel files created in processed_data/by_level/:")
        print("  - german_words_A1.json  ( 767 multi-word entries)")
        print("  - german_words_A2.json  ( 768 multi-word entries)")
        print("  - german_words_B1.json  ( 851 multi-word entries)")
        print("  - german_words_B2.json  ( 851 multi-word entries)")
        print("  - german_words_C1.json  (1435 multi-word entries)")
        print("  - german_words_C2.json  (1435 multi-word entries)")
        print("\nExpanded level files in processed_data/by_level_expanded/:")
        print("  - german_words_A1.json  (2294 individual pairs)")
        print("  - german_words_A2.json  (2314 individual pairs)")
        print("  - german_words_B1.json  (2891 individual pairs)")
        print("  - german_words_B2.json  (2877 individual pairs)")
        print("  - german_words_C1.json  (4749 individual pairs)")
        print("  - german_words_C2.json  (4593 individual pairs)")
        print("\nWord type files created in processed_data/by_word_type/:")
        print("  - Multi-word entries organized by type")
        print("\nExpanded word type files in processed_data/by_word_type_expanded/:")
        print("  - Individual pairs organized by type (19,718 total pairs)")
        print("\nAll words now include:")
        print("  * German word with articles")
        print("  * English translation")
        print("  * CEFR level (A1-C2)")
        print("  * Frequency rating (1-5)")
        print("  * Word type (Noun, Verb, etc.)")
        print("\nBackup files saved in backups/")
        print("\n" + "=" * 70)

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
