# Lexpresso Core Rules

**READ THIS BEFORE MAKING ANY CHANGES**

These rules define how the app MUST work. Do not break these behaviors.

---

## ⚠️ CRITICAL REQUIREMENT

**USER DATA MUST BE SAVED TO LOCAL FILES**

- Run: `python server.py` (NOT `python -m http.server`)
- Data saves to: `user_stats/{username}.json`
- Files are human-readable, editable JSON
- Browser localStorage is backup only

---

## 1. Learning Pool Management

### Rule 1.1: Learning Pool Size
- The learning pool MUST be capped at **50 words maximum** (configurable via LEARNING_POOL_SIZE)
- When learning pool < 50: **ALWAYS add new words from to_learn** to build it up
- When learning pool = 50: **ONLY resample from learning pool**, NO new words until one graduates to "learned"

### Rule 1.2: Word Selection Logic (SIMPLIFIED)

**Core principle: Simple cap-based logic**

#### When learning pool < 50:
- **100% from to_learn** (always pick new words until we reach 50)
- Selection: frequency-sorted (higher frequency = more common = learn first)
- No mixing, no percentages
- Build up to exactly 50 words

#### When learning pool = 50:
- **100% from learning pool** (resample from the 50 words)
- Selection: weighted random (lower streak = higher probability)
- NO new words added during normal flow
- Only add new word when one graduates to learned

#### When word graduates to learned (3 consecutive correct):
1. Word moves from learning → learned (pool: 50 → 49)
2. **IF learned pool not empty**: Pick 1 word for review (weighted random)
   - User answers the review word
   - If correct: stays in learned, streak +1, pool stays 49
   - If wrong: moves back to learning, pool becomes 50
3. **After review** (or if no learned words): Grab 1 NEW word from to_learn
4. Learning pool back to 50 (or stays 50 if review failed)

### Rule 1.3: Word Progression
- **to_learn** → first correct answer → **learning**
- **learning** → 3 consecutive correct → **learned**
- **learned** → 1 wrong answer → **learning**

---

## 2. Word Selection (Anti-Ambiguity)

### Rule 2.1: No Duplicate Displayed Words
**NEVER show the same German or English word twice on screen**
- Example: Cannot show both (this, die) and (which, die)
- Check: `usedDisplayWords.germanWords` and `usedDisplayWords.englishWords`

### Rule 2.2: No Original Entry Conflicts
**If two original entries share ANY German or English words, cannot use both**
- Entry 1: "der, die, das|the"
- Entry 2: "der, die, das|who"
- Cannot show pairs from both entries simultaneously
- Check: `wouldCreateAmbiguity()` function

### Rule 2.3: Both Checks Required
ALWAYS apply BOTH checks:
1. Displayed word duplicates (actual words on screen)
2. Original entry ambiguity (words from source entries)

---

## 3. Word Selection Algorithms

### Rule 3.1: To-Learn Pool Selection (New Words)
**Method:** Deterministic, sorted by priority
1. **Frequency first** (higher frequency = more common = learn first)
2. **Never seen** (prioritize words where last_seen is null)
3. **Least recently seen** (oldest last_seen timestamp)

### Rule 3.2: Learning Pool Selection (Active Practice)
**Method:** Weighted random selection
- Formula: `weight = 1 / (streak + 1)`
- Lower streak = higher weight = higher selection probability
- Example: word with streak 0 is 2x more likely than streak 1
- Ensures struggling words (lower streak) appear more frequently

### Rule 3.3: Learned Pool Selection (Review Only)
**Method:** Weighted random (only after graduation event)
- Formula: `weight = 1 / (streak - threshold + 1)`
- Lower streak (closer to threshold of 3) = higher probability
- Example: streak 3 (just learned) is more likely than streak 20
- Reviews ONLY triggered when a word graduates to learned (not randomly)

---

## 4. Game Flow

### Rule 4.1: Starting Display
**Always show 5 pairs initially** (10 cards total: 5 left, 5 right)

### Rule 4.2: Card Replacement Timing
**Fill empty spots after every 2 correct matches (respecting learning pool cap)**
- Match 1 → cards disappear, 4 pairs remain
- Match 2 → cards disappear, 3 pairs remain
- **Check learning pool size to decide what to show:**
  - If pool < cap: Fill with NEW words from to_learn (up to 2, respecting cap, frequency-sorted)
  - If pool >= cap: Fill with words from LEARNING pool (re-practice, weighted random, no new words)
- Example with cap=50:
  - Pool=49: add 1 NEW word (50-49=1)
  - Pool=50: add 2 words from LEARNING pool (weighted random re-practice)

### Rule 4.3: Card Position Randomization
**New pairs fill empty spots, but their left-right placement is randomized**
- Old pairs stay in their positions
- New pairs: shuffle English words into empty left spots
- New pairs: shuffle German words independently into empty right spots
- This prevents position-based memorization

### Rule 4.4: Fast Clicking
**User can click next pair immediately, no waiting for animations**
- Cards with classes 'correct', 'incorrect', 'removing' cannot be clicked
- Cards with opacity '0' cannot be clicked
- All other cards are clickable during animations

---

## 5. Data Persistence

### Rule 5.0: MANDATORY FILE STORAGE
**USER DATA MUST BE SAVED TO LOCAL FILES - NOT JUST BROWSER**
- Primary storage: `user_stats/{username}.json` (REQUIRED)
- Browser localStorage: backup only
- **Always run server.py** (not plain http.server) to enable file saving
- Files must be human-readable, editable JSON

### Rule 5.1: Dual Storage
**Save to BOTH locations on every change:**
1. **Server file: `user_stats/{username}.json`** (PRIMARY - MANDATORY)
2. Browser localStorage: backup fallback

### Rule 5.2: Save Triggers
Save after EVERY:
- Correct answer
- Incorrect answer
- Status change (to_learn → learning → learned)

### Rule 5.3: Load Priority
On login:
1. Try server file first (PRIMARY SOURCE)
2. If server fails, use localStorage
3. If localStorage exists but not on server: migrate to server file

### Rule 5.4: Running the Server
**MUST use server.py, NOT python -m http.server**
```bash
python server.py
```
This enables the API endpoints for file saving.

---

## 6. Statistics Tracking

### Rule 6.1: Per-Word Stats
Track for each word:
- `status`: to_learn, learning, learned
- `correct_streak`: consecutive correct (resets to 0 on wrong)
- `total_correct`: lifetime correct count
- `total_incorrect`: lifetime incorrect count
- `last_seen`: timestamp
- `learned_date`: when it moved to learned (or null)

### Rule 6.2: Daily Stats
Track per day:
- `words_learned`: count of words that moved to learned TODAY
- `total_attempts`: all attempts today
- `correct`: correct answers today
- `incorrect`: incorrect answers today

### Rule 6.3: Display Stats
Show in UI:
- Today's Goal: `{words_learned} / 50`
- Learning: count of words with status='learning'
- Learned: count of words with status='learned'
- Accuracy: `(today.correct / today.attempts) * 100%`

---

## 7. Review System

### Rule 7.1: Learned Word Review
**ONLY review learned words after a word graduates to learned** (not randomly)
- When word moves from learning → learned:
  1. Check if learned pool has any words
  2. If yes: pick 1 learned word for review (weighted random)
  3. Show that word immediately
- Selection: weighted random where lower streak = higher probability
  - Formula: `weight = 1 / (streak - threshold + 1)`
  - Words with streak 3 (just learned) are more likely than streak 20+
  - Ensures recently learned words (riskier) are reviewed more often

### Rule 7.2: Failed Review
If user gets a learned word wrong during review:
- Move it back to learning pool (pool: 49 → 50)
- Reset learned_date to null
- Reset correct_streak to 0
- Word needs to earn its way back to learned (3 consecutive correct)
- Since pool is now 50, NO new word is grabbed

### Rule 7.3: Successful Review
If user gets a learned word correct during review:
- Word stays in learned pool
- Increment correct_streak (+1)
- Update last_seen timestamp
- Learning pool still at 49, so grab 1 NEW word from to_learn next

---

## 8. Auto-Select Feature

### Rule 8.1: Left Card Auto-Selection
**Enabled by default** (toggle in Menu → "Auto-select left words")
- Automatically selects left (English) cards in cycle: 1→2→3→4→5→1→2→3...
- After correct match, next card is auto-selected (50ms delay)
- User can manually click any left card to override
- Cycle advances after each selection (auto or manual)

### Rule 8.2: Cycle Position Management
- Track current position in 1-5 cycle (0-4 index)
- Auto-select: advances to `(position + 1) % 5`
- Manual select: updates to `(selected_position + 1) % 5`
- Special case: if user selects 2 positions back, skip empty position

## Common Bugs to Avoid

### Bug A: Learning Pool Growing Forever
**WRONG:** Letting learning pool exceed 50 words
**RIGHT:** Cap at 50, only add new words when learning < 50

### Bug B: Same Words Repeatedly
**WRONG:** Showing same 5-10 words over and over
**RIGHT:** Actively add new words when pool < 50, use weighted random when pool = 50

### Bug C: Ambiguous Pairs
**WRONG:** Showing (this, die) and (which, die) together
**RIGHT:** Check both displayed words AND original entries

### Bug D: Fast Click Breaking
**WRONG:** Using global `isProcessing` flag
**RIGHT:** Check card classes and opacity

### Bug E: Position Memorization
**WRONG:** New cards always appear in same position
**RIGHT:** Randomize left-right placement independently

---

## Testing Checklist

Before declaring something "fixed":
- [ ] Learning pool builds up to 50 words
- [ ] No duplicate German or English words on screen
- [ ] Fast clicking works (no waiting for animations)
- [ ] Auto-select cycles through left cards (when enabled)
- [ ] New cards appear in random positions
- [ ] Stats save to server files
- [ ] Words move to "learned" after 3 consecutive correct
- [ ] Learned words appear for review after graduation
- [ ] Weighted random selection for learning pool (lower streak appears more)
- [ ] Frequency-based selection for new words (higher frequency first)

---

**If you're about to change the code, re-read this file first!**
