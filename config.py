import google.generativeai as genai

# Replace this with your actual Gemini API key
genai.configure(api_key="AIzaSyBif5c4kQOeJKpo-aRNQva86h1ldss_ggE")

def get_model():
    return genai.GenerativeModel("gemini-2.0-flash")

# --- Spotify API Configuration ---
# Get these credentials from https://developer.spotify.com/dashboard/
SPOTIFY_CLIENT_ID = "c9a5ff11cec84ed5a3b27baeb8372588"
SPOTIFY_CLIENT_SECRET = "84f3442d474f41c7b41462bd29069a32"
SPOTIFY_REDIRECT_URI = "http://localhost:8080/callback"

# Instructions:
# 1. Go to https://developer.spotify.com/dashboard/
# 2. Create a new app
# 3. Copy the Client ID and Client Secret
# 4. Add http://localhost:8888/callback to Redirect URIs
# 5. Replace the values above with your actual credentials
