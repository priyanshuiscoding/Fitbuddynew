# FitBuddy

Outfit ideas from your wardrobe + a free AI preview image. No payment; uses Hugging Face’s free Inference API.

---

## How to run (step-by-step)

### 1. Open a terminal in the project folder

- **Where:** The folder that contains `app.py` (e.g. `D:\Neurodrobe-wardrobe` or wherever you cloned it).
- **What to do:** Open Command Prompt or PowerShell, then:
  ```bash
  cd D:\Neurodrobe-wardrobe
  ```
  (Replace with your actual path if different.)

---

### 2. Install dependencies

- **Where:** Same terminal, same folder.
- **What to do:**
  ```bash
  pip install -r requirements.txt
  ```
  Wait until it finishes.

---

### 3. Get a free Hugging Face token (for “Show me how it looks”)

- **Where:** In your browser, go to: **https://huggingface.co/settings/tokens**
- **What to do:**
  1. Sign up or log in (free).
  2. Click **“Create new token”**.
  3. Name it anything (e.g. `fitbuddy`), and grant permission to **call Inference Providers**.
  4. Click **Create**, then **copy** the token (starts with `hf_...`).

---

### 4. Put the token in a `.env` file

- **Where:** Inside the project folder (same place as `app.py`).
- **What to do:**
  1. Create a file named `.env` (not `.env.txt` — the app looks for `.env` first, then `.env.txt` as fallback).
  2. Open it and add this line (paste your token after the `=`):
     ```
     HUGGINGFACE_TOKEN=hf_your_copied_token_here
     ```
     Optional model override:
     ```
     HF_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell
     ```
  3. Save the file. If you already have `.env.txt` with the token, the app will load it too.

---

### 5. Start the app

- **Where:** Terminal, project folder.
- **What to do:**
  ```bash
  python app.py
  ```
  You should see something like: `Running on http://0.0.0.0:5000`.

---

### 6. Open the app in the browser

- **Where:** In your browser address bar.
- **What to do:** Go to: **http://localhost:5000**

You can now pick gender, occasion, get outfit ideas, and click **“Show me how it looks”** to generate a free preview image. The first image may take 20–60 seconds (Hugging Face loads the model on first use).

---

## If you don’t set the token

- The app still runs. You can pick gender and occasion and get outfit recommendations.
- Only **“Show me how it looks”** will fail until you add `HUGGINGFACE_TOKEN` to `.env` as in step 4.

---

## Summary

| Step | Where | What to do |
|------|--------|------------|
| 1 | Terminal | `cd` into project folder |
| 2 | Terminal | `pip install -r requirements.txt` |
| 3 | Browser | Go to https://huggingface.co/settings/tokens and create a token, copy it |
| 4 | Project folder | Create `.env` with `HUGGINGFACE_TOKEN=hf_...` |
| 5 | Terminal | `python app.py` |
| 6 | Browser | Open http://localhost:5000 |

All of this is free; no payment or card required.

---

## Deploy from GitHub (optional)

Push this repo to GitHub, then on **Render** or **Railway**: create a new Web Service from the repo, use the **Docker** option, and add environment variable `HUGGINGFACE_TOKEN` with your token. No payment needed for their free tiers.
