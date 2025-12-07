// Main JavaScript for EcoLearn Platform

// Global utilities
const EcoLearn = {
    // API base URL
    apiBase: '/api/',
    
    // CSRF token helper
    getCSRFToken: function() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    },
    
    // Show loading spinner
    showLoading: function(element) {
        if (element) {
            element.innerHTML = '<div class="spinner mx-auto"></div>';
        }
    },
    
    // Hide loading spinner
    hideLoading: function(element, originalContent) {
        if (element) {
            element.innerHTML = originalContent || '';
        }
    },
    
    // Show notification
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-20 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm fade-in ${
            type === 'success' ? 'bg-green-100 border-green-500 text-green-800' :
            type === 'error' ? 'bg-red-100 border-red-500 text-red-800' :
            type === 'warning' ? 'bg-yellow-100 border-yellow-500 text-yellow-800' :
            'bg-blue-100 border-blue-500 text-blue-800'
        } border-l-4`;
        
        notification.innerHTML = `
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <i class="fas ${
                        type === 'success' ? 'fa-check-circle' :
                        type === 'error' ? 'fa-exclamation-circle' :
                        type === 'warning' ? 'fa-exclamation-triangle' :
                        'fa-info-circle'
                    }"></i>
                </div>
                <div class="ml-3">
                    <p class="text-sm">${message}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-current opacity-70 hover:opacity-100">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    },
    
    // Format currency
    formatCurrency: function(amount, currency = 'ZMW') {
        return new Intl.NumberFormat('en-ZM', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    // Format date
    formatDate: function(dateString) {
        return new Date(dateString).toLocaleDateString('en-ZM', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
};

// Progress tracking
class ProgressTracker {
    constructor(moduleId) {
        this.moduleId = moduleId;
        this.progressBar = document.querySelector('.progress-bar .progress-fill');
    }
    
    updateProgress(percentage) {
        if (this.progressBar) {
            this.progressBar.style.width = `${percentage}%`;
        }
        
        // Update progress text
        const progressText = document.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${percentage}% Complete`;
        }
    }
    
    async markLessonComplete(lessonId) {
        try {
            const response = await fetch(`/learning/lesson/${lessonId}/complete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': EcoLearn.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateProgress(data.completion_percentage);
                EcoLearn.showNotification('Lesson completed!', 'success');
                
                if (data.is_completed) {
                    EcoLearn.showNotification('Congratulations! Module completed!', 'success');
                }
            }
        } catch (error) {
            console.error('Error marking lesson complete:', error);
            EcoLearn.showNotification('Error updating progress', 'error');
        }
    }
}

// Quiz functionality
class QuizManager {
    constructor(quizId) {
        this.quizId = quizId;
        this.answers = {};
        this.timeLeft = 0;
        this.timer = null;
    }
    
    startTimer(minutes) {
        this.timeLeft = minutes * 60;
        this.timer = setInterval(() => {
            this.timeLeft--;
            this.updateTimerDisplay();
            
            if (this.timeLeft <= 0) {
                this.submitQuiz();
            }
        }, 1000);
    }
    
    updateTimerDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        const timerElement = document.querySelector('.quiz-timer');
        
        if (timerElement) {
            timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (this.timeLeft <= 300) { // Last 5 minutes
                timerElement.classList.add('text-red-600');
            }
        }
    }
    
    recordAnswer(questionId, answer) {
        this.answers[questionId] = answer;
    }
    
    async submitQuiz() {
        if (this.timer) {
            clearInterval(this.timer);
        }
        
        try {
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', EcoLearn.getCSRFToken());
            
            Object.keys(this.answers).forEach(questionId => {
                formData.append(`question_${questionId}`, this.answers[questionId]);
            });
            
            const response = await fetch(`/learning/quiz/${this.quizId}/submit/`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showResults(data);
            } else {
                EcoLearn.showNotification(data.error || 'Error submitting quiz', 'error');
            }
        } catch (error) {
            console.error('Error submitting quiz:', error);
            EcoLearn.showNotification('Error submitting quiz', 'error');
        }
    }
    
    showResults(results) {
        const resultsModal = document.createElement('div');
        resultsModal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        resultsModal.innerHTML = `
            <div class="bg-white rounded-lg p-8 max-w-md mx-4">
                <div class="text-center">
                    <i class="fas ${results.passed ? 'fa-check-circle text-green-500' : 'fa-times-circle text-red-500'} text-6xl mb-4"></i>
                    <h2 class="text-2xl font-bold mb-4">${results.passed ? 'Congratulations!' : 'Try Again'}</h2>
                    <p class="text-gray-600 mb-4">
                        You scored ${results.score} out of ${results.total_questions} questions
                    </p>
                    <p class="text-lg font-semibold mb-6">
                        ${results.percentage.toFixed(1)}% (Pass: ${results.pass_percentage}%)
                    </p>
                    <button onclick="location.reload()" class="bg-eco-green text-white px-6 py-2 rounded-lg hover:bg-eco-dark">
                        Continue
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(resultsModal);
    }
}

// Location services for reporting
class LocationService {
    constructor() {
        this.currentLocation = null;
    }
    
    async getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported'));
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                position => {
                    this.currentLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    resolve(this.currentLocation);
                },
                error => {
                    reject(error);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000
                }
            );
        });
    }
    
    async reverseGeocode(lat, lng) {
        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`);
            const data = await response.json();
            return data.display_name || `${lat}, ${lng}`;
        } catch (error) {
            console.error('Reverse geocoding failed:', error);
            return `${lat}, ${lng}`;
        }
    }
}

// Payment processing
class PaymentProcessor {
    constructor() {
        this.pollInterval = null;
    }
    
    async initiatePayment(planId, provider, phoneNumber) {
        try {
            const response = await fetch(`/payments/pay/${planId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': EcoLearn.getCSRFToken()
                },
                body: new URLSearchParams({
                    provider: provider,
                    phone_number: phoneNumber
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.payment_id) {
                    this.pollPaymentStatus(data.payment_id);
                }
                return data;
            } else {
                throw new Error('Payment initiation failed');
            }
        } catch (error) {
            console.error('Payment error:', error);
            throw error;
        }
    }
    
    pollPaymentStatus(paymentId) {
        this.pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/payments/status/${paymentId}/`);
                const data = await response.json();
                
                if (data.status === 'completed') {
                    clearInterval(this.pollInterval);
                    EcoLearn.showNotification('Payment successful!', 'success');
                    setTimeout(() => {
                        window.location.href = '/dashboard/';
                    }, 2000);
                } else if (data.status === 'failed') {
                    clearInterval(this.pollInterval);
                    EcoLearn.showNotification('Payment failed. Please try again.', 'error');
                }
            } catch (error) {
                console.error('Status polling error:', error);
            }
        }, 3000);
    }
    
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute bg-gray-800 text-white text-sm px-2 py-1 rounded z-50';
            tooltip.textContent = this.dataset.tooltip;
            tooltip.style.top = this.offsetTop - 30 + 'px';
            tooltip.style.left = this.offsetLeft + 'px';
            document.body.appendChild(tooltip);
            
            this.addEventListener('mouseleave', function() {
                tooltip.remove();
            }, { once: true });
        });
    });
    
    // Initialize lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
    
    // Initialize form validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
});

// Form validation helper
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('border-red-500');
            isValid = false;
        } else {
            field.classList.remove('border-red-500');
        }
    });
    
    return isValid;
}

// Export for global use
window.EcoLearn = EcoLearn;
window.ProgressTracker = ProgressTracker;
window.QuizManager = QuizManager;
window.LocationService = LocationService;
window.PaymentProcessor = PaymentProcessor;
