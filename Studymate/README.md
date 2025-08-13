# Studymate - Production-Grade Study Management Platform

## 🎯 Project Overview
A full-stack study management platform with AI-powered features, real-time collaboration, and comprehensive progress tracking.

## 🏗️ Architecture Overview
```
Studymate/
├── frontend/          # React + TypeScript + TailwindCSS
├── backend/           # Python Flask REST API
├── database/          # PostgreSQL schemas and migrations
├── docs/             # API documentation and guides
└── scripts/          # Deployment and utility scripts
```

## 🚀 Tech Stack

### Frontend
- **React 18** with TypeScript
- **TailwindCSS** for styling
- **React Router** for navigation
- **Axios** for API calls
- **Socket.io-client** for real-time features
- **React Query** for state management
- **React Hook Form** for form handling

### Backend
- **Python Flask** REST API
- **SQLAlchemy** ORM with PostgreSQL
- **Flask-JWT-Extended** for authentication
- **Flask-SocketIO** for real-time features
- **Flask-CORS** for cross-origin requests
- **Cloudinary** for file storage
- **IBM Granite API** for AI features

### Database
- **PostgreSQL** with Supabase
- **SQLAlchemy** migrations
- **Redis** for caching (optional)

### Deployment
- **Frontend**: Vercel
- **Backend**: Render
- **Database**: Supabase PostgreSQL
- **File Storage**: Cloudinary

## 📋 Features

### Core Features
1. **User Authentication**
   - Register/Login with JWT
   - Password reset via email
   - Profile management

2. **Study Planner**
   - Create study schedules
   - AI-powered study recommendations
   - Progress tracking and analytics

3. **Resource Library**
   - Upload and share study materials
   - Categorize by subject/topic
   - Search and filter functionality

4. **Study Groups**
   - Create/join study groups
   - Real-time chat with Socket.io
   - Group video calls (WebRTC)

5. **AI Study Assistant**
   - IBM Granite integration
   - Personalized study tips
   - Question answering
   - Content summarization

6. **Progress Analytics**
   - Study time tracking
   - Performance metrics
   - Achievement badges
   - Weekly/monthly reports

7. **Admin Dashboard**
   - User management
   - Content moderation
   - Analytics overview
   - System health monitoring

## 🏃‍♂️ Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL 13+
- Redis (optional)

### Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd Studymate

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
```

### Environment Variables
Create `.env` files in respective directories:

**Backend (.env)**
```env
FLASK_ENV=development
DATABASE_URL=postgresql://user:pass@localhost/studymate
JWT_SECRET_KEY=your-secret-key
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
IBM_GRANITE_API_KEY=your-ibm-key
REDIS_URL=redis://localhost:6379
```

**Frontend (.env)**
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_SOCKET_URL=http://localhost:5000
```

### Running Locally
```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend
cd frontend
npm start
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Backend (Render)
```bash
# Push to GitHub and connect to Render
# Environment variables configured in Render dashboard
```

## 📚 API Documentation
- Swagger UI: `http://localhost:5000/api/docs`
- Postman collection: `docs/Studymate.postman_collection.json`

## 🤝 Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License
MIT License - see LICENSE file for details
