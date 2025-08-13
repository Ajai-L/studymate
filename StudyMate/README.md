# StudyMate

AI-powered study assistant built with Flask and local IBM Granite models. It can summarize PDFs, generate flashcards, and create competitive exam questions (GATE, JEE, NEET, etc.).

## Features
- Local inference with IBM Granite (no API keys)
- PDF upload and text extraction
- Summarization, flashcards, competitive exam MCQs, and custom prompts
- User accounts, profile editing, chat history per session
- Download AI responses as TXT or PDF
- Responsive UI (Bootstrap), Spring Green theme

## 1) Download and run IBM Granite locally
You can use the Hugging Face model:
- `ibm-granite/granite-3.3-8b-instruct` (recommended if you have a GPU)
- or a smaller variant if resources are limited

Steps:
1. Install Git LFS if needed: `git lfs install`
2. Download a Granite instruct model from Hugging Face (example):
   ```bash
   git clone https://huggingface.co/ibm-granite/granite-3.3-8b-instruct /models/granite-3.3-8b-instruct
   ```
3. Set an environment variable to point to the model folder:
   ```bash
   export GRANITE_MODEL_PATH=/models/granite-3.3-8b-instruct
   ```

Notes:
- The app lazily loads the model at first AI request. Server can start without model installed.
- For CPU-only environments, generation will be slow. Consider smaller models or quantization.

## 2) Install dependencies
Create a virtual environment and install:
```bash
cd StudyMate
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# To start the server without AI calls, these are sufficient:
pip install Flask Flask-WTF Flask-SQLAlchemy pdfplumber PyPDF2 bcrypt python-dotenv
# To enable AI features, install full requirements (heavy):
pip install -r requirements.txt
```

## 3) Run the Flask server
```bash
export FLASK_ENV=development
export SECRET_KEY="change-me"
# Optionally set a custom upload directory (defaults to ./uploads)
# export UPLOAD_FOLDER=/path/to/uploads
# Point to your local Granite model folder
# export GRANITE_MODEL_PATH=/models/granite-3.3-8b-instruct

python app.py
```
The server will run at `http://127.0.0.1:5000`.

## 4) Access the web UI
- Sign up, then log in
- Go to the dashboard, then open the chat
- Upload a PDF (plus icon) or type text
- Choose Summarize, Flashcards, Competitive Exams, or just send a custom prompt

## Notes on models and performance
- The app uses Hugging Face Transformers to load Granite locally. It tries to auto-detect GPU (`device_map="auto"`).
- For smaller memory footprints, consider 4-bit or 8-bit loading via bitsandbytes (not included by default). See Transformers + Accelerate docs.
- Model loading is done lazily in `ai.AIService.load_model()`.

## Database
- SQLite database file `studymate.db` will be created automatically.
- Tables: Users, UploadedFiles, ChatHistory, UserSettings

## Security
- Passwords are hashed (Werkzeug security)
- CSRF protection via Flask-WTF
- Routes `/dashboard`, `/chat`, `/upload-pdf`, `/process-request`, and downloads are protected

## Downloading outputs
- Each AI message can be downloaded as `.txt` or `.pdf` via the download icons/links.

## Project Structure
```
StudyMate/
  app.py
  ai.py
  config.py
  models.py
  pdf_utils.py
  utils.py
  requirements.txt
  README.md
  templates/
    base.html
    login.html
    signup.html
    dashboard.html
    chat.html
  static/
    css/style.css
    js/main.js
    js/chat.js
  uploads/
  instance/
```