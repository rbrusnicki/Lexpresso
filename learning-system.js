/**
 * Spaced Repetition Learning System
 * Implements three-pool system: To Learn -> Learning -> Learned
 */

class LearningSystem {
    constructor(userManager) {
        this.userManager = userManager;
        this.LEARNING_POOL_SIZE = 50; // Target size of learning pool
        this.LEARNED_THRESHOLD = 3; // Consecutive correct answers
        this.DAILY_GOAL = 50; // Words to learn per day
    }

    /**
     * Get word ID from word data
     */
    getWordId(wordData) {
        return `${wordData.word}|${wordData.translation}`;
    }

    /**
     * Initialize word stats if not exists
     */
    initializeWordStats(wordData) {
        const user = this.userManager.getCurrentUser();
        const wordId = this.getWordId(wordData);

        if (!user.words[wordId]) {
            user.words[wordId] = {
                status: 'to_learn',
                correct_streak: 0,
                total_correct: 0,
                total_incorrect: 0,
                last_seen: null,
                learned_date: null,
                frequency: wordData.frequency || 1,
                level: wordData.level || 'A1',
                word_type: wordData.word_type || 'Unknown'
            };
        }

        return user.words[wordId];
    }

    /**
     * Get words by status
     */
    getWordsByStatus(status) {
        const user = this.userManager.getCurrentUser();
        return Object.entries(user.words)
            .filter(([id, stats]) => stats.status === status)
            .map(([id, stats]) => ({ id, ...stats }));
    }

    /**
     * Record answer for a word
     */
    recordAnswer(wordData, correct) {
        const user = this.userManager.getCurrentUser();
        const wordId = this.getWordId(wordData);
        const stats = this.initializeWordStats(wordData);

        // Update stats
        stats.last_seen = new Date().toISOString();

        if (correct) {
            stats.total_correct++;
            stats.correct_streak++;

            // Check if word should move to learning pool
            if (stats.status === 'to_learn' && stats.correct_streak >= 1) {
                stats.status = 'learning';
            }

            // Check if word should move to learned pool
            if (stats.status === 'learning' && stats.correct_streak >= this.LEARNED_THRESHOLD) {
                stats.status = 'learned';
                stats.learned_date = new Date().toISOString();

                // Update daily stats
                this.userManager.updateTodayStats(true, 1);
                this.userManager.saveCurrentUser();

                return { statusChange: 'learned' };
            }
        } else {
            stats.total_incorrect++;
            stats.correct_streak = 0;

            // If learned word is wrong, move back to learning
            if (stats.status === 'learned') {
                stats.status = 'learning';
                stats.learned_date = null;

                this.userManager.updateTodayStats(false);
                this.userManager.saveCurrentUser();

                return { statusChange: 'unlearned' };
            }
        }

        this.userManager.updateTodayStats(correct);
        this.userManager.saveCurrentUser();

        return { statusChange: null };
    }

    /**
     * Get pool sizes
     */
    getPoolSizes() {
        return {
            to_learn: this.getWordsByStatus('to_learn').length,
            learning: this.getWordsByStatus('learning').length,
            learned: this.getWordsByStatus('learned').length
        };
    }

    /**
     * Get today's progress
     */
    getTodayProgress() {
        const todayStats = this.userManager.getTodayStats();
        return {
            learned: todayStats.words_learned,
            goal: this.DAILY_GOAL,
            attempts: todayStats.total_attempts,
            correct: todayStats.correct,
            incorrect: todayStats.incorrect
        };
    }

    /**
     * Check if daily goal is reached
     */
    isDailyGoalReached() {
        const progress = this.getTodayProgress();
        return progress.learned >= this.DAILY_GOAL;
    }

    /**
     * Select next word pair to practice
     * SIMPLIFIED algorithm:
     * - Pool < 10: ALWAYS pick from to_learn (100%)
     * - Pool = 10: ALWAYS pick from learning (100%)
     * - Learned words only reviewed after graduation (not randomly)
     */
    selectNextWord(availableWords) {
        const user = this.userManager.getCurrentUser();
        const pools = this.getPoolSizes();

        // Initialize stats for all available words
        availableWords.forEach(word => this.initializeWordStats(word));

        // Separate into pools
        const toLearnWords = availableWords.filter(word => {
            const stats = user.words[this.getWordId(word)];
            return stats.status === 'to_learn';
        });

        const learningWords = availableWords.filter(word => {
            const stats = user.words[this.getWordId(word)];
            return stats.status === 'learning';
        });

        // Simple rule: pool < cap = pick new, pool = cap = pick learning
        let candidatePool;
        let isLearningPool = false;

        if (pools.learning < this.LEARNING_POOL_SIZE && toLearnWords.length > 0) {
            // Pool < cap: Pick from to_learn (prioritize by frequency)
            candidatePool = toLearnWords;
            isLearningPool = false;
        } else if (pools.learning >= this.LEARNING_POOL_SIZE && learningWords.length > 0) {
            // Pool = cap: Pick from learning (use weighted random)
            candidatePool = learningWords;
            isLearningPool = true;
        } else {
            // Fallback
            candidatePool = toLearnWords.length > 0 ? toLearnWords : learningWords;
            isLearningPool = learningWords.length > 0 && toLearnWords.length === 0;
        }

        if (candidatePool.length === 0) {
            // Fallback: return any available word
            return availableWords[Math.floor(Math.random() * availableWords.length)];
        }

        if (isLearningPool) {
            // Weighted random selection for learning pool
            // Lower streak = higher weight = higher probability
            // Formula: weight = 1 / (streak + 1)
            const weights = candidatePool.map(word => {
                const stats = user.words[this.getWordId(word)];
                return 1 / (stats.correct_streak + 1);
            });

            // Calculate total weight
            const totalWeight = weights.reduce((sum, w) => sum + w, 0);

            // Generate random number and select word
            const random = Math.random() * totalWeight;
            let cumulativeWeight = 0;

            for (let i = 0; i < candidatePool.length; i++) {
                cumulativeWeight += weights[i];
                if (random <= cumulativeWeight) {
                    return candidatePool[i];
                }
            }

            // Fallback
            return candidatePool[0];
        } else {
            // Deterministic selection for to_learn pool
            // Sort by: 1) Frequency (higher first), 2) Never seen, 3) Least recently seen
            candidatePool.sort((a, b) => {
                const statsA = user.words[this.getWordId(a)];
                const statsB = user.words[this.getWordId(b)];

                // Prioritize by frequency (higher frequency = more common = learn first)
                if (a.frequency !== b.frequency) {
                    return b.frequency - a.frequency; // Descending
                }

                // Then prioritize never seen
                if (!statsA.last_seen && statsB.last_seen) return -1;
                if (statsA.last_seen && !statsB.last_seen) return 1;

                // Then by last seen (ascending - oldest first)
                return (statsA.last_seen || '') < (statsB.last_seen || '') ? -1 : 1;
            });

            return candidatePool[0];
        }
    }

    /**
     * Select a learned word for review (called after graduation)
     * Reviews from ALL learned words in user's history, not just current pool
     * Prioritize: 1) Lower streak, 2) Oldest last_seen
     * Applies anti-ambiguity checks
     */
    selectLearnedWordForReview(currentlyDisplayedWordIds, currentDisplayWords, currentUsedOriginalWords) {
        const user = this.userManager.getCurrentUser();

        // Get ALL learned words from user's entire history
        const allLearnedWords = [];
        for (const [wordId, stats] of Object.entries(user.words)) {
            if (stats.status === 'learned') {
                // Skip if already displayed on screen (exact word ID)
                if (currentlyDisplayedWordIds.has(wordId)) {
                    continue;
                }

                // Reconstruct word object from wordId (format: "german|english")
                const [germanWord, englishWord] = wordId.split('|');

                // Anti-ambiguity check: skip if German or English word would duplicate
                if (currentDisplayWords.germanWords.has(germanWord.toLowerCase()) ||
                    currentDisplayWords.englishWords.has(englishWord.toLowerCase())) {
                    continue;
                }

                const wordObj = {
                    word: germanWord,
                    translation: englishWord,
                    frequency: stats.frequency || 1,
                    level: stats.level || 'A1',
                    word_type: stats.word_type || 'Unknown',
                    original_id: wordId // Use wordId as original_id for learned words
                };

                // Check if this word would create ambiguity with original entries
                // For learned words, we use the wordId as original_id
                const wouldConflict = this.checkOriginalIdConflict(
                    wordId,
                    currentUsedOriginalWords
                );

                if (!wouldConflict) {
                    allLearnedWords.push({ word: wordObj, stats: stats });
                }
            }
        }

        if (allLearnedWords.length === 0) {
            return null;
        }

        // Weighted random selection based on streak
        // Lower streak = higher weight = higher probability
        // Formula: weight = 1 / (streak - LEARNED_THRESHOLD + 1)
        // This creates exponential decay favoring lower streaks
        const weights = allLearnedWords.map(item => {
            const streakAboveThreshold = item.stats.correct_streak - this.LEARNED_THRESHOLD;
            return 1 / (streakAboveThreshold + 1);
        });

        // Calculate total weight
        const totalWeight = weights.reduce((sum, w) => sum + w, 0);

        // Generate random number and select word
        const random = Math.random() * totalWeight;
        let cumulativeWeight = 0;

        for (let i = 0; i < allLearnedWords.length; i++) {
            cumulativeWeight += weights[i];
            if (random <= cumulativeWeight) {
                return allLearnedWords[i].word;
            }
        }

        // Fallback (should never reach here)
        return allLearnedWords[0].word;
    }

    /**
     * Check if an original_id would create ambiguity with already-selected words
     */
    checkOriginalIdConflict(originalId, usedOriginalWords) {
        const [germanPart, englishPart] = originalId.split('|');
        const germanWords = germanPart.split(',').map(w => w.trim().toLowerCase());
        const englishWords = englishPart.split(',').map(w => w.trim().toLowerCase());

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
     * Get statistics summary
     */
    getStatsSummary() {
        const user = this.userManager.getCurrentUser();
        const pools = this.getPoolSizes();
        const today = this.getTodayProgress();

        return {
            username: user.username,
            level: user.current_level,
            pools: pools,
            today: today,
            totalWords: Object.keys(user.words).length,
            accuracy: today.attempts > 0
                ? Math.round((today.correct / today.attempts) * 100)
                : 0
        };
    }
}
