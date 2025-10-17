/**
 * Main Game Controller with Learning System Integration
 */

// Global instances
let userManager;
let learningSystem;

// Game state
let gameState = {
    selectedLeft: null,
    selectedRight: null,
    wordPool: [], // All available words
    currentWords: [], // Currently displayed 5 words
    pendingMatches: 0 // Count matches before refreshing with new words
};

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    // Initialize managers
    userManager = new UserManager();
    learningSystem = new LearningSystem(userManager);

    // ALWAYS show login screen - no auto-login
    setupLoginScreen();
});

/**
 * Setup login screen handlers
 */
function setupLoginScreen() {
    const loginBtn = document.getElementById('loginBtn');
    const usernameInput = document.getElementById('usernameInput');

    loginBtn.addEventListener('click', handleLogin);
    usernameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleLogin();
        }
    });

    // Auto-focus username input
    usernameInput.focus();
}

/**
 * Handle user login
 */
async function handleLogin() {
    const username = document.getElementById('usernameInput').value;

    try {
        const result = await userManager.login(username);

        if (result.success) {
            await startApp();
        } else {
            alert(result.error);
        }
    } catch (error) {
        alert('Error logging in: ' + error.message);
    }
}

/**
 * Start the main application after login
 */
async function startApp() {
    // Hide login screen, show app
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('appContainer').style.display = 'block';

    // Update user display
    const user = userManager.getCurrentUser();
    document.getElementById('usernameDisplay').textContent =
        user.displayName || user.username;

    // Setup menu handlers
    setupMenuHandlers();

    // Load words and start game
    await loadWords();
    updateStatsDisplay();
    initializeGame();
}

/**
 * Setup menu modal handlers
 */
function setupMenuHandlers() {
    const menuBtn = document.getElementById('menuBtn');
    const menuModal = document.getElementById('menuModal');
    const closeMenuBtn = document.getElementById('closeMenuBtn');
    const exportBtn = document.getElementById('exportDataBtn');
    const importBtn = document.getElementById('importDataBtn');
    const importFileInput = document.getElementById('importFileInput');
    const logoutBtn = document.getElementById('logoutBtn');

    // Open menu
    menuBtn.addEventListener('click', () => {
        menuModal.classList.add('show');
    });

    // Close menu
    closeMenuBtn.addEventListener('click', () => {
        menuModal.classList.remove('show');
    });

    // Export data
    exportBtn.addEventListener('click', () => {
        userManager.exportUserData();
        menuModal.classList.remove('show');
    });

    // Import data
    importBtn.addEventListener('click', () => {
        importFileInput.click();
    });

    importFileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (file) {
            try {
                await userManager.importUserData(file);
                alert('Data imported successfully! Reloading...');
                location.reload();
            } catch (error) {
                alert('Error importing data: ' + error);
            }
        }
    });

    // Logout
    logoutBtn.addEventListener('click', () => {
        userManager.logout();
        location.reload();
    });

    // View stats
    const viewStatsBtn = document.getElementById('viewStatsBtn');
    viewStatsBtn.addEventListener('click', () => {
        showDetailedStats();
    });
}

/**
 * Show detailed statistics
 */
function showDetailedStats() {
    const stats = learningSystem.getStatsSummary();
    const pools = stats.pools;
    const user = userManager.getCurrentUser();
    const displayName = user.displayName || user.username;

    alert(`📊 Your Statistics\n\n` +
          `User: ${displayName}\n` +
          `Level: ${stats.level}\n` +
          `Total Words Tracked: ${stats.totalWords}\n\n` +
          `📚 Pool Status:\n` +
          `• To Learn: ${pools.to_learn}\n` +
          `• Learning: ${pools.learning}\n` +
          `• Learned: ${pools.learned}\n\n` +
          `📅 Today:\n` +
          `• Words Learned: ${stats.today.learned} / ${stats.today.goal}\n` +
          `• Attempts: ${stats.today.attempts}\n` +
          `• Accuracy: ${stats.accuracy}%`
    );

    document.getElementById('menuModal').classList.remove('show');
}

/**
 * Load word data from JSON
 */
async function loadWords() {
    try {
        const level = userManager.getCurrentUser().current_level;
        const response = await fetch(`processed_data/by_level_expanded/german_words_${level}.json`);
        const data = await response.json();

        gameState.wordPool = data.words;
        console.log(`Loaded ${gameState.wordPool.length} words for level ${level}`);
    } catch (error) {
        console.error('Error loading words:', error);
        alert('Error loading word data. Please check the console.');
    }
}

/**
 * Initialize game with smart word selection
 */
function initializeGame() {
    // Check if daily goal is reached
    if (learningSystem.isDailyGoalReached()) {
        showDailyGoalComplete();
        return;
    }

    // Reset pending matches
    gameState.pendingMatches = 0;

    // Select 5 words using smart selection
    gameState.currentWords = selectSmartWords(5);
    console.log('Initial game words:', gameState.currentWords.length, 'words selected');
    console.log('Words:', gameState.currentWords.map(w => `${w.word} - ${w.translation}`));
    renderWords();

    // Ensure we have exactly 5 pairs
    setTimeout(() => ensureFivePairs(), 200);
}

/**
 * Parse original_id to get all German and English words from the original entry
 */
function parseOriginalId(originalId) {
    const [germanPart, englishPart] = originalId.split('|');
    const germanWords = germanPart.split(',').map(w => w.trim().toLowerCase());
    const englishWords = englishPart.split(',').map(w => w.trim().toLowerCase());
    return { germanWords, englishWords };
}

/**
 * Check if a word would create ambiguity with already-selected words
 */
function wouldCreateAmbiguity(word, usedOriginalWords) {
    const { germanWords, englishWords } = parseOriginalId(word.original_id);

    // Check if any German word from this original entry conflicts
    for (const germanWord of germanWords) {
        if (usedOriginalWords.germanWords.has(germanWord)) {
            return true;
        }
    }

    // Check if any English word from this original entry conflicts
    for (const englishWord of englishWords) {
        if (usedOriginalWords.englishWords.has(englishWord)) {
            return true;
        }
    }

    return false;
}

/**
 * Select words using learning system's smart algorithm
 */
function selectSmartWords(count) {
    const selected = [];
    // Track all words from ALL original entries we've selected from
    const usedOriginalWords = {
        germanWords: new Set(),
        englishWords: new Set()
    };
    const usedOriginalIds = new Set();

    // ALSO track the actual displayed words to prevent duplicates
    const usedDisplayWords = {
        germanWords: new Set(),
        englishWords: new Set()
    };

    let attempts = 0;
    const maxAttempts = 100; // Prevent infinite loops

    // Keep trying until we get 'count' unique words or run out of options
    while (selected.length < count && attempts < maxAttempts) {
        attempts++;

        // Filter out words that would create ambiguity
        const availableWords = gameState.wordPool.filter(word => {
            // Skip if we already used this exact original_id
            if (usedOriginalIds.has(word.original_id)) {
                return false;
            }

            // Skip if the actual displayed words would duplicate
            if (usedDisplayWords.germanWords.has(word.word.toLowerCase()) ||
                usedDisplayWords.englishWords.has(word.translation.toLowerCase())) {
                return false;
            }

            // Check if this would create ambiguity with already-selected originals
            return !wouldCreateAmbiguity(word, usedOriginalWords);
        });

        if (availableWords.length === 0) {
            console.log('No more available words to select without ambiguity');
            break;
        }

        // Get next word from learning system
        const word = learningSystem.selectNextWord(availableWords);

        if (!word) {
            console.log('selectNextWord returned null');
            break;
        }

        // Add to selected
        selected.push(word);
        usedOriginalIds.add(word.original_id);

        // Add the actual displayed words
        usedDisplayWords.germanWords.add(word.word.toLowerCase());
        usedDisplayWords.englishWords.add(word.translation.toLowerCase());

        // Add ALL words from this original entry to used sets
        const { germanWords, englishWords } = parseOriginalId(word.original_id);
        germanWords.forEach(w => usedOriginalWords.germanWords.add(w));
        englishWords.forEach(w => usedOriginalWords.englishWords.add(w));

        console.log(`  Added: ${word.word} - ${word.translation}`);
        console.log(`    Original: ${word.original_id}`);
        console.log(`    All German from original: ${germanWords.join(', ')}`);
        console.log(`    All English from original: ${englishWords.join(', ')}`);
    }

    console.log(`Selected ${selected.length} words out of ${count} requested`);
    return selected;
}

/**
 * Render words in grid
 */
function renderWords() {
    const leftColumn = document.getElementById('leftColumn');
    const rightColumn = document.getElementById('rightColumn');

    // Clear existing cards
    leftColumn.innerHTML = '';
    rightColumn.innerHTML = '';

    // Shuffle left (English) and right (German) separately
    const shuffledLeft = shuffleArray(gameState.currentWords);
    const shuffledRight = shuffleArray(gameState.currentWords);

    // Create left column cards (English)
    shuffledLeft.forEach((word) => {
        const card = createWordCard(word.translation, 'left', word);
        leftColumn.appendChild(card);
    });

    // Create right column cards (German)
    shuffledRight.forEach((word) => {
        const card = createWordCard(word.word, 'right', word);
        rightColumn.appendChild(card);
    });
}

/**
 * Create word card element
 */
function createWordCard(text, side, wordData) {
    const card = document.createElement('div');
    card.className = 'word-card';
    card.textContent = text;
    card.dataset.side = side;
    card.dataset.wordId = `${wordData.word}|${wordData.translation}`;

    // Add gender-based color for German nouns (right side only)
    if (side === 'right' && wordData.word_type === 'Noun') {
        const germanWord = wordData.word.toLowerCase();
        if (germanWord.startsWith('der ')) {
            card.classList.add('gender-der');
        } else if (germanWord.startsWith('die ')) {
            card.classList.add('gender-die');
        } else if (germanWord.startsWith('das ')) {
            card.classList.add('gender-das');
        }
    }

    card.addEventListener('click', () => handleCardClick(card, side, wordData));

    return card;
}

/**
 * Handle card click
 */
function handleCardClick(card, side, wordData) {
    // Don't allow clicking cards that are being processed/removed
    if (card.classList.contains('correct') ||
        card.classList.contains('removing') ||
        card.classList.contains('incorrect') ||
        card.style.opacity === '0' ||
        card.style.pointerEvents === 'none') {
        return;
    }

    // Deselect if clicking the same card again
    if (side === 'left' && gameState.selectedLeft === card) {
        card.classList.remove('selected');
        gameState.selectedLeft = null;
        return;
    }

    if (side === 'right' && gameState.selectedRight === card) {
        card.classList.remove('selected');
        gameState.selectedRight = null;
        return;
    }

    // Select card
    if (side === 'left') {
        // Deselect previous left card if any
        if (gameState.selectedLeft) {
            gameState.selectedLeft.classList.remove('selected');
        }
        gameState.selectedLeft = card;
        card.classList.add('selected');
    } else {
        // Deselect previous right card if any
        if (gameState.selectedRight) {
            gameState.selectedRight.classList.remove('selected');
        }
        gameState.selectedRight = card;
        card.classList.add('selected');
    }

    // Check if both sides are selected
    if (gameState.selectedLeft && gameState.selectedRight) {
        checkMatch();
    }
}

/**
 * Check if selected pair matches
 */
function checkMatch() {
    // Store references to the cards being processed
    const leftCard = gameState.selectedLeft;
    const rightCard = gameState.selectedRight;
    const leftId = leftCard.dataset.wordId;
    const rightId = rightCard.dataset.wordId;

    // Find the word data
    const wordData = gameState.currentWords.find(
        w => `${w.word}|${w.translation}` === leftId
    );

    // Clear selections immediately so user can select next pair
    gameState.selectedLeft = null;
    gameState.selectedRight = null;

    const isCorrect = leftId === rightId;

    // Record answer in learning system
    const result = learningSystem.recordAnswer(wordData, isCorrect);

    if (isCorrect) {
        // Correct match
        leftCard.classList.add('correct');
        rightCard.classList.add('correct');

        // Show notification if word was learned
        if (result.statusChange === 'learned') {
            showNotification('🎉 Word learned!');
        }

        setTimeout(() => {
            // Remove matched cards
            leftCard.classList.add('removing');
            rightCard.classList.add('removing');

            setTimeout(() => {
                // Remove the matched word from currentWords
                gameState.currentWords = gameState.currentWords.filter(
                    w => `${w.word}|${w.translation}` !== leftId
                );

                // Make matched cards invisible
                leftCard.style.opacity = '0';
                leftCard.style.pointerEvents = 'none';
                rightCard.style.opacity = '0';
                rightCard.style.pointerEvents = 'none';

                // Update stats display
                updateStatsDisplay();

                // Check if daily goal is reached
                if (learningSystem.isDailyGoalReached()) {
                    // Show completion after all cards are cleared
                    if (gameState.currentWords.length === 0) {
                        setTimeout(() => {
                            showDailyGoalComplete();
                        }, 500);
                    }
                } else {
                    // Check if word moved to learned (new flow: review then refill)
                    if (result.statusChange === 'learned') {
                        console.log('Word graduated to learned! Checking for learned words to review...');
                        // On graduation, we need to:
                        // 1. Show learned word for review (if any exist)
                        // 2. Add new word from to_learn
                        // 3. If this was the 2nd match, we have 2 empty spots
                        // 4. If this was the 1st match, we have 1 empty spot
                        const actualEmptySpots = gameState.pendingMatches + 1;

                        // If only 1 spot is empty, DON'T reset counter - let next match trigger 2-fill
                        if (actualEmptySpots === 1) {
                            // Fill the 1 empty spot, keep pendingMatches at 0 so next match will be #1
                            handleGraduationFlow(1);
                            gameState.pendingMatches = 0;
                        } else {
                            // Fill the 2 empty spots, reset counter
                            handleGraduationFlow(2);
                            gameState.pendingMatches = 0;
                        }
                    } else {
                        // Normal flow: increment pending matches
                        gameState.pendingMatches++;

                        // After 2 matches, add new words and refresh display
                        if (gameState.pendingMatches >= 2) {
                            gameState.pendingMatches = 0;
                            addNewWordsAndRefresh();
                        }
                    }
                }
            }, 300);
        }, 500);
    } else {
        // Incorrect match
        leftCard.classList.add('incorrect');
        rightCard.classList.add('incorrect');

        // Show notification if learned word was unlearned
        if (result.statusChange === 'unlearned') {
            showNotification('⚠️ Word moved back to learning');
        }

        setTimeout(() => {
            leftCard.classList.remove('selected', 'incorrect');
            rightCard.classList.remove('selected', 'incorrect');

            // Update stats display
            updateStatsDisplay();
        }, 500);
    }
}

/**
 * Handle graduation flow: review learned word (if any), then grab new word
 * This is called INSTEAD of normal 2-match refill, so we need to fill ALL empty spots
 */
function handleGraduationFlow(totalEmptySpots) {
    console.log(`=== Graduation Flow Started (${totalEmptySpots} empty spots) ===`);

    // Build tracking for current words
    const currentUsedOriginalWords = {
        germanWords: new Set(),
        englishWords: new Set()
    };
    const currentUsedOriginalIds = new Set();
    const currentDisplayWords = {
        germanWords: new Set(),
        englishWords: new Set()
    };

    gameState.currentWords.forEach(w => {
        currentUsedOriginalIds.add(w.original_id);
        currentDisplayWords.germanWords.add(w.word.toLowerCase());
        currentDisplayWords.englishWords.add(w.translation.toLowerCase());

        const { germanWords, englishWords } = parseOriginalId(w.original_id);
        germanWords.forEach(gw => currentUsedOriginalWords.germanWords.add(gw));
        englishWords.forEach(ew => currentUsedOriginalWords.englishWords.add(ew));
    });

    const wordsToShow = [];

    // Step 1: Try to get a learned word for review
    let availablePool = gameState.wordPool.filter(word => {
        if (currentUsedOriginalIds.has(word.original_id)) return false;
        if (currentDisplayWords.germanWords.has(word.word.toLowerCase())) return false;
        if (currentDisplayWords.englishWords.has(word.translation.toLowerCase())) return false;
        return !wouldCreateAmbiguity(word, currentUsedOriginalWords);
    });

    const learnedWord = learningSystem.selectLearnedWordForReview(availablePool);

    if (learnedWord) {
        console.log(`Adding learned word for review: ${learnedWord.word} - ${learnedWord.translation}`);
        gameState.currentWords.push(learnedWord);
        wordsToShow.push(learnedWord);

        // Update tracking
        currentUsedOriginalIds.add(learnedWord.original_id);
        currentDisplayWords.germanWords.add(learnedWord.word.toLowerCase());
        currentDisplayWords.englishWords.add(learnedWord.translation.toLowerCase());
        const { germanWords, englishWords } = parseOriginalId(learnedWord.original_id);
        germanWords.forEach(gw => currentUsedOriginalWords.germanWords.add(gw));
        englishWords.forEach(ew => currentUsedOriginalWords.englishWords.add(ew));
    }

    // Step 2: ALWAYS add new word(s) from to_learn to fill remaining empty spots
    const spotsToFill = totalEmptySpots - wordsToShow.length;
    console.log(`Need to fill ${spotsToFill} more spots (total: ${totalEmptySpots}, already have: ${wordsToShow.length})`);

    for (let i = 0; i < spotsToFill; i++) {
        // Rebuild available pool for each word
        availablePool = gameState.wordPool.filter(word => {
            if (currentUsedOriginalIds.has(word.original_id)) return false;
            if (currentDisplayWords.germanWords.has(word.word.toLowerCase())) return false;
            if (currentDisplayWords.englishWords.has(word.translation.toLowerCase())) return false;
            return !wouldCreateAmbiguity(word, currentUsedOriginalWords);
        });

        console.log(`  Spot ${i+1}: Available pool has ${availablePool.length} words`);

        if (availablePool.length === 0) {
            console.error(`❌ No more available words for spot ${i+1}!`);
            console.log(`  Current words on screen: ${gameState.currentWords.length}`);
            console.log(`  Total word pool: ${gameState.wordPool.length}`);
            break;
        }

        const newWord = learningSystem.selectNextWord(availablePool);

        if (!newWord) {
            console.error(`❌ selectNextWord returned null for spot ${i+1}!`);
            break;
        }

        console.log(`  ✓ Adding new word ${i+1}: ${newWord.word} - ${newWord.translation}`);
        gameState.currentWords.push(newWord);
        wordsToShow.push(newWord);

        // Update tracking
        currentUsedOriginalIds.add(newWord.original_id);
        currentDisplayWords.germanWords.add(newWord.word.toLowerCase());
        currentDisplayWords.englishWords.add(newWord.translation.toLowerCase());
        const { germanWords, englishWords } = parseOriginalId(newWord.original_id);
        germanWords.forEach(gw => currentUsedOriginalWords.germanWords.add(gw));
        englishWords.forEach(ew => currentUsedOriginalWords.englishWords.add(ew));
    }

    console.log(`Graduation flow: showing ${wordsToShow.length} words total`);

    // Fill empty spots with the selected words
    if (wordsToShow.length > 0) {
        fillEmptySpots(wordsToShow);
    }

    console.log('=== Graduation Flow Complete ===');

    // Ensure we always have 5 pairs
    setTimeout(() => ensureFivePairs(), 200);
}

/**
 * Ensure we always have exactly 5 pairs on screen
 * Call this after any card operation to maintain consistency
 */
function ensureFivePairs() {
    const currentPairs = gameState.currentWords.length;
    console.log(`🔍 ensureFivePairs check: Currently have ${currentPairs} pairs`);

    if (currentPairs >= 5) {
        console.log(`✓ Have ${currentPairs} pairs, no action needed`);
        return; // Already have 5 or more
    }

    const needMore = 5 - currentPairs;
    console.log(`⚠️ Only ${currentPairs} pairs! Need to add ${needMore} more...`);

    // Build tracking for current words
    const currentUsedOriginalWords = {
        germanWords: new Set(),
        englishWords: new Set()
    };
    const currentUsedOriginalIds = new Set();
    const currentDisplayWords = {
        germanWords: new Set(),
        englishWords: new Set()
    };

    gameState.currentWords.forEach(w => {
        currentUsedOriginalIds.add(w.original_id);
        currentDisplayWords.germanWords.add(w.word.toLowerCase());
        currentDisplayWords.englishWords.add(w.translation.toLowerCase());

        const { germanWords, englishWords } = parseOriginalId(w.original_id);
        germanWords.forEach(gw => currentUsedOriginalWords.germanWords.add(gw));
        englishWords.forEach(ew => currentUsedOriginalWords.englishWords.add(ew));
    });

    const wordsToAdd = [];

    for (let i = 0; i < needMore; i++) {
        // Filter available words
        const availablePool = gameState.wordPool.filter(word => {
            if (currentUsedOriginalIds.has(word.original_id)) return false;
            if (currentDisplayWords.germanWords.has(word.word.toLowerCase())) return false;
            if (currentDisplayWords.englishWords.has(word.translation.toLowerCase())) return false;
            return !wouldCreateAmbiguity(word, currentUsedOriginalWords);
        });

        if (availablePool.length === 0) {
            console.error(`❌ Cannot add word ${i+1}: no available words!`);
            break;
        }

        const newWord = learningSystem.selectNextWord(availablePool);

        if (newWord) {
            console.log(`  ✓ Adding word ${i+1}: ${newWord.word} - ${newWord.translation}`);
            gameState.currentWords.push(newWord);
            wordsToAdd.push(newWord);

            // Update tracking
            currentUsedOriginalIds.add(newWord.original_id);
            currentDisplayWords.germanWords.add(newWord.word.toLowerCase());
            currentDisplayWords.englishWords.add(newWord.translation.toLowerCase());
            const { germanWords, englishWords } = parseOriginalId(newWord.original_id);
            germanWords.forEach(gw => currentUsedOriginalWords.germanWords.add(gw));
            englishWords.forEach(ew => currentUsedOriginalWords.englishWords.add(ew));
        }
    }

    if (wordsToAdd.length > 0) {
        console.log(`Adding ${wordsToAdd.length} words to reach 5 pairs`);
        fillEmptySpots(wordsToAdd);
    }

    console.log(`✓ ensureFivePairs complete: Now have ${gameState.currentWords.length} pairs`);
}

/**
 * Add new words and refresh the display (after 2 matches)
 */
function addNewWordsAndRefresh() {
    // Build used original words from current words
    const currentUsedOriginalWords = {
        germanWords: new Set(),
        englishWords: new Set()
    };
    const currentUsedOriginalIds = new Set();

    // Track actual displayed words
    const currentDisplayWords = {
        germanWords: new Set(),
        englishWords: new Set()
    };

    gameState.currentWords.forEach(w => {
        currentUsedOriginalIds.add(w.original_id);
        currentDisplayWords.germanWords.add(w.word.toLowerCase());
        currentDisplayWords.englishWords.add(w.translation.toLowerCase());

        const { germanWords, englishWords } = parseOriginalId(w.original_id);
        germanWords.forEach(gw => currentUsedOriginalWords.germanWords.add(gw));
        englishWords.forEach(ew => currentUsedOriginalWords.englishWords.add(ew));
    });

    // Check if we should add new words (respect learning pool cap)
    const poolSizes = learningSystem.getPoolSizes();
    const shouldAddNewWords = poolSizes.learning < learningSystem.LEARNING_POOL_SIZE;

    let wordsToShow = [];

    if (shouldAddNewWords) {
        // Learning pool < cap: Add new words from to_learn
        const maxToAdd = Math.min(2, learningSystem.LEARNING_POOL_SIZE - poolSizes.learning);
        console.log(`Can add up to ${maxToAdd} new words (pool: ${poolSizes.learning}/${learningSystem.LEARNING_POOL_SIZE})`);

        for (let i = 0; i < maxToAdd; i++) {
        // Rebuild available pool with updated tracking for each word
        const availablePool = gameState.wordPool.filter(word => {
            if (currentUsedOriginalIds.has(word.original_id)) {
                return false;
            }

            // Check for displayed word duplicates
            if (currentDisplayWords.germanWords.has(word.word.toLowerCase()) ||
                currentDisplayWords.englishWords.has(word.translation.toLowerCase())) {
                return false;
            }

            return !wouldCreateAmbiguity(word, currentUsedOriginalWords);
        });

        if (availablePool.length === 0) {
            console.log(`No more available words for iteration ${i+1}`);
            break;
        }

            const newWord = learningSystem.selectNextWord(availablePool);

            if (newWord) {
                gameState.currentWords.push(newWord);
                wordsToShow.push(newWord);

                // Update tracking for next iteration
                currentUsedOriginalIds.add(newWord.original_id);
                currentDisplayWords.germanWords.add(newWord.word.toLowerCase());
                currentDisplayWords.englishWords.add(newWord.translation.toLowerCase());

                const { germanWords, englishWords } = parseOriginalId(newWord.original_id);
                germanWords.forEach(gw => currentUsedOriginalWords.germanWords.add(gw));
                englishWords.forEach(ew => currentUsedOriginalWords.englishWords.add(ew));

                console.log(`Added new word ${i+1}: ${newWord.word} - ${newWord.translation}`);
            }
        }
    } else {
        // Learning pool at cap: Re-show words from learning pool (not new words)
        console.log(`Learning pool at ${poolSizes.learning}, re-showing from learning pool`);

        for (let i = 0; i < 2; i++) {
            // Filter to get learning pool words not currently displayed
            const availablePool = gameState.wordPool.filter(word => {
                const stats = learningSystem.initializeWordStats(word);
                if (stats.status !== 'learning') return false;

                if (currentUsedOriginalIds.has(word.original_id)) {
                    return false;
                }

                // Check for displayed word duplicates
                if (currentDisplayWords.germanWords.has(word.word.toLowerCase()) ||
                    currentDisplayWords.englishWords.has(word.translation.toLowerCase())) {
                    return false;
                }

                return !wouldCreateAmbiguity(word, currentUsedOriginalWords);
            });

            if (availablePool.length === 0) {
                console.log(`No more learning words available for iteration ${i+1}`);
                break;
            }

            const word = learningSystem.selectNextWord(availablePool);

            if (word) {
                gameState.currentWords.push(word);
                wordsToShow.push(word);

                // Update tracking
                currentUsedOriginalIds.add(word.original_id);
                currentDisplayWords.germanWords.add(word.word.toLowerCase());
                currentDisplayWords.englishWords.add(word.translation.toLowerCase());

                const { germanWords, englishWords } = parseOriginalId(word.original_id);
                germanWords.forEach(gw => currentUsedOriginalWords.germanWords.add(gw));
                englishWords.forEach(ew => currentUsedOriginalWords.englishWords.add(ew));

                console.log(`Re-showing learning word ${i+1}: ${word.word} - ${word.translation}`);
            }
        }
    }

    console.log(`Showing ${wordsToShow.length} words. Current total: ${gameState.currentWords.length}`);

    // Find empty spots and fill them with selected cards
    if (wordsToShow.length > 0) {
        fillEmptySpots(wordsToShow);
    }

    // Ensure we always have 5 pairs
    setTimeout(() => ensureFivePairs(), 200);
}

/**
 * Fill empty spots with new word cards
 */
function fillEmptySpots(newWords) {
    const leftColumn = document.getElementById('leftColumn');
    const rightColumn = document.getElementById('rightColumn');

    // Find empty spots (cards with opacity 0)
    const leftCards = Array.from(leftColumn.children);
    const rightCards = Array.from(rightColumn.children);

    const emptyLeftSpots = leftCards.filter(card => card.style.opacity === '0');
    const emptyRightSpots = rightCards.filter(card => card.style.opacity === '0');

    console.log(`📍 fillEmptySpots called with ${newWords.length} new words`);
    console.log(`  Found ${emptyLeftSpots.length} empty left spots and ${emptyRightSpots.length} empty right spots`);

    if (newWords.length > emptyLeftSpots.length || newWords.length > emptyRightSpots.length) {
        console.warn(`⚠️ Mismatch: ${newWords.length} words to show but only ${Math.min(emptyLeftSpots.length, emptyRightSpots.length)} empty spots!`);
    }

    // Shuffle the new words for random placement in left column
    const shuffledLeftWords = shuffleArray(newWords);
    // Shuffle independently for right column
    const shuffledRightWords = shuffleArray([...newWords]);

    // Fill empty spots with new words
    let filled = 0;
    newWords.forEach((word, index) => {
        if (index < emptyLeftSpots.length && index < emptyRightSpots.length) {
            const emptyLeftCard = emptyLeftSpots[index];
            const emptyRightCard = emptyRightSpots[index];

            // Use shuffled order for each column
            const leftWord = shuffledLeftWords[index];
            const rightWord = shuffledRightWords[index];

            // Replace the empty cards
            emptyLeftCard.parentNode.replaceChild(
                createWordCard(leftWord.translation, 'left', leftWord),
                emptyLeftCard
            );
            emptyRightCard.parentNode.replaceChild(
                createWordCard(rightWord.word, 'right', rightWord),
                emptyRightCard
            );

            filled++;
            console.log(`  ✓ Filled spot ${filled} - Left: ${leftWord.translation}, Right: ${rightWord.word}`);
        } else {
            console.error(`  ❌ Cannot fill word ${index+1}: not enough empty spots!`);
        }
    });

    console.log(`📍 fillEmptySpots complete: filled ${filled} out of ${newWords.length} words`);
}

/**
 * Update all stats in the UI
 */
function updateStatsDisplay() {
    const stats = learningSystem.getStatsSummary();
    const pools = stats.pools;
    const today = stats.today;

    // Update stats panel
    document.getElementById('todayGoal').textContent =
        `${today.learned} / ${today.goal}`;
    document.getElementById('learningCount').textContent = pools.learning;
    document.getElementById('learnedCount').textContent = pools.learned;
    document.getElementById('accuracyPercent').textContent = `${stats.accuracy}%`;

    // Update progress bar
    const progressPercent = (today.learned / today.goal) * 100;
    document.getElementById('progressBar').style.width = `${progressPercent}%`;
}

/**
 * Show notification message
 */
function showNotification(message) {
    // Simple alert for now - could be enhanced with custom notification UI
    console.log(message);
}

/**
 * Show daily goal completion screen
 */
function showDailyGoalComplete() {
    const stats = learningSystem.getStatsSummary();
    const completionScreen = document.getElementById('completionScreen');
    const completionMessage = document.getElementById('completionMessage');
    const completionStats = document.getElementById('completionStats');

    completionMessage.textContent =
        `Congratulations! You've learned ${stats.today.learned} words today!`;

    completionStats.innerHTML = `
        <p><strong>Total Attempts:</strong> ${stats.today.attempts}</p>
        <p><strong>Correct:</strong> ${stats.today.correct}</p>
        <p><strong>Incorrect:</strong> ${stats.today.incorrect}</p>
        <p><strong>Accuracy:</strong> ${stats.accuracy}%</p>
        <p><strong>Words Learning:</strong> ${stats.pools.learning}</p>
        <p><strong>Words Learned:</strong> ${stats.pools.learned}</p>
    `;

    completionScreen.classList.add('show');
}

/**
 * Shuffle array utility
 */
function shuffleArray(array) {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
}
