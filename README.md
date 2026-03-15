# ScoutAI 🏆
**Democratized, AI-Powered Sports Talent Assessment**

ScoutAI is a full-stack platform that uses state-of-the-art Computer Vision (CV) to analyze athletic performance from uploaded videos. By combining YOLOv8 (for object tracking), MediaPipe (for biomechanical pose estimation), and XGBoost (for talent scoring), ScoutAI democratizes access to elite-level sports analytics.

## 🌟 Key Features
*   **Multi-Sport Analysis:** Supports Cricket, Basketball, Football, Athletics, and more.
*   **Computer Vision Pipeline:** Tracks player skeletons, ball trajectories, and calculates critical biomechanical metrics (speed, joint angles, acceleration).
*   **AI Talent Scoring:** Contextually grades athletes from "Evaluating" to "Elite".
*   **Cloud Architecture:** Highly available frontend hosted on Vercel, a robust API hosted on Render (with PostgreSQL), and heavy ML operations offloaded to a dedicated Hugging Face Space.
*   **Global Leaderboard:** Rank and compare players based on AI-generated talent scores.
*   **Interactive AI Chatbot:** Talk to a sports-science-aware assistant about training methods.

---

## 🏗️ Architecture
The project is split into three main components:
1.  **Frontend (`scoutai-frontend`)**: React + Vite, TailwindCSS, Framer Motion. Hosted on **Vercel**.
2.  **Backend API (`scoutai-backend`)**: Python Flask API, SQLAlchemy (PostgreSQL). Hosted on **Render**.
3.  **AI Engine**: FastAPI Python worker running on **Hugging Face Spaces** for GPU-intensive Computer Vision tasks.

---

## 🛠️ Step-by-Step Setup Guide

### 1. Prerequisites
You need the following installed on your machine:
*   [Node.js](https://nodejs.org/) (for Frontend)
*   [Python 3.10+](https://www.python.org/downloads/) (for Backend & AI engine)
*   [Git](https://git-scm.com/)

### 2. Getting API Keys
Before running the app, you need accounts and API keys from the following services:

#### A. Cloudinary (For Video/Image Storage)
Cloudinary is used to host videos and pass them to the Hugging Face AI.
*   Go to [Cloudinary](https://cloudinary.com/) and create a free account.
*   In your Dashboard, look for the **API Environment variable**.
*   Copy your `CLOUDINARY_URL` (It looks like `cloudinary://<api_key>:<api_secret>@<cloud_name>`).

#### B. Free PostgreSQL Database (Or Use SQLite locally)
*   If testing locally, the system will automatically create a local `scoutai.db` SQLite file.
*   For cloud deployment, create a free database on [Render](https://render.com/) or [Supabase](https://supabase.com/) and copy the `DATABASE_URL` (e.g., `postgresql://user:password@host/db`).

#### C. Hugging Face AI URL
*   The system offloads AI video processing to Hugging Face. Set the `HF_AI_URL` environment variable to the deployed Space API.
*   *Default (already active):* `https://ak47dev-scoutai-ai.hf.space/analyze`

---

## 💻 Local Development (Scratch to Execution)

### Step 1: Clone the Repository
```bash
git clone https://github.com/akshaybhai123/scout.git
cd scout
```

### Step 2: Set up the Backend (Flask API)
```bash
cd scoutai-backend

# Create and activate a Virtual Environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your Environment Variables file
# Create a file named `.env` in the scoutai-backend folder and add:
# CLOUDINARY_URL=cloudinary://your_key:your_secret@your_cloud_name
# DATABASE_URL=sqlite:///scoutai.db  (Or your PostgreSQL URL)
# HF_AI_URL=https://ak47dev-scoutai-ai.hf.space/analyze

# Run the Flask Server
python main.py
```
*The backend will start at `http://127.0.0.1:8000`*

### Step 3: Set up the Frontend (React)
Open a **new terminal window**.
```bash
cd scoutai-frontend

# Install node modules
npm install

# Run the frontend
npm run dev
```
*The frontend will start at `http://localhost:5173`.*

**Note:** If running locally, you must change `API_BASE_URL` in `scoutai-frontend/src/api/scoutApi.js` from the Render URL to `http://127.0.0.1:8000/api` during development.

---

## ☁️ Deployment Guide

### Deploying the Backend (Render)
1. Push your code to GitHub.
2. Go to [Render](https://render.com/) -> New -> Web Service.
3. Connect your repository.
4. **Root Directory**: `scoutai-backend`
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: `gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:app`
7. **Environment Variables**: Add your `CLOUDINARY_URL`, `DATABASE_URL` (Render PostgreSQL), and `HF_AI_URL`.

### Deploying the Frontend (Vercel)
1. Go to [Vercel](https://vercel.com/) -> Add New Project.
2. Connect your repository.
3. **Framework Preset**: Vite.
4. **Root Directory**: `scoutai-frontend`
5. Ensure `src/api/scoutApi.js` points to your LIVE Render backend URL before deploying.
6. Click **Deploy**. Vercel will process the `vercel.json` file for routing.

---

## 🧠 How the AI Pipeline Works
When you upload a video:
1. **Frontend** calls `/api/upload/video` on the Render backend.
2. **Backend** uploads the raw video file to Cloudinary and saves a "Pending" job in PostgreSQL.
3. **Backend** sends the Cloudinary URL to the **Hugging Face Space** API (`/analyze`).
4. **Hugging Face** runs YOLOv8 and MediaPipe to calculate jumping metrics, sprinting speed, and pose angles. It computes a Talent Score (0-100) using a trained XGBoost model.
5. Hugging Face returns the data to Render.
6. **Render** saves the Final Score and Performance Grade in the PostgreSQL database.
7. **Frontend** polls the background status and reveals the completed Dashboard when 100% is reached!

---
*Built for the future of sports scouting.*
