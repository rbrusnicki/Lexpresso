/**
 * User Management System
 * Handles user login, stats storage, and data persistence
 */

class UserManager {
    constructor() {
        this.currentUser = null;
        this.storagePrefix = 'lexpresso_user_';
        // Use the same host and protocol as the page for API calls (works on phone, computer, and ngrok)
        const protocol = window.location.protocol || 'http:';
        const host = window.location.host || 'localhost:8000';
        this.apiUrl = `${protocol}//${host}/api`;
    }

    /**
     * Login or create a new user (ONLY use server files - no localStorage)
     */
    async login(username) {
        if (!username || username.trim() === '') {
            return { success: false, error: 'Username cannot be empty' };
        }

        const displayName = username.trim();
        const usernameKey = displayName.toLowerCase();

        try {
            // Try to load from server
            const response = await fetch(`${this.apiUrl}/load_user?username=${encodeURIComponent(usernameKey)}`);

            if (response.ok) {
                // User exists on server
                this.currentUser = await response.json();
                this.currentUser.displayName = displayName;
                console.log(`✓ Loaded ${displayName} from server file`);
            } else if (response.status === 404) {
                // New user - create fresh
                this.currentUser = this.createNewUser(usernameKey, displayName);
                await this.saveCurrentUser();
                console.log(`✓ Created new user: ${displayName}`);
            } else {
                return { success: false, error: 'Server error - please make sure server.py is running' };
            }
        } catch (error) {
            console.error('Cannot connect to server:', error);
            return { success: false, error: 'Cannot connect to server. Make sure server.py is running!' };
        }

        return { success: true, user: this.currentUser };
    }

    /**
     * Create a new user object
     */
    createNewUser(username, displayName) {
        return {
            username: username,
            displayName: displayName || username,
            created_date: new Date().toISOString().split('T')[0],
            current_level: 'A1',
            total_sessions: 0,
            words: {},
            daily_stats: {},
            settings: {
                daily_goal: 50,
                learning_pool_size: 50
            }
        };
    }

    /**
     * Get current user
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * Save current user data to server ONLY (no localStorage)
     */
    async saveCurrentUser() {
        if (!this.currentUser) return;

        try {
            const response = await fetch(`${this.apiUrl}/save_user`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.currentUser)
            });

            if (!response.ok) {
                console.error('Failed to save to server!');
            }
        } catch (error) {
            console.error('Cannot save to server:', error);
        }
    }

    /**
     * Logout current user
     */
    logout() {
        this.saveCurrentUser();
        this.currentUser = null;
    }

    /**
     * Export user data as JSON file
     */
    exportUserData() {
        if (!this.currentUser) return null;

        const dataStr = JSON.stringify(this.currentUser, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);

        const link = document.createElement('a');
        link.href = url;
        link.download = `lexpresso_${this.currentUser.username}_${new Date().toISOString().split('T')[0]}.json`;
        link.click();

        URL.revokeObjectURL(url);
    }

    /**
     * Import user data from JSON file
     */
    async importUserData(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = async (e) => {
                try {
                    const userData = JSON.parse(e.target.result);

                    // Validate structure
                    if (!userData.username || !userData.words) {
                        reject('Invalid user data file');
                        return;
                    }

                    // Save to server
                    this.currentUser = userData;
                    await this.saveCurrentUser();

                    resolve(userData);
                } catch (error) {
                    reject('Error parsing user data file');
                }
            };

            reader.onerror = () => reject('Error reading file');
            reader.readAsText(file);
        });
    }

    /**
     * Get today's date string
     */
    getTodayString() {
        return new Date().toISOString().split('T')[0];
    }

    /**
     * Get or create today's stats
     */
    getTodayStats() {
        const today = this.getTodayString();

        if (!this.currentUser.daily_stats[today]) {
            this.currentUser.daily_stats[today] = {
                words_learned: 0,
                total_attempts: 0,
                correct: 0,
                incorrect: 0,
                session_start: new Date().toISOString()
            };
        }

        return this.currentUser.daily_stats[today];
    }

    /**
     * Update today's stats
     */
    updateTodayStats(correct, wordsLearned = 0) {
        const todayStats = this.getTodayStats();

        todayStats.total_attempts++;
        if (correct) {
            todayStats.correct++;
        } else {
            todayStats.incorrect++;
        }
        todayStats.words_learned += wordsLearned;

        this.saveCurrentUser();
    }
}
