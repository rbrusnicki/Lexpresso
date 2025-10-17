#!/usr/bin/env python3
"""
User Management Utility for Lexpresso
Manage user data files in user_stats/
"""

import json
import os
import argparse
from datetime import datetime

USER_STATS_DIR = 'user_stats'

def load_user(username):
    """Load user data from file"""
    filepath = os.path.join(USER_STATS_DIR, f'{username}.json')
    if not os.path.exists(filepath):
        print(f"User '{username}' not found")
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_user(user_data):
    """Save user data to file"""
    username = user_data['username']
    filepath = os.path.join(USER_STATS_DIR, f'{username}.json')

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved {username}")

def show_stats(username):
    """Show user statistics"""
    user_data = load_user(username)
    if not user_data:
        return

    words = user_data.get('words', {})

    # Count by status
    to_learn = sum(1 for w in words.values() if w.get('status') == 'to_learn')
    learning = sum(1 for w in words.values() if w.get('status') == 'learning')
    learned = sum(1 for w in words.values() if w.get('status') == 'learned')

    print(f"\n{'='*50}")
    print(f"Stats for {user_data.get('displayName', username)}")
    print(f"{'='*50}")
    print(f"Level: {user_data.get('current_level', 'A1')}")
    print(f"Total words tracked: {len(words)}")
    print(f"\nPool Distribution:")
    print(f"  To Learn:  {to_learn:4d}")
    print(f"  Learning:  {learning:4d}")
    print(f"  Learned:   {learned:4d}")

    # Today's stats
    today = datetime.now().strftime('%Y-%m-%d')
    daily_stats = user_data.get('daily_stats', {})
    if today in daily_stats:
        stats = daily_stats[today]
        print(f"\nToday's Progress:")
        print(f"  Words learned: {stats.get('words_learned', 0)}")
        print(f"  Attempts: {stats.get('total_attempts', 0)}")
        print(f"  Correct: {stats.get('correct', 0)}")
        print(f"  Incorrect: {stats.get('incorrect', 0)}")

        if stats.get('total_attempts', 0) > 0:
            accuracy = (stats.get('correct', 0) / stats.get('total_attempts', 1)) * 100
            print(f"  Accuracy: {accuracy:.1f}%")

    print(f"{'='*50}\n")

def reset_learning_pool(username, count):
    """Reset specified number of learning words back to to_learn"""
    user_data = load_user(username)
    if not user_data:
        return

    words = user_data.get('words', {})

    # Find all learning words
    learning_words = [(word_id, stats) for word_id, stats in words.items()
                      if stats.get('status') == 'learning']

    if len(learning_words) == 0:
        print("No learning words to reset")
        return

    # Reset the specified count
    to_reset = min(count, len(learning_words))

    for i in range(to_reset):
        word_id, stats = learning_words[i]
        stats['status'] = 'to_learn'
        stats['correct_streak'] = 0
        stats['total_correct'] = 0
        stats['total_incorrect'] = 0
        stats['last_seen'] = None

    save_user(user_data)
    print(f"✓ Reset {to_reset} words from learning to to_learn")
    print(f"  Learning pool: {len(learning_words)} → {len(learning_words) - to_reset}")

def list_users():
    """List all users"""
    if not os.path.exists(USER_STATS_DIR):
        print("No users found")
        return

    users = [f.replace('.json', '') for f in os.listdir(USER_STATS_DIR)
             if f.endswith('.json')]

    if not users:
        print("No users found")
        return

    print(f"\n{'='*50}")
    print("Users:")
    print(f"{'='*50}")
    for user in sorted(users):
        print(f"  {user}")
    print(f"{'='*50}\n")

def main():
    parser = argparse.ArgumentParser(description='Manage Lexpresso user data')
    parser.add_argument('--stats', metavar='USERNAME', help='Show user statistics')
    parser.add_argument('--reset-learning', metavar='USERNAME',
                       help='Reset learning pool words back to to_learn')
    parser.add_argument('--count', type=int, default=100,
                       help='Number of words to reset (default: 100)')
    parser.add_argument('--list', action='store_true', help='List all users')

    args = parser.parse_args()

    if args.list:
        list_users()
    elif args.stats:
        show_stats(args.stats)
    elif args.reset_learning:
        reset_learning_pool(args.reset_learning, args.count)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
