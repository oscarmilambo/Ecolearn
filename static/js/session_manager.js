// Session Manager - Optional Enhanced Features
// This file is NOT required for basic dashboard switching
// Use only if you need additional session monitoring features

(function() {
    'use strict';

    // Configuration
    const SESSION_CHECK_INTERVAL = 300000; // Check every 5 minutes (less frequent)
    const SESSION_TIMEOUT_WARNING = 300000; // Warn 5 minutes before timeout

    // Check if user is authenticated and if we should run session checks
    const isAuthenticated = document.querySelector('meta[name="user-authenticated"]')?.content === 'true';
    const currentPath = window.location.pathname;
    
    // Only run session checks on login page or if explicitly enabled
    const shouldRunSessionChecks = currentPath.includes('/login/') || 
                                  document.querySelector('meta[name="enable-session-checks"]')?.content === 'true';
    
    if (!isAuthenticated || !shouldRunSessionChecks) {
        return; // Exit if not authenticated or session checks not needed
    }

    // Session Monitor Class
    class SessionManager {
        constructor() {
            this.lastActivity = Date.now();
            this.warningShown = false;
            this.init();
        }

        init() {
            // Track user activity
            this.trackActivity();
            
            // Periodically check session status
            this.startSessionCheck();
            
            // Listen for dashboard switches
            this.monitorDashboardChanges();
        }

        trackActivity() {
            const events = ['mousedown', 'keypress', 'scroll', 'touchstart'];
            events.forEach(event => {
                document.addEventListener(event, () => {
                    this.lastActivity = Date.now();
                    this.warningShown = false;
                }, { passive: true });
            });
        }

        startSessionCheck() {
            setInterval(() => {
                this.checkSession();
            }, SESSION_CHECK_INTERVAL);
        }

        async checkSession() {
            try {
                const response = await fetch('/accounts/session/status/', {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (!response.ok) {
                    // Only redirect if we're on a protected page
                    if (response.status === 401 || response.status === 403) {
                        this.handleSessionExpired();
                    }
                }
            } catch (error) {
                // Silently fail - don't disrupt user experience
                console.warn('Session check failed (non-critical):', error);
            }
        }

        handleSessionExpired() {
            // Redirect to login with return URL
            const returnUrl = encodeURIComponent(window.location.pathname);
            window.location.href = `/accounts/login/?next=${returnUrl}&session_expired=1`;
        }

        monitorDashboardChanges() {
            // Listen for popstate (back/forward navigation)
            window.addEventListener('popstate', () => {
                this.handleDashboardChange();
            });

            // Intercept dashboard switch links
            document.addEventListener('click', (e) => {
                const link = e.target.closest('a[href*="dashboard"]');
                if (link && link.href) {
                    this.handleDashboardSwitch(link.href);
                }
            });
        }

        handleDashboardChange() {
            // Refresh page if switching between admin/user views
            const path = window.location.pathname;
            if (path.includes('dashboard') || path.includes('admin-dashboard')) {
                // Force reload to ensure correct dashboard loads
                window.location.reload();
            }
        }

        handleDashboardSwitch(targetUrl) {
            const currentPath = window.location.pathname;
            const isCurrentlyAdmin = currentPath.includes('admin-dashboard');
            const isTargetAdmin = targetUrl.includes('admin-dashboard');

            // If switching between different dashboard types
            if (isCurrentlyAdmin !== isTargetAdmin) {
                // Add a slight delay to ensure smooth transition
                setTimeout(() => {
                    window.location.href = targetUrl;
                }, 100);
            }
        }

        showTimeoutWarning() {
            if (this.warningShown) return;
            
            this.warningShown = true;
            const warning = document.createElement('div');
            warning.className = 'fixed top-20 right-4 bg-yellow-100 border-l-4 border-yellow-500 p-4 rounded-lg shadow-lg max-w-sm z-50';
            warning.innerHTML = `
                <div class="flex items-start">
                    <i class="fas fa-exclamation-triangle text-yellow-500 text-lg mr-3"></i>
                    <div class="flex-1">
                        <p class="text-sm font-semibold text-gray-800">Session Expiring Soon</p>
                        <p class="text-xs text-gray-600 mt-1">Your session will expire in 5 minutes. Any activity will extend it.</p>
                    </div>
                    <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            document.body.appendChild(warning);

            // Auto-remove after 10 seconds
            setTimeout(() => warning.remove(), 10000);
        }
    }

    // Initialize session manager
    if (isAuthenticated) {
        new SessionManager();
    }

    // Export for debugging purposes
    window.SessionManager = SessionManager;
})();