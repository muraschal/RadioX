import os
from typing import List, Dict
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from loguru import logger

class SpotifyManager:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        
        if not self.client_id or not self.client_secret or not self.redirect_uri:
            raise ValueError("Spotify API Credentials oder Redirect URI nicht gefunden")
            
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope="user-top-read playlist-read-private"
        ))
        
    def get_top_tracks(self, limit: int = 5, time_range: str = "long_term") -> List[Dict]:
        """Holt die Top-Tracks des Users."""
        try:
            results = self.sp.current_user_top_tracks(
                limit=limit,
                time_range=time_range
            )
            
            tracks = []
            for item in results["items"]:
                track = {
                    "name": item["name"],
                    "artists": [artist["name"] for artist in item["artists"]],
                    "duration_ms": item["duration_ms"],
                    "preview_url": item["preview_url"],
                    "album": item["album"]["name"],
                    "spotify_url": item["external_urls"]["spotify"]
                }
                tracks.append(track)
                
            logger.info(f"{len(tracks)} Top-Tracks gefunden")
            return tracks
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Top-Tracks: {e}")
            raise
            
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Holt Tracks von einer Playlist."""
        try:
            results = self.sp.playlist_tracks(playlist_id)
            
            tracks = []
            for item in results["items"]:
                track = item["track"]
                track_info = {
                    "name": track["name"],
                    "artists": [artist["name"] for artist in track["artists"]],
                    "duration_ms": track["duration_ms"],
                    "preview_url": track["preview_url"],
                    "album": track["album"]["name"],
                    "spotify_url": track["external_urls"]["spotify"]
                }
                tracks.append(track_info)
                
            logger.info(f"{len(tracks)} Tracks aus Playlist gefunden")
            return tracks
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Playlist-Tracks: {e}")
            raise
            
    def search_tracks(self, query: str, limit: int = 5) -> List[Dict]:
        """Sucht nach Tracks."""
        try:
            results = self.sp.search(
                q=query,
                limit=limit,
                type="track"
            )
            
            tracks = []
            for item in results["tracks"]["items"]:
                track = {
                    "name": item["name"],
                    "artists": [artist["name"] for artist in item["artists"]],
                    "duration_ms": item["duration_ms"],
                    "preview_url": item["preview_url"],
                    "album": item["album"]["name"],
                    "spotify_url": item["external_urls"]["spotify"]
                }
                tracks.append(track)
                
            logger.info(f"{len(tracks)} Tracks für '{query}' gefunden")
            return tracks
            
        except Exception as e:
            logger.error(f"Fehler bei der Track-Suche: {e}")
            raise 