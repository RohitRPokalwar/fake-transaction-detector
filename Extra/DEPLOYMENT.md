# 🚀 Deployment Guide: Fake Transaction Detector

This project is ready to be deployed to the web. We recommend **Render.com** as it is free, supports Python natively, and keeps the server memory alive (crucial for the Graph Demo).

### Method 1: Deploy on Render (Recommended)

1.  **Push to GitHub:**
    *   Ensure this code is pushed to your GitHub repository.
    *   (The generated `Procfile` and updated `requirements.txt` are already there).

2.  **Create Account:**
    *   Go to [dashboard.render.com](https://dashboard.render.com/) and sign up with GitHub.

3.  **New Web Service:**
    *   Click **"New +"** -> **"Web Service"**.
    *   Connect your GitHub repository (`fake-transaction-detector`).

4.  **Configure:**
    *   **Name:** `fake-txn-detector` (or unique name)
    *   **Languge:** `Python 3`
    *   **Start Command:** `gunicorn app:app` (It might auto-detect this from Procfile)
    *   **Plan:** Select **"Free"**.

5.  **Deploy:**
    *   Click **"Create Web Service"**.
    *   Wait ~2-3 minutes.

6.  **Done!**
    *   You will get a URL like `https://fake-txn-detector.onrender.com`.
    *   Share this link with the Judges.

---

### Method 2: PythonAnywhere (Alternative)

1.  Sign up at [PythonAnywhere.com](https://www.pythonanywhere.com/).
2.  Go to **Web** tab -> **Add a new web app**.
3.  Select **Flask** -> **Python 3.9**.
4.  In the configuration, point the source code to your uploaded files.
5.  Go to **Consoles** -> **Bash** and run:
    ```bash
    pip install -r requirements.txt
    ```
6.  Reload the app.

---
### ⚠️ Crucial Note for Judge Mode
Because "Judge Mode" uses **in-memory storage** to remember your "Loops" (A->B->C), **Serverless** platforms (like Vercel) are **NOT recommended**. They reset the memory too often.
**Render (Free Tier)** or **PythonAnywhere** are best because they keep one worker alive.
