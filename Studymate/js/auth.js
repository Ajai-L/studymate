// Authentication Management
class AuthManager {
    constructor() {
        this.isAuthenticated = !!localStorage.getItem('token');
        this.currentUser = null;
        this.init();
    }

    init() {
        if (this.isAuthenticated) {
            this.loadUserProfile();
        }
        this.updateAuthUI();
    }

    async login(email, password) {
        try {
            const response = await api.login(email, password);
            if (response.access_token) {
                this.isAuthenticated = true;
                this.currentUser = response.user;
                this.updateAuthUI();
                window.location.href = '/dashboard.html';
            }
            return response;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }

    async register(userData) {
        try {
            const response = await api.register(userData);
            if (response.message === 'User created successfully') {
                return this.login(userData.email, userData.password);
            }
            return response;
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    }

    logout() {
        api.logout();
        this.isAuthenticated = false;
        this.currentUser = null;
        window.location.href = '/index.html';
    }

    async loadUserProfile() {
        try {
            this.currentUser = { email: 'user@example.com' }; // Placeholder
        } catch (error) {
            console.error('Failed to load user profile:', error);
            this.logout();
        }
    }

    updateAuthUI() {
        const authButtons = document.querySelectorAll('.auth-buttons');
        authButtons.forEach(button => {
            if (this.isAuthenticated) {
                button.innerHTML = `
                    <button onclick="authManager.logout()" class="btn btn-danger">Logout</button>
                `;
            } else {
                button.innerHTML = `
                    <a href="/login.html" class="btn btn-primary">Login</a>
                    <a href="/register.html" class="btn btn-secondary">Register</a>
                `;
            }
        });
    }
}

// Create global auth manager
const authManager = new AuthManager();
