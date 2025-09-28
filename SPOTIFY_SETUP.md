# Spotify Integration Setup Guide

## Prerequisites
1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Spotify API Setup

### Step 1: Create Spotify App
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in:
   - App Name: "Zara Voice Assistant"
   - Description: "Voice-controlled music player"
   - Redirect URI: `http://localhost:8888/callback`
   - Check "Web API" in APIs used

### Step 2: Get Credentials
1. Click on your newly created app
2. Copy the **Client ID**
3. Click "Show Client Secret" and copy the **Client Secret**

### Step 3: Update Configuration
1. Open `config.py`
2. Replace:
   ```python
   SPOTIFY_CLIENT_ID = "your_actual_client_id_here"
   SPOTIFY_CLIENT_SECRET = "your_actual_client_secret_here"
   ```

### Step 4: First-time Authentication
1. Run the application: `python main.py`
2. Say "play song" or "spotify"
3. A browser window will open for Spotify authentication
4. Log in and authorize the app
5. The browser will redirect to localhost (this is normal)
6. Copy the URL from the browser and paste it in the terminal if prompted

## Usage Commands

### English Commands:
- "play song" - Listen for song request
- "play [song name]" - Direct song search
- "spotify" - Open Spotify mode

### Tamil Commands:
- "பாடல் இசை" - Listen for song request
- "இசை இசை" - Play music

## Troubleshooting

### No Active Device Error:
- Open Spotify app on your phone/computer
- Start playing any song (even briefly)
- Try the voice command again

### Authentication Issues:
- Delete `.cache` file (if exists) and re-authenticate
- Make sure redirect URI matches exactly: `http://localhost:8888/callback`

### Song Not Found:
- Try using artist name + song name
- Use English song/artist names for better results

## Examples:
- "Play Shape of You"
- "Play Bohemian Rhapsody by Queen"
- "Play Imagine Dragons Thunder"
