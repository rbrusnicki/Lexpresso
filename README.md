# Lexpresso

A German language learning web application featuring spaced repetition and card matching exercises. Learn German vocabulary through interactive matching games organized by CEFR levels (A1-C2).

## Features

- **Spaced Repetition System**: Three-pool learning algorithm (To Learn, Learning, Learned) that optimizes word retention
- **Card Matching Game**: Duolingo-style matching interface with 5 pairs per round
- **Progress Tracking**: User statistics including daily goals, accuracy, and learning streaks
- **Multi-User Support**: Individual user accounts with persistent progress storage
- **CEFR Organized**: Vocabulary organized by Common European Framework levels (A1-C2)
- **Gender Color Coding**: Visual indicators for German noun genders (masculine/feminine/neutral)
- **13,483 Word Pairs**: Comprehensive vocabulary database from 6,107 German word entries

## Quick Start

### 1. Start the Server

```bash
python server.py
```

The server will display URLs for local and network access:
- Local: http://localhost:8000
- Network: http://YOUR_IP:8000 (for smartphone access)

### 2. Open in Browser

Navigate to the displayed URL and create a new user account by entering a username.

### 3. Start Learning

Match German words with their English translations. The app tracks your progress and adapts to your learning pace.

## How It Works

### Learning System

**Three-Pool Algorithm:**

1. **To Learn**: New words not yet practiced
2. **Learning**: Words being actively practiced (max 50 at a time)
3. **Learned**: Mastered words (3 consecutive correct answers)

**Word Selection Logic:**
- Learning pool < 50: System selects new words from "To Learn" (frequency-sorted)
- Learning pool = 50: System resamples from the "Learning" pool (weighted random)
- After mastery: System reviews learned words (weighted random) and introduces new ones

### Game Mechanics

- 5 word pairs displayed per round (10 cards total)
- Cards are independently shuffled for left and right columns
- After 2 correct matches, new words appear
- Anti-ambiguity system prevents duplicate or conflicting words on screen
- Fast-clicking supported with parallel animations

### Progress Tracking

**Daily Goal**: Learn 50 new words per day

**Statistics Tracked:**
- Words in each pool (To Learn, Learning, Learned)
- Daily accuracy percentage
- Total attempts, correct, and incorrect answers
- Individual word statistics (streak, total correct/incorrect, last seen)

## Technical Details

### Architecture

**Frontend:**
- `index.html`: Main application interface
- `styles.css`: Styling and animations
- `game.js`: Game logic and card management
- `learning-system.js`: Spaced repetition algorithm
- `user-manager.js`: User authentication and data persistence

**Backend:**
- `server.py`: Python HTTP server with API endpoints
- File-based user data storage in `user_stats/`

**Data:**
- `processed_data/by_level_expanded/`: Vocabulary organized by CEFR level
- Word database includes frequency, word type, and level information

### API Endpoints

- `GET /api/load_user?username={name}`: Load user data
- `POST /api/save_user`: Save user progress
- `GET /api/list_users`: Get all registered users

### Data Storage

User progress is saved to `user_stats/{username}.json` after every answer:

```json
{
  "username": "learner",
  "current_level": "A1",
  "words": {
    "haben|to have": {
      "status": "learning",
      "correct_streak": 2,
      "total_correct": 8,
      "total_incorrect": 2,
      "last_seen": "2025-10-17T12:34:56Z"
    }
  },
  "daily_stats": {
    "2025-10-17": {
      "words_learned": 12,
      "total_attempts": 150,
      "correct": 135,
      "incorrect": 15
    }
  }
}
```

## Network Access

To access from smartphone on the same WiFi network:

1. Start the server on your computer
2. Note the network IP displayed in the console (e.g., http://192.168.1.100:8000)
3. Ensure firewall allows port 8000 (Windows Firewall rule may be needed)
4. Open the network URL on your smartphone browser

## Requirements

- Python 3.6 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No external dependencies (uses Python standard library only)

## Project Structure

```
Lexpresso/
├── index.html              # Main application page
├── styles.css              # Styling and animations
├── game.js                 # Game controller and UI
├── learning-system.js      # Spaced repetition algorithm
├── user-manager.js         # User authentication
├── server.py               # Backend API server
├── manage_users.py         # User management utilities
├── user_stats/             # User progress files
├── processed_data/         # Vocabulary database
│   └── by_level_expanded/  # Word pairs by CEFR level
└── scripts/                # Data processing utilities

```

## User Management

**Create Account**: Enter username on login screen

**Export Data**: Menu > Export User Data (downloads JSON file)

**Import Data**: Menu > Import User Data (restores from JSON file)

**Switch Users**: Logout and login with different username

## Development

The vocabulary database was generated from raw HTML files containing German-English word pairs. The processing pipeline:

1. Parses raw word lists by CEFR level
2. Adds word type information (Noun, Verb, Adjective, etc.)
3. Rebalances and splits levels by frequency
4. Expands comma-separated entries into individual pairs
5. Organizes by level and word type

See `scripts/` directory for data processing tools.

## License

This project is provided as-is for educational purposes.
