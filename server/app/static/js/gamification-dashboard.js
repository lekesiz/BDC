/**
 * Gamification Dashboard JavaScript Component
 * Provides interactive UI for displaying user progress, achievements, and engagement
 */

class GamificationDashboard {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            apiBaseUrl: '/api/gamification',
            updateInterval: 30000, // 30 seconds
            animationDuration: 300,
            ...options
        };
        
        this.userData = null;
        this.progressData = null;
        this.updateTimer = null;
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadUserProgress();
            this.render();
            this.startAutoUpdate();
            this.bindEvents();
        } catch (error) {
            console.error('Failed to initialize gamification dashboard:', error);
            this.renderError('Failed to load gamification data');
        }
    }
    
    async loadUserProgress() {
        const response = await fetch(`${this.options.apiBaseUrl}/progress/summary`, {
            headers: {
                'Authorization': `Bearer ${this.getAuthToken()}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        this.progressData = data.data;
    }
    
    render() {
        if (!this.container || !this.progressData) return;
        
        this.container.innerHTML = `
            <div class="gamification-dashboard">
                ${this.renderXPSection()}
                ${this.renderBadgesSection()}
                ${this.renderChallengesSection()}
                ${this.renderGoalsSection()}
                ${this.renderStatsSection()}
            </div>
        `;
        
        this.initializeProgressBars();
        this.initializeTooltips();
    }
    
    renderXPSection() {
        const xp = this.progressData.xp;
        const progressPercent = ((xp.total_xp - this.calculateLevelXP(xp.current_level - 1)) / 
                                (this.calculateLevelXP(xp.current_level) - this.calculateLevelXP(xp.current_level - 1))) * 100;
        
        return `
            <div class="xp-section">
                <div class="xp-header">
                    <h3>Level ${xp.current_level}</h3>
                    <div class="xp-total">${xp.total_xp.toLocaleString()} XP</div>
                </div>
                <div class="xp-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progressPercent}%"></div>
                    </div>
                    <div class="xp-next">${xp.xp_to_next_level} XP to level ${xp.current_level + 1}</div>
                </div>
                <div class="streak-info">
                    <div class="streak-current">
                        <span class="streak-icon">🔥</span>
                        <span>${xp.current_streak} day streak</span>
                    </div>
                    <div class="streak-longest">
                        <span class="trophy-icon">🏆</span>
                        <span>Best: ${xp.longest_streak} days</span>
                    </div>
                </div>
                ${xp.xp_multiplier > 1 ? this.renderMultiplierBonus(xp) : ''}
            </div>
        `;
    }
    
    renderMultiplierBonus(xp) {
        const expiresAt = new Date(xp.multiplier_expires_at);
        const timeLeft = this.formatTimeLeft(expiresAt);
        
        return `
            <div class="multiplier-bonus">
                <span class="multiplier-icon">⚡</span>
                <span>${xp.xp_multiplier}x XP Boost</span>
                <span class="multiplier-time">${timeLeft} left</span>
            </div>
        `;
    }
    
    renderBadgesSection() {
        const badges = this.progressData.badges.slice(0, 6); // Show last 6 badges
        
        return `
            <div class="badges-section">
                <div class="section-header">
                    <h4>Recent Achievements</h4>
                    <a href="#" class="view-all" onclick="this.showAllBadges()">View All</a>
                </div>
                <div class="badges-grid">
                    ${badges.map(badge => this.renderBadge(badge)).join('')}
                </div>
            </div>
        `;
    }
    
    renderBadge(userBadge) {
        const badge = userBadge.badge;
        const earnedDate = new Date(userBadge.earned_at).toLocaleDateString();
        
        return `
            <div class="badge-item ${badge.rarity}" data-tooltip="Earned on ${earnedDate}">
                <div class="badge-icon">
                    ${badge.icon_url ? 
                        `<img src="${badge.icon_url}" alt="${badge.name}">` : 
                        this.getDefaultBadgeIcon(badge.category)
                    }
                </div>
                <div class="badge-name">${badge.name}</div>
                <div class="badge-points">+${badge.points_value} XP</div>
            </div>
        `;
    }
    
    renderChallengesSection() {
        const activeChallenges = this.progressData.challenges.filter(c => !c.is_completed).slice(0, 3);
        
        return `
            <div class="challenges-section">
                <div class="section-header">
                    <h4>Active Challenges</h4>
                    <a href="#" class="view-all" onclick="this.showAllChallenges()">View All</a>
                </div>
                <div class="challenges-list">
                    ${activeChallenges.length > 0 ? 
                        activeChallenges.map(challenge => this.renderChallenge(challenge)).join('') :
                        '<div class="no-challenges">No active challenges. <a href="#" onclick="this.exploreChallenge()">Explore challenges</a></div>'
                    }
                </div>
            </div>
        `;
    }
    
    renderChallenge(participation) {
        const challenge = participation.challenge;
        const progress = participation.completion_percentage;
        
        return `
            <div class="challenge-item">
                <div class="challenge-header">
                    <h5>${challenge.title}</h5>
                    <span class="challenge-difficulty ${challenge.difficulty}">${challenge.difficulty}</span>
                </div>
                <div class="challenge-description">${challenge.description}</div>
                <div class="challenge-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <span class="progress-text">${Math.round(progress)}% complete</span>
                </div>
                <div class="challenge-rewards">
                    ${this.renderChallengeRewards(challenge.rewards)}
                </div>
            </div>
        `;
    }
    
    renderGoalsSection() {
        const activeGoals = this.progressData.goals.filter(g => g.is_active && !g.is_completed).slice(0, 3);
        
        return `
            <div class="goals-section">
                <div class="section-header">
                    <h4>Personal Goals</h4>
                    <button class="add-goal-btn" onclick="this.showAddGoal()">+ Add Goal</button>
                </div>
                <div class="goals-list">
                    ${activeGoals.length > 0 ? 
                        activeGoals.map(goal => this.renderGoal(goal)).join('') :
                        '<div class="no-goals">No active goals. Set a goal to track your progress!</div>'
                    }
                </div>
            </div>
        `;
    }
    
    renderGoal(goal) {
        const progress = goal.progress_percentage;
        const deadline = goal.deadline ? new Date(goal.deadline).toLocaleDateString() : null;
        
        return `
            <div class="goal-item">
                <div class="goal-header">
                    <h5>${goal.title}</h5>
                    ${deadline ? `<span class="goal-deadline">Due: ${deadline}</span>` : ''}
                </div>
                <div class="goal-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <span class="progress-text">${goal.current_value}/${goal.target_value}</span>
                </div>
            </div>
        `;
    }
    
    renderStatsSection() {
        const stats = this.progressData.stats;
        
        return `
            <div class="stats-section">
                <h4>Your Stats</h4>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">${stats.total_badges}</div>
                        <div class="stat-label">Badges Earned</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${stats.completed_challenges}</div>
                        <div class="stat-label">Challenges Won</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${stats.active_goals}</div>
                        <div class="stat-label">Active Goals</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${this.progressData.xp.current_level}</div>
                        <div class="stat-label">Current Level</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderChallengeRewards(rewards) {
        if (!rewards) return '';
        
        const rewardsList = [];
        if (rewards.points) rewardsList.push(`${rewards.points} XP`);
        if (rewards.badge_id) rewardsList.push('Badge');
        
        return `<span class="rewards">🎁 ${rewardsList.join(', ')}</span>`;
    }
    
    initializeProgressBars() {
        // Animate progress bars
        const progressBars = this.container.querySelectorAll('.progress-fill');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.transition = `width ${this.options.animationDuration}ms ease-out`;
                bar.style.width = width;
            }, 100);
        });
    }
    
    initializeTooltips() {
        // Initialize tooltips for elements with data-tooltip
        const tooltipElements = this.container.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.getAttribute('data-tooltip'));
            });
            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }
    
    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'gamification-tooltip';
        tooltip.textContent = text;
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
        
        this.currentTooltip = tooltip;
    }
    
    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }
    
    bindEvents() {
        // Event delegation for dynamic content
        this.container.addEventListener('click', (e) => {
            if (e.target.matches('.view-all')) {
                e.preventDefault();
                // Handle view all clicks
            }
        });
    }
    
    startAutoUpdate() {
        this.updateTimer = setInterval(() => {
            this.loadUserProgress().then(() => {
                this.render();
            }).catch(console.error);
        }, this.options.updateInterval);
    }
    
    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }
    
    // Utility methods
    calculateLevelXP(level) {
        if (level <= 1) return 0;
        return Math.floor(100 * Math.pow(level, 1.5));
    }
    
    formatTimeLeft(expiresAt) {
        const diff = expiresAt.getTime() - Date.now();
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        
        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        }
        return `${minutes}m`;
    }
    
    getDefaultBadgeIcon(category) {
        const icons = {
            'learning': '📚',
            'participation': '🎯',
            'social': '👥',
            'mastery': '⭐',
            'consistency': '🔥',
            'special': '🏆'
        };
        return icons[category] || '🏅';
    }
    
    getAuthToken() {
        // This should be implemented based on your auth system
        return localStorage.getItem('auth_token') || '';
    }
    
    renderError(message) {
        this.container.innerHTML = `
            <div class="gamification-error">
                <div class="error-icon">⚠️</div>
                <div class="error-message">${message}</div>
                <button onclick="this.init()" class="retry-btn">Retry</button>
            </div>
        `;
    }
    
    // Public methods for external interaction
    async refreshData() {
        await this.loadUserProgress();
        this.render();
    }
    
    showAllBadges() {
        // Implement modal or navigation to full badges view
        console.log('Show all badges');
    }
    
    showAllChallenges() {
        // Implement modal or navigation to challenges view
        console.log('Show all challenges');
    }
    
    exploreChallenge() {
        // Implement navigation to challenge exploration
        console.log('Explore challenges');
    }
    
    showAddGoal() {
        // Implement goal creation modal
        console.log('Add new goal');
    }
    
    destroy() {
        this.stopAutoUpdate();
        this.hideTooltip();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Progress notification system
class GamificationNotifier {
    constructor() {
        this.notifications = [];
        this.container = null;
        this.createContainer();
    }
    
    createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'gamification-notifications';
        document.body.appendChild(this.container);
    }
    
    showXPGained(amount, reason = '') {
        this.showNotification({
            type: 'xp',
            title: `+${amount} XP`,
            message: reason,
            icon: '⚡',
            duration: 3000
        });
    }
    
    showBadgeEarned(badgeName, badgeIcon = '🏅') {
        this.showNotification({
            type: 'badge',
            title: 'Badge Earned!',
            message: badgeName,
            icon: badgeIcon,
            duration: 5000,
            important: true
        });
    }
    
    showLevelUp(newLevel) {
        this.showNotification({
            type: 'levelup',
            title: `Level Up!`,
            message: `You reached level ${newLevel}`,
            icon: '🎉',
            duration: 5000,
            important: true
        });
    }
    
    showChallengeCompleted(challengeName) {
        this.showNotification({
            type: 'challenge',
            title: 'Challenge Complete!',
            message: challengeName,
            icon: '🏆',
            duration: 4000,
            important: true
        });
    }
    
    showNotification(options) {
        const notification = document.createElement('div');
        notification.className = `gamification-notification ${options.type} ${options.important ? 'important' : ''}`;
        
        notification.innerHTML = `
            <div class="notification-icon">${options.icon}</div>
            <div class="notification-content">
                <div class="notification-title">${options.title}</div>
                <div class="notification-message">${options.message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        this.container.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, options.duration || 3000);
        
        // Slide in animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
    }
}

// Export for use
window.GamificationDashboard = GamificationDashboard;
window.GamificationNotifier = GamificationNotifier;