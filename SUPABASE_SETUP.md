# Supabase Setup Guide

This app now uses **Supabase** for persistent data storage, which works seamlessly on Streamlit Community Cloud.

## Quick Setup

### 1. Create a Supabase Account
- Go to [supabase.com](https://supabase.com)
- Sign up for a free account (or log in)

### 2. Create a New Project
- Click "New Project"
- Choose your region
- Set a strong database password (save it somewhere safe)
- Wait for the project to be created (5-10 minutes)

### 3. Create the Database Table
Once your project is ready:
- Go to the "SQL Editor" section
- Click "New Query"
- Paste this SQL and run it:

```sql
CREATE TABLE routines_data (
  id INT PRIMARY KEY,
  data JSONB NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(id)
);
```

### 4. Get Your API Keys
- Go to "Project Settings" → "API"
- Copy your:
  - **Project URL** (SUPABASE_URL)
  - **anon public** key (SUPABASE_KEY)

### 5. Add Secrets to Streamlit

#### For Local Development:
Create a `.streamlit/secrets.toml` file in your project:
```toml
SUPABASE_URL = "your-project-url-here"
SUPABASE_KEY = "your-anon-public-key-here"
```

#### For Streamlit Cloud Deployment:
- Go to your app's settings on Streamlit Cloud
- Navigate to "Secrets"
- Add the same credentials:
```
SUPABASE_URL = "your-project-url-here"
SUPABASE_KEY = "your-anon-public-key-here"
```

### 6. Test Locally
Run the app locally to test:
```bash
streamlit run main.py
```

Your data will now persist across app restarts!

## Fallback Behavior

If Supabase credentials are not configured, the app automatically falls back to local file storage (`routines.json`). This is useful for local development or testing.

## Important Notes

- **Security**: Keep your `SUPABASE_KEY` secret. Never commit `.streamlit/secrets.toml` to git.
- **Free Tier**: Supabase's free tier includes plenty of storage and bandwidth for this app.
- **No Code Changes Needed**: The app automatically detects available credentials and uses the best option.
