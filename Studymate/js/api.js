// API Service Layer for Studymate Frontend
const API_BASE_URL = 'http://localhost:5000/api';

class StudymateAPI {
    constructor() {
        this.token = localStorage.getItem('token') || null;
    }

    // Auth methods
    async login(email, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            const data = await response.json();
            if (response.ok) {
                this.token = data.access_token;
                localStorage.setItem('token', this.token);
            }
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    async register(userData) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });
            const data = await response.json();
            if (response.ok) {
                // Automatically login after registration
                await this.login(userData.email, userData.password);
            }
            return data;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }

    async logout() {
        this.token = null;
        localStorage.removeItem('token');
    }

    // Generic request method with auth
    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return response.json();
    }

    // Study groups
    async getStudyGroups() {
        return this.request('/groups');
    }

    async createStudyGroup(groupData) {
        return this.request('/groups', {
            method: 'POST',
            body: JSON.stringify(groupData)
        });
    }

    // Resources
    async getResources() {
        return this.request('/resources');
    }

    async uploadResource(formData) {
        return fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        }).then(res => res.json());
    }

    // Progress tracking
    async getProgress() {
        return this.request('/analytics/progress');
    }

    // Chat messages
    async getMessages(roomId) {
        return this.request(`/study/messages/${roomId}`);
    }

    async sendMessage(roomId, message) {
        return this.request('/study/messages', {
            method: 'POST',
            body: JSON.stringify({ room_id: roomId, message })
        });
    }

    // Ask questions
    async askQuestion(question, context = []) {
        return this.request('/ask', {
            method: 'POST',
            body: JSON.stringify({ question, context })
        });
    }
}

// Create global API instance
const api = new StudymateAPI();
