# Lexpresso Complete Behavior Specification

This document describes EXACTLY how the app should behave in all situations.

---

## Initial State

### On Page Load
1. Always show login screen (no auto-login)
2. User must enter username to proceed

### After Login
1. Hide login screen, show main app
2. Display username in top right
3. Load word data for current level (default: A1)
4. Display stats panel:
   - Today's Goal: 0 / 50
   - Learning: 0
   - Learned: 0
   - Accuracy: 0%
5. Initialize game with 5 pairs (10 cards total)

---

## Learning Pool Logic

### Simple Two-State System

**State 1: Pool < 50 (Building)**
- **Word selection:** ALWAYS pick from `to_learn`
- **After 2 correct matches:** Add up to 2 NEW words from `to_learn` (respecting cap)
- Example: Pool at 49 → add 1 word → Pool at 50

**State 2: Pool = 50 (Maintenance)**
- **Word selection:** ALWAYS pick from `learning` (weighted random)
- **After 2 correct matches:** Re-show 2 words from `learning` pool
- Pool stays at 50

**Graduation Event (word reaches 3 consecutive correct):**
1. Word moves: learning → learned (pool: 50 → 49)
2. Fill the 2 empty spots (from the 2 matches):
   - **IF learned pool not empty:** Show 1 learned word for review (weighted random)
   - **Always:** Add new word(s) from `to_learn` to fill remaining spots
3. This ensures we always maintain 5 pairs on screen
4. Learning pool: 49 → 50 (or 49 → 51 if review fails later)

---

## Word Status Transitions

### To Learn → Learning
**Trigger:** First correct answer
**What happens:**
- Status changes: to_learn → learning
- correct_streak: 0 → 1
- total_correct: 0 → 1
- last_seen: updated to now

### Learning → Learned
**Trigger:** 3 consecutive correct answers
**What happens:**
- Status changes: learning → learned
- correct_streak: stays at 3+ (continues counting)
- learned_date: set to current date
- Daily stats: words_learned +1
- Today's Goal updates: e.g., 5/50 → 6/50
- **IMMEDIATELY refill learning pool with 1 new word**

### Learned → Learning
**Trigger:** Any incorrect answer during review
**What happens:**
- Status changes: learned → learning
- learned_date: reset to null
- correct_streak: reset to 0
- Daily stats: words_learned -1
- Today's Goal updates: e.g., 6/50 → 5/50
- Learning pool grows by 1 (temporarily)

---

## Answering Pairs

### Correct Match
1. Cards flash green with pulse animation (500ms)
2. Cards fade out (300ms)
3. Remove matched word from currentWords array
4. Update stats:
   - correct_streak +1
   - total_correct +1
   - last_seen updated
5. Check for status change (to_learn→learning or learning→learned)
6. Update UI stats panel
7. Increment pending matches counter
8. If pending matches >= 2 OR status change to learned:
   - Add new words (following pool cap rules)
   - Reset pending matches to 0

### Incorrect Match
1. Cards flash red with shake animation (500ms)
2. Cards return to normal state
3. Cards can be selected again
4. Update stats:
   - correct_streak: reset to 0
   - total_incorrect +1
   - last_seen updated
5. Check for status change (learned→learning)
6. Update UI stats panel
7. No word replacement (cards stay on screen)

---

## Card Replacement Logic

**Normal flow (after 2 correct matches):**
- If pool < 50: Add up to 2 NEW words from `to_learn` (respect cap)
  - New words selected by frequency (higher frequency = more common = learn first)
- If pool = 50: Re-show 2 words from `learning` pool (weighted random selection)
  - Weighted random: lower streak = higher probability

**Graduation flow (word moves to learned):**
- Always fill ALL empty spots (usually 2 from the 2 matches)
- Priority: 1 learned word for review (weighted random if any exist), then fill remaining with NEW words from `to_learn`
- Learned review selection: lower streak = higher probability
- Example: 1 learned review + 1 new word = 2 spots filled
- Example: 0 learned + 2 new words = 2 spots filled

---

## Card Display Rules

### Initial Display (5 Pairs)
1. Select 5 unique words (no German duplicates, no English duplicates, no original_id conflicts)
2. Shuffle German words randomly for right column
3. Shuffle English words independently for left column
4. Display in 5x2 grid (5 rows, 2 columns: left=English, right=German)

### Filling Empty Spots (After 2 Matches)
1. Find empty spot positions (cards with opacity=0)
2. Get words to show (new or from learning pool)
3. Shuffle words for left column independently
4. Shuffle words for right column independently
5. Replace empty cards with new cards
6. **Key:** Old cards stay in their positions, only empty spots are filled

### Anti-Ambiguity Rules (ALWAYS ENFORCED)
**Never allow these on screen simultaneously:**
1. Same German word twice (e.g., "die" and "die")
2. Same English word twice (e.g., "the" and "the")
3. Words from conflicting original entries:
   - Entry 1: "der, die, das|the"
   - Entry 2: "der, die, das|who"
   - ❌ Cannot show pairs from both entries together

**Checks applied:**
- `usedDisplayWords.germanWords` - actual German words on screen
- `usedDisplayWords.englishWords` - actual English words on screen
- `wouldCreateAmbiguity()` - checks original entry conflicts

---

## Daily Goal

### Goal: Learn 50 New Words Per Day
**"Learned" means:** Word moved to learned status today (3 consecutive correct)

**What happens at 50 words:**
- Stats continue to track progress beyond 50 (e.g., 52/50, 60/50)
- No completion screen or forced stop
- User can continue learning indefinitely
- Next day: Counter resets to 0/50
- The 50 word goal is a target, not a limit

---

## Statistics Display

### Stats Panel (Real-Time Updates)
**Today's Goal:** `{words_learned_today} / 50`
- Only counts words that moved to learned TODAY

**Learning:** `{count of words with status='learning'}`
- Target: ~50 words

**Learned:** `{count of words with status='learned'}`
- All words ever mastered (not just today)

**Accuracy:** `{(correct / total_attempts) * 100}%`
- Today's accuracy percentage

### Detailed Stats (Menu → View Statistics)
Shows:
- Username
- Current Level
- Total Words Tracked
- Pool Distribution (To Learn, Learning, Learned)
- Today's Progress (Words Learned, Attempts, Correct, Incorrect, Accuracy)

---

## Data Persistence

### When Data Saves
**After EVERY answer (correct or incorrect):**
1. Update word stats in memory
2. Save to server file: `user_stats/{username}.json`
3. Save to localStorage (backup)

### What Gets Saved
**Per word:**
- status (to_learn, learning, learned)
- correct_streak
- total_correct
- total_incorrect
- last_seen (timestamp)
- learned_date (date or null)
- frequency, level, word_type (from original data)

**Per day:**
- words_learned (count moved to learned today)
- total_attempts
- correct
- incorrect
- session_start (timestamp)

**User info:**
- username
- displayName
- created_date
- current_level
- total_sessions
- settings (daily_goal, learning_pool_size)

---

## Fast Clicking Support

### User Can Click Rapidly
**No waiting for animations:**
- User selects pair 1 → animation starts
- User can immediately select pair 2 (don't wait)
- Animations play independently

**Protected cards (cannot click):**
- Cards with class `correct`
- Cards with class `incorrect`
- Cards with class `removing`
- Cards with `opacity='0'`
- Cards with `pointerEvents='none'`

**All other cards:** Clickable at any time

---

## Edge Cases

### No More Available Words (Conflict Resolution)
**If all available words create conflicts:**
1. Don't add new words
2. Leave empty spots empty
3. Continue with fewer pairs on screen
4. Game continues normally

### Learning Pool Temporarily > 50
**Happens when:** Learned word fails review
**Behavior:**
- Learning pool: 50 → 51
- Next selections: Only from learning pool (no new words)
- Eventually corrects when a word graduates

### Learning Pool < 5 Words on Screen
**Example:** Learning pool = 3 words
- Can only show 3 pairs (not 5)
- Rest must come from to_learn
- Acceptable: mix of learning and new words

---

## Auto-Select Feature

### Left Card Auto-Selection
**Enabled by default** (toggle in Menu → "Auto-select left words")

**Behavior:**
- Automatically selects left (English) cards in cycle: 1→2→3→4→5→1→2→3...
- After correct match, next card is auto-selected for fast clicking
- User can manually click any left card to override
- When disabled: user must manually select both left and right cards

**Cycle Update Logic:**
- Auto-select advances to next position after each selection
- User manual selection updates cycle to position + 1
- Enables rapid gameplay without waiting for animations

## Word Selection Algorithms

### To-Learn Pool (New Words)
**Selection method:** Deterministic, sorted by priority
1. **Frequency** (higher frequency = more common words = learn first)
2. **Never seen** (prioritize words never shown before)
3. **Least recently seen** (oldest last_seen timestamp)

### Learning Pool (Active Practice)
**Selection method:** Weighted random
- Formula: `weight = 1 / (streak + 1)`
- Lower streak = higher weight = higher probability
- Example: streak 0 has 2x probability vs streak 1
- Ensures struggling words appear more often

### Learned Pool (Review)
**Selection method:** Weighted random (only after graduation)
- Formula: `weight = 1 / (streak - threshold + 1)`
- Lower streak (closer to threshold of 3) = higher probability
- Example: streak 3 (just learned) has higher probability than streak 20
- Reviews are only triggered when a word graduates to learned

## Summary of Key Numbers

| Setting | Value |
|---------|-------|
| Learning Pool Cap | 50 words |
| Learned Threshold | 3 consecutive correct |
| Daily Goal | 50 words (target, not limit) |
| Pairs on Screen | 5 (10 cards) |
| Matches Before Refresh | 2 |
| Word Selection | Pool < 50: from `to_learn` (frequency-sorted)<br>Pool = 50: from `learning` (weighted random)<br>After graduation: review `learned` (weighted random), then grab from `to_learn` |

---

**If the actual behavior differs from this document, THE CODE IS WRONG.**
