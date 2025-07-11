# Rule-Based Bad Posture Detection App

A full-stack application for real-time and image-based human posture analysis using rule-based logic and pose estimation. The app provides instant feedback for various postures (squat, desk sitting, pushup, lunge, yoga T-pose) via a React frontend and a Flask backend powered by OpenCV and MediaPipe.

---

## Table of Contents
- [Features](#features)
- [Backend (Flask)](#backend-flask)
- [Frontend (React + Vite)](#frontend-react--vite)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Posture Analysis Logic](#posture-analysis-logic)
- [Sample Assets](#sample-assets)
- [Development](#development)


---

## Features
- Real-time posture detection via webcam or uploaded images/videos
- Rule-based feedback for:
  - Squat
  - Desk Sitting
  - Pushup
  - Lunge
  - Yoga T-pose
- Visual skeleton overlay and confidence scores
- Downloadable feedback reports
- Modern, responsive UI

---


 

---

## Backend (Flask)
- **Location:** `backend/`
- **Main file:** `app.py`
- **Dependencies:**
  - Flask
  - Flask-Cors
  - opencv-python
  - mediapipe
- **Endpoints:**
  - `POST /api/process_frame` — Accepts a base64 image and posture mode, returns feedback, confidences, and landmarks.
  - `GET /api/test_pose` — Runs all posture analyses on a sample image (`test_squat.jpg`).
  - `GET /api/health` — Health check endpoint.
- **Posture Analysis:**
  - Implemented in `posture_analysis.py` using geometric rules on MediaPipe pose landmarks.
  - Each posture (squat, desk, pushup, lunge, yoga T-pose) has a dedicated analysis function.

---

## Frontend (React + Vite)
- **Location:** `frontend/rule_based_bad_posture/`
- **Main file:** `src/PostureCam.jsx`
- **Features:**
  - Webcam capture, image/video upload
  - Mode selection (squat, desk, pushup, lunge, yoga T-pose)
  - Sends frames to backend for analysis
  - Displays feedback cards with confidence and tooltips
  - Visualizes pose skeleton overlay
  - Downloadable JSON report
- **Dependencies:**
  - React, react-dom
  - axios
  - react-webcam
  - Vite (build tool)

---

## Setup & Installation

### Prerequisites
- Python 3.8+
- Node.js 18+

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
- The backend runs on `http://localhost:5000` by default.

### Frontend Setup
```bash
cd frontend/rule_based_bad_posture
npm install
npm run dev
```
- The frontend runs on `http://localhost:5173` by default.

---

## Usage
1. Start both backend and frontend servers as above.
2. Open the frontend in your browser (`http://localhost:5173`).
3. Select a posture mode.
4. Use your webcam, upload an image, or upload a video.
5. Receive instant feedback and visual skeleton overlay.
6. Download feedback report if desired.

---

## Posture Analysis Logic
- **Squat:** Checks back angle, knee position relative to toes, symmetry.
- **Desk Sitting:** Checks neck and back angles for slouching or head tilt.
- **Pushup:** Checks elbow bend, back straightness, hip position.
- **Lunge:** Checks knee-over-ankle, torso uprightness, back leg straightness.
- **Yoga T-pose:** Checks arm straightness, shoulder relaxation, symmetry.
- All logic is in `backend/posture_analysis.py` and uses MediaPipe's 3D pose landmarks.

---

## Sample Assets
- `backend/test_squat.jpg`: Sample image for backend testing (`/api/test_pose`).
- `frontend/rule_based_bad_posture/public/vite.svg`, `src/assets/react.svg`: Used for UI branding.

---

## Development
- **Backend:**
  - Edit or add rules in `posture_analysis.py`.
  - Add new endpoints in `app.py`.
- **Frontend:**
  - Main logic in `src/PostureCam.jsx`.
  - Styles in `src/App.css`, `src/index.css`.
  - UI uses React functional components and hooks.
- **Testing:**
  - Use `/api/test_pose` for backend rule testing.
  - Use frontend UI for end-to-end testing.

---

 