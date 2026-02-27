# 🚀 Niyati Project

Stop fighting CORS errors at 2:00 AM, and start building your core product. This project couples a blazing-fast **Next.js 16 (App Router)** frontend with a lightweight, AI-ready **Flask Python** backend.

## ✨ Features Out-of-the-Box

- **Next.js 16 (Turbopack)**: State-of-the-art React rendering with TailwindCSS v4.2 fully configured via PostCSS. Features a custom `not-found.tsx` landing page.
- **Flask Python Backend API**: Lightweight and unopinionated. Built specifically for wrapping Jupyter Notebook logic, TensorFlow scripts, or `openai` API calls quickly.
- **Authentication Built-in**: Complete JSON Web Token (JWT) system using Flask-Bcrypt and SQLite. (Easily switchable to Postgres via SQLAlchemy). Frontend is wrapped in a secure `AuthContext.tsx`.
- **Pre-configured Proxy**: Utilizes Next.js 16's new `proxy.ts` Edge middleware spec.
- **Single-Command Startup**: Shell scripts included to install dependencies and run both servers simultaneously.

---

## 🏗️ Folder Structure

```text
niyati/
├── backend/                  # Python Flask Environment (Port 5000)
│   ├── .env                  # Store OpenAI / Gemini keys here
│   ├── app.py                # Main Flask router & DB init
│   ├── auth.py               # JWT logic & /signup, /login endpoints
│   ├── database.py & models.py # SQLAlchemy setup & User schema
│   ├── requirements.txt      # Python dependencies
│   └── ai_services/          # Isolate your ML scripts here
│       └── llm_agent.py      # The "brain" function being called by app.py
│
├── frontend/                 # Next.js Environment (Port 3000)
│   ├── .env.local            # NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
│   ├── src/app/              # Next.js Routing (page.tsx, layout.tsx, login, signup)
│   ├── src/components/       # Reusable UI (Buttons, Inputs)
│   ├── src/context/          # AuthContext provider
│   └── src/proxy.ts          # Edge interception logic (Next 16 convention)
│
├── start_dev.sh              # Bash startup script (Mac/Linux)
└── start_dev.ps1             # PowerShell startup script (Windows)
```

---

## 🏃 Getting Started

We provide startup scripts that will automatically generate virtual environments, install Python + NPM packages, and spin up both modules contextually.

### Windows (PowerShell)
```powershell
.\start_dev.ps1
```

### Mac/Linux (Bash)
```bash
./start_dev.sh
```

### Manual Startup (If you prefer running two terminal tabs)

**Terminal 1 (Backend):**
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm install
npm run dev
```

---

## 🧠 Connecting your ML Models

To avoid turning `app.py` into a 5,000-line monolith, **do all of your AI processing inside `backend/ai_services/llm_agent.py`**. 

1. Write your custom prompt chains.
2. Initialize LangChain or Transformers.
3. Keep `generate_response()` as the single pipeline that `app.py` calls to return data to the user.

If you ever need to change database providers (e.g., SQLite -> Supabase / Postgres), simply edit `app.config['SQLALCHEMY_DATABASE_URI']` inside `app.py`.

Good luck, and build something awesome!
