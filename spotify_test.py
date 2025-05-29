import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

# .env laden
load_dotenv()

print("=== Spotify Auth Test (Neustart) ===")
print(f"Client ID: {os.getenv('SPOTIFY_CLIENT_ID')}")
print(f"Redirect URI: {os.getenv('SPOTIFY_REDIRECT_URI')}")

# Stelle sicher, dass wir 127.0.0.1 verwenden
if os.getenv('SPOTIFY_REDIRECT_URI') and 'localhost' in os.getenv('SPOTIFY_REDIRECT_URI'):
    print("⚠️  WARNUNG: Du nutzt noch 'localhost' - bitte ändere es zu '127.0.0.1' in der .env!")

# Umgebungsvariablen setzen (wichtig für Spotipy)
os.environ["SPOTIPY_CLIENT_ID"] = os.getenv("SPOTIFY_CLIENT_ID")
os.environ["SPOTIPY_CLIENT_SECRET"] = os.getenv("SPOTIFY_CLIENT_SECRET")
os.environ["SPOTIPY_REDIRECT_URI"] = os.getenv("SPOTIFY_REDIRECT_URI")

try:
    print("Starte Auth-Flow...")
    sp_oauth = SpotifyOAuth(scope="user-top-read playlist-read-private")
    print("SpotifyOAuth erstellt, hole Token...")
    token_info = sp_oauth.get_access_token(as_dict=False)
    print("SUCCESS: Token erhalten!")
    print(f"Token: {token_info[:50]}...")
except Exception as e:
    print(f"FEHLER: {e}")
    import traceback
    traceback.print_exc() 