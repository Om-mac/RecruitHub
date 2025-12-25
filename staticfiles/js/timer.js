/**
 * Timer utility for OTP and rate limiting countdowns
 */

class CountdownTimer {
    constructor(elementId, durationSeconds = 300, onComplete = null) {
        this.element = document.getElementById(elementId);
        this.duration = durationSeconds;
        this.remaining = durationSeconds;
        this.onComplete = onComplete;
        this.intervalId = null;
        this.startTime = null;
    }

    start() {
        if (!this.element) return;
        
        this.startTime = Date.now();
        this.remaining = this.duration;
        
        // Initial display
        this.updateDisplay();
        
        // Update every second
        this.intervalId = setInterval(() => {
            this.remaining = Math.max(0, this.duration - Math.floor((Date.now() - this.startTime) / 1000));
            this.updateDisplay();
            
            if (this.remaining <= 0) {
                this.stop();
                if (this.onComplete) {
                    this.onComplete();
                }
            }
        }, 1000);
    }

    updateDisplay() {
        const minutes = Math.floor(this.remaining / 60);
        const seconds = this.remaining % 60;
        const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        this.element.textContent = timeStr;
        
        // Change color based on remaining time
        if (this.remaining <= 60) {
            this.element.style.color = '#dc3545'; // Red - urgent
        } else if (this.remaining <= 120) {
            this.element.style.color = '#ff6c00'; // Orange - warning
        } else {
            this.element.style.color = '#28a745'; // Green - ok
        }
    }

    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    reset(durationSeconds = null) {
        this.stop();
        if (durationSeconds) {
            this.duration = durationSeconds;
        }
        this.remaining = this.duration;
        this.start();
    }

    getRemaining() {
        return this.remaining;
    }

    isExpired() {
        return this.remaining <= 0;
    }
}

/**
 * Resend OTP button with cooldown timer
 */
class ResendOtpButton {
    constructor(buttonId, cooldownSeconds = 60) {
        this.button = document.getElementById(buttonId);
        this.cooldownSeconds = cooldownSeconds;
        this.timerElement = null;
        this.originalText = this.button ? this.button.textContent : '';
    }

    setCooldown() {
        if (!this.button) return;
        
        this.button.disabled = true;
        this.button.classList.add('disabled');
        this.button.style.opacity = '0.6';
        
        let remaining = this.cooldownSeconds;
        const originalHtml = this.button.innerHTML;
        
        const updateButton = () => {
            const minutes = Math.floor(remaining / 60);
            const seconds = remaining % 60;
            const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            this.button.innerHTML = `<i class="fas fa-clock"></i> Wait ${timeStr}`;
            
            if (remaining > 0) {
                remaining--;
                setTimeout(updateButton, 1000);
            } else {
                this.button.disabled = false;
                this.button.classList.remove('disabled');
                this.button.style.opacity = '1';
                this.button.innerHTML = originalHtml;
            }
        };
        
        updateButton();
    }

    reset() {
        if (this.button) {
            this.button.disabled = false;
            this.button.classList.remove('disabled');
            this.button.style.opacity = '1';
            this.button.innerHTML = this.originalText;
        }
    }
}

/**
 * Rate Limit Handler - Show retry countdown
 */
class RateLimitHandler {
    constructor(containerId = 'rateLimitMessage') {
        this.container = document.getElementById(containerId);
    }

    show(retryAfterSeconds = 900) {
        if (!this.container) {
            this.createContainer();
        }

        this.container.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert" id="rateLimitAlert">
                <div class="mb-3">
                    <i class="fas fa-exclamation-triangle"></i> 
                    <strong>Too Many Attempts</strong>
                </div>
                <p class="mb-2">You've exceeded the maximum number of attempts. Please try again in:</p>
                <div class="alert alert-warning" style="font-size: 1.5rem; text-align: center; font-weight: bold;">
                    <span id="rateLimitTimer">15:00</span>
                </div>
                <small class="text-muted">
                    This is a security measure to protect your account from unauthorized access.
                </small>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        this.container.style.display = 'block';

        // Start countdown
        const timer = new CountdownTimer('rateLimitTimer', retryAfterSeconds, () => {
            this.hide();
        });
        timer.start();
    }

    hide() {
        if (this.container) {
            this.container.style.display = 'none';
        }
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'rateLimitMessage';
        document.body.insertBefore(this.container, document.body.firstChild);
    }
}

/**
 * Initialize timer from data attribute
 * Usage: <div id="timer" data-duration="300"></div>
 */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-start timers with data-duration attribute
    const timerElements = document.querySelectorAll('[data-timer]');
    timerElements.forEach(element => {
        const duration = parseInt(element.dataset.duration) || 300;
        const timer = new CountdownTimer(element.id, duration);
        timer.start();
    });

    // Check for rate limit message (429 response)
    const rateLimitMessage = document.getElementById('rateLimitAlert');
    if (rateLimitMessage) {
        const retryAfter = rateLimitMessage.dataset.retryAfter || 900;
        const handler = new RateLimitHandler();
        handler.show(parseInt(retryAfter));
    }
});
