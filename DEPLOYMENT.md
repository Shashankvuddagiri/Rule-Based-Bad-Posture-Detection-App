# Deployment Guide

## Option 1: GitHub Pages + Render (Recommended)

### Frontend Deployment (GitHub Pages)

1. **Push your code to GitHub:**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Enable GitHub Pages:**
   - Go to your repository settings
   - Scroll to "Pages" section
   - Select "Deploy from a branch"
   - Choose `main` branch and `/frontend/rule_based_bad_posture` folder
   - Save

3. **Update API URL:**
   - Edit `frontend/rule_based_bad_posture/src/PostureCam.jsx`
   - Replace `http://localhost:5000` with your backend URL

### Backend Deployment (Render)

1. **Create Render account and new Web Service**
2. **Connect your GitHub repository**
3. **Configure:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
4. **Set Environment Variables:**
   - `FLASK_ENV=production`
   - `CORS_ORIGIN=https://your-github-pages-url.github.io`

## Option 2: Vercel (Frontend Only)

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Deploy frontend:**
```bash
cd frontend/rule_based_bad_posture
vercel
```

3. **Update vercel.json:**
   - Replace `your-backend-url.com` with actual backend URL

## Option 3: Railway (Full Stack)

1. **Create Railway account**
2. **Connect GitHub repository**
3. **Railway will auto-detect both frontend and backend**
4. **Configure environment variables for CORS**

## Environment Variables

### Backend (.env)
```
FLASK_ENV=production
CORS_ORIGIN=https://your-frontend-domain.com
```

### Frontend
Update API base URL in your React app to point to deployed backend.

## Important Notes

1. **CORS Configuration:** Your backend needs to allow requests from your frontend domain
2. **API URLs:** Update all API calls in frontend to use deployed backend URL
3. **File Uploads:** Ensure your deployment platform supports file uploads
4. **Webcam Access:** HTTPS is required for webcam access in production

## Quick Deploy Commands

```bash
# Commit your changes
git add .
git commit -m "Prepare for deployment"
git push origin main

# Deploy frontend to Vercel
cd frontend/rule_based_bad_posture
vercel --prod

# Deploy backend to Render/Railway
# (Use their web interface)
``` 