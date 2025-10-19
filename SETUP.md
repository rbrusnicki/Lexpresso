# Lexpresso Setup Guide

## Starting the Server

Instead of using `python -m http.server`, use the new backend server:

```bash
python server.py
```

This will:
- Start the web server on http://localhost:8000
- Automatically save user data to `user_stats/{username}.json` files
- Provide real-time feedback in the console

## Using the App

1. Open http://localhost:8000 in your browser
2. Login with your username (e.g., "Brusk")
3. Your progress is automatically saved to files after every answer!

## Managing Your Data

### View Your Stats
```bash
python manage_users.py --stats brusk
```

### Reset Learning Pool (if it gets too large)
```bash
# Reset 100 words from learning back to to_learn
python manage_users.py --reset-learning brusk --count 100
```

### List All Users
```bash
python manage_users.py --list
```

## Where is my data?

Your data is saved primarily to:
1. **Files**: `user_stats/{username}.json` (primary storage, persistent, visible, editable)
2. **Browser localStorage**: Fallback only if server connection fails

## Backing Up

Just copy the files in `user_stats/` folder or commit them to git!

## Migrating Old Data

If you have old data in localStorage, it will be automatically migrated to files the first time you login with the new server running.
