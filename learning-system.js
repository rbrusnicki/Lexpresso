/**
 * Spaced Repetition Learning System
 * Implements three-pool system: To Learn -> Learning -> Learned
 */

class LearningSystem {
    constructor(userManager) {
        this.userManager = userManager;
        this.LEARNING_POOL_SIZE = 15; // Target size of learning pool
        this.LEARNED_THRESHOLD = 10; // Consecutive correct answers
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

        if (pools.learning < this.LEARNING_POOL_SIZE && toLearnWords.length > 0) {
            // Pool < 10: Always pick from to_learn (100%)
            candidatePool = toLearnWords;
        } else if (pools.learning >= this.LEARNING_POOL_SIZE && learningWords.length > 0) {
            // Pool = 10: Always pick from learning (100%)
            candidatePool = learningWords;
        } else {
            // Fallback
            candidatePool = toLearnWords.length > 0 ? toLearnWords : learningWords;
        }

        if (candidatePool.length === 0) {
            // Fallback: return any available word
            return availableWords[Math.floor(Math.random() * availableWords.length)];
        }

        // Sort candidates by priority:
        // 1. Never seen before (last_seen is null)
        // 2. Least recently seen
        // 3. Lower correct streak (needs more practice)
        candidatePool.sort((a, b) => {
            const statsA = user.words[this.getWordId(a)];
            const statsB = user.words[this.getWordId(b)];

            // Prioritize never seen
            if (!statsA.last_seen && statsB.last_seen) return -1;
            if (statsA.last_seen && !statsB.last_seen) return 1;

            // Then by last seen (ascending - oldest first)
            if (statsA.last_seen !== statsB.last_seen) {
                return (statsA.last_seen || '') < (statsB.last_seen || '') ? -1 : 1;
            }

            // Then by correct streak (ascending - lower streak first)
            return statsA.correct_streak - statsB.correct_streak;
        });

        // Return the best candidate
        return candidatePool[0];
    }

    /**
     * Select a learned word for review (called after graduation)
     * Prioritize: 1) Lower streak, 2) Oldest last_seen
     */
    selectLearnedWordForReview(availableWords) {
        const user = this.userManager.getCurrentUser();

        // Filter to learned words only
        const learnedWords = availableWords.filter(word => {
            const stats = user.words[this.getWordId(word)];
            return stats && stats.status === 'learned';
        });

        if (learnedWords.length === 0) {
            return null;
        }

        // Sort by: 1) Lower streak (riskier), 2) Oldest last_seen
        learnedWords.sort((a, b) => {
            const statsA = user.words[this.getWordId(a)];
            const statsB = user.words[this.getWordId(b)];

            // Prioritize lower streak (closer to threshold = more at risk)
            if (statsA.correct_streak !== statsB.correct_streak) {
                return statsA.correct_streak - statsB.correct_streak;
            }

            // Then by last seen (oldest first)
            return (statsA.last_seen || '') < (statsB.last_seen || '') ? -1 : 1;
        });

        return learnedWords[0];
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
