# User Statistics

User progress data is saved automatically to JSON files in this folder.

## How It Works

- **Automatic saving**: Every time you answer a word correctly or incorrectly, your data is saved to a file
- **File format**: `{username}.json` (e.g., `brusk.json`)
- **Backup**: Data is also saved to browser localStorage as a fallback
- **Migration**: If you have old localStorage data, it will be automatically migrated to files on first login

## Data Structure

Each user file contains:
```json
{
  "username": "brusk",
  "displayName": "Brusk",
  "created_date": "2025-10-17",
  "current_level": "A1",
  "total_sessions": 0,
  "words": {
    "word_id": {
      "status": "learning",
      "correct_streak": 3,
      "total_correct": 5,
      "total_incorrect": 2,
      "last_seen": "2025-10-17T10:00:00Z",
      "learned_date": null,
      "frequency": 5,
      "level": "A1",
      "word_type": "Noun"
    }
  },
  "daily_stats": {
    "2025-10-17": {
      "words_learned": 12,
      "total_attempts": 50,
      "correct": 42,
      "incorrect": 8,
      "session_start": "2025-10-17T09:00:00Z"
    }
  },
  "settings": {
    "daily_goal": 50,
    "learning_pool_size": 50
  }
}
```

## Word Status

- **to_learn**: Words not yet seen
- **learning**: Words being actively practiced (max 50)
- **learned**: Words mastered (10+ consecutive correct answers)

## Managing Your Data

### Reset Learning Pool
If your learning pool is too large, use the management script:
```bash
python manage_users.py --reset-learning brusk --count 100
```

### View Stats
```bash
python manage_users.py --stats brusk
```

### Backup
Just copy the JSON files to another location or commit them to version control.

### Restore
Replace the JSON files with your backup.
