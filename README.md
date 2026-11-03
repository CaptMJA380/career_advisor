# CareerAdvisor — AI-Powered Career Mentorship & Roadmap Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-8E75C2.svg?logo=google&logoColor=white)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent, full-stack career guidance application built with **Django** and powered by **Google Gemini AI**. CareerAdvisor acts as a virtual career counselor that guides students, recent graduates, and career changers from broad interest areas into specialized subfields, delivering customized, milestone-based learning roadmaps with realistic duration estimates and recommended resources.

---

## 🌟 Key Features

- **Guided Multi-Turn Consultation**: Employs an intelligent state machine (`await_interest` &rarr; `asked_subtopics` &rarr; `detailed`) that structures broad ambitions into focused specializations.
- **Milestone-Based Roadmaps**: Generates numbered, time-estimated milestones (e.g., *2–4 weeks*, *3–6 months*) with recommended actions, books, platforms, and certifications.
- **Conversation Persistence**: Full multi-turn chats are stored in SQLite and organized by title, allowing users to switch between past conversations or start fresh anytime.
- **Modern Dark Glassmorphic UI**: Designed with a responsive interface featuring conversational chat bubbles, quick-start topic pills, active history selection, and real-time typing indicators.
- **Graceful Error Handling**: Automatically detects missing API keys or upstream service errors and displays actionable in-app alerts without crashing.
- **Rich Markdown Formatting**: Safely formats headings, numbered roadmaps, bullet lists, inline bold text, and code snippets into clean HTML.
- **Django Admin Integration**: Includes a configured administrative dashboard to inspect conversations, message history, and user interactions.

---

## 🏗️ Architecture & Conversational Flow

The bot utilizes a multi-phase conversational workflow:

```
[User Input: Broad Area]
        │
        ▼
[Phase 1: Explore & Subtopics]
• Summary of industry domain
• 5 concise specialization paths
• Prompts user to choose a focus area
        │
        ▼
[User Selection: Specific Subtopic]
        │
        ▼
[Phase 2: Deep Dive & Roadmap]
• Specialized domain breakdown & outlook
• Numbered, time-estimated milestone roadmap
• Curated certifications, books & platforms
        │
        ▼
[Phase 3: Interactive Q&A]
• Follow-up queries, interview prep & tailored advice
```

---

## 📁 Project Structure

```
career_advisor/
├── manage.py                     # Django CLI utility
├── requirements.txt              # Project dependencies
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore configuration
├── db.sqlite3                    # Local SQLite database
│
├── career_advisor/               # Project configuration
│   ├── __init__.py
│   ├── asgi.py                   # ASGI config for async servers
│   ├── settings.py               # Django configuration & env loader
│   ├── urls.py                   # Top-level URL routing
│   └── wsgi.py                   # WSGI config for web servers
│
└── advisor/                      # Main career advisor application
    ├── admin.py                  # Django admin registrations
    ├── apps.py                   # App configuration
    ├── forms.py                  # Career interest forms
    ├── models.py                 # Conversation & Message data models
    ├── tests.py                  # Automated unit test suite
    ├── urls.py                   # App route endpoints
    ├── views.py                  # Gemini AI prompts, formatting & views
    │
    ├── migrations/               # Database schema migrations
    │   ├── 0001_initial.py
    │   └── 0002_conversation_state.py
    │
    └── templates/
        └── advisor/
            └── home.html         # Responsive chat UI with CSS & JS
```

---

## 🚀 Getting Started

Follow these steps to clone, configure, and run the project locally.

### 1. Prerequisites

Make sure you have installed:
- **Python 3.10+** ([Download Python](https://www.python.org/downloads/))
- **Git** ([Download Git](https://git-scm.com/))
- A free **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)

---

### 2. Clone the Repository

```bash
git clone https://github.com/CaptMJA380/career_advisor.git
cd career_advisor
```

---

### 3. Create and Activate a Virtual Environment

It is recommended to use an isolated Python virtual environment:

- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- **Windows (Command Prompt)**:
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```

- **Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

---

### 4. Install Dependencies

Install all required Python packages via `pip`:

```bash
pip install -r requirements.txt
```

*(Packages installed: `Django`, `python-dotenv`, `google-generativeai`)*

---

### 5. Configure Environment Variables

Create your local `.env` configuration file from the example:

```bash
cp .env.example .env
```

Open `.env` in any text editor and add your Google Gemini API key:

```env
# Required: Google Gemini API Key
GOOGLE_API_KEY=your_actual_gemini_api_key_here

# Optional: Model selection & Django options
GEMINI_MODEL=gemini-1.5-flash
DEBUG=True
# SECRET_KEY=optional_custom_secret_key
```

> **Note**: You can obtain a free Gemini API key in seconds at [aistudio.google.com](https://aistudio.google.com/).

---

### 6. Apply Database Migrations

Set up the SQLite database schemas for conversations and messages:

```bash
python manage.py migrate
```

---

### 7. (Optional) Create an Admin User

To access Django's built-in administration dashboard:

```bash
python manage.py createsuperuser
```
Follow the interactive prompts to create an admin username and password.

---

### 8. Run the Development Server

Start the local Django development server:

```bash
python manage.py runserver
```

Once running, visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your web browser.

- **Main Application**: `http://127.0.0.1:8000/`
- **Admin Dashboard**: `http://127.0.0.1:8000/admin/`

---

## 🧪 Running Automated Tests

Run the included automated test suite to verify models and views:

```bash
python manage.py test advisor
```

All tests should pass:
```text
Found 6 test(s).
Creating test database for alias 'default'...
......
----------------------------------------------------------------------
Ran 6 tests in 0.02s

OK
Destroying test database for alias 'default'...
```

---

## ⚙️ Configuration Reference

| Environment Variable | Default Value | Description |
|---|---|---|
| `GOOGLE_API_KEY` | *(None)* | **Required.** Your Gemini API key from Google AI Studio. |
| `GEMINI_MODEL` | `gemini-1.5-flash` | The Gemini model name (e.g., `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash`). |
| `DEBUG` | `True` | Set to `False` in production environments. |
| `SECRET_KEY` | Development key | Secret key used for cryptographic signing in Django. |
| `ALLOWED_HOSTS` | `*` (when debug is on) | Comma-separated list of allowed host/domain names. |

---

## 💡 Recent Project Improvements

1. **Dependency Management**: Added standard `requirements.txt` specifying compatible versions of Django, python-dotenv, and google-generativeai.
2. **Security & Secrets Guarding**: Added a comprehensive `.gitignore` and `.env.example` preventing accidental commits of secret keys, database files, and system artifacts.
3. **Cleaned Architecture**: Removed duplicate nested files (e.g., `career_advisor/career_advisor/manage.py`).
4. **Enhanced Markdown Parsing**: Added custom regex post-processing in `advisor/views.py` to support inline bold, italics, code blocks, numbered milestones, and bullet lists.
5. **Modernized UI/UX**:
   - Integrated quick suggestion pills for 1-click consultation starts.
   - Added interactive typing/loading animations to prevent double-submissions.
   - Added active conversation highlighting in the sidebar.
6. **Automated Unit Testing**: Built a comprehensive test suite in `advisor/tests.py` verifying model behaviors, conversation state initialization, and view rendering.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
