#!/usr/bin/env python3
"""
RadioX Web Dashboard
Live-Dashboard mit Bitcoin-OG Tweets und Radio-Controls
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from loguru import logger

from src.content.x_feed import XFeedManager
from src.content.x_feed_config import VIP_ACCOUNTS
from src.utils.config import DEFAULT_PERSONAS

# Lade Umgebungsvariablen
load_dotenv()

# Flask App initialisieren
app = Flask(__name__)
CORS(app)

# Globale Variablen
x_feed_manager = None
current_persona = "maximalist"

def init_x_feed():
    """Initialisiert X-Feed Manager."""
    global x_feed_manager
    try:
        x_feed_manager = XFeedManager()
        if x_feed_manager.enabled:
            logger.info("✅ X-Feed Manager für Dashboard initialisiert")
        else:
            logger.warning("⚠️ X-Feed Manager deaktiviert")
    except Exception as e:
        logger.error(f"❌ X-Feed Manager Initialisierung fehlgeschlagen: {e}")
        x_feed_manager = None

@app.route('/')
def index():
    """RadioX Dashboard Startseite."""
    return render_template('index.html', 
                         personas=DEFAULT_PERSONAS,
                         vip_accounts=VIP_ACCOUNTS,
                         current_persona=current_persona)

@app.route('/api/tweets')
def get_tweets():
    """API Endpoint für aktuelle Tweets."""
    try:
        if not x_feed_manager or not x_feed_manager.enabled:
            return jsonify({
                'error': 'X-Feed Manager nicht verfügbar',
                'tweets': []
            })
        
        # Hole aktuelle Tweets
        tweets = x_feed_manager.get_vip_tweets(count=10, hours_back=24)
        
        # Konvertiere zu JSON-Format
        tweets_data = []
        for tweet in tweets:
            tweets_data.append({
                'username': tweet.username,
                'display_name': tweet.display_name,
                'content': tweet.content,
                'timestamp': tweet.timestamp.isoformat(),
                'engagement_score': tweet.engagement_score,
                'relevance_score': tweet.relevance_score,
                'category': tweet.category,
                'url': tweet.original_url,
                'radio_intro': tweet.radio_intro
            })
        
        return jsonify({
            'success': True,
            'tweets': tweets_data,
            'count': len(tweets_data),
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Tweets: {e}")
        return jsonify({
            'error': str(e),
            'tweets': []
        })

@app.route('/api/radio-segment')
def generate_radio_segment():
    """Generiert Radio-Segment aus aktuellen Tweets."""
    try:
        if not x_feed_manager or not x_feed_manager.enabled:
            return jsonify({'error': 'X-Feed Manager nicht verfügbar'})
        
        persona = request.args.get('persona', current_persona)
        count = int(request.args.get('count', 3))
        
        # Hole Tweets
        tweets = x_feed_manager.get_vip_tweets(count=count, hours_back=24)
        
        if not tweets:
            return jsonify({
                'error': 'Keine aktuellen Tweets verfügbar',
                'segment': 'Keine Bitcoin-Updates von unseren OGs verfügbar.'
            })
        
        # Generiere Radio-Segment
        segment = x_feed_manager.generate_radio_segment(tweets, persona)
        
        return jsonify({
            'success': True,
            'segment': segment,
            'persona': persona,
            'tweet_count': len(tweets),
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Fehler bei Radio-Segment Generierung: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/persona/<persona_name>')
def set_persona(persona_name):
    """Setzt aktuelle Persona."""
    global current_persona
    
    if persona_name in DEFAULT_PERSONAS:
        current_persona = persona_name
        return jsonify({
            'success': True,
            'persona': persona_name,
            'description': DEFAULT_PERSONAS[persona_name].description
        })
    else:
        return jsonify({
            'error': f'Persona "{persona_name}" nicht gefunden',
            'available': list(DEFAULT_PERSONAS.keys())
        })

@app.route('/api/account/<username>')
def get_account_tweets(username):
    """Holt Tweets von einem spezifischen Account."""
    try:
        if not x_feed_manager or not x_feed_manager.enabled:
            return jsonify({'error': 'X-Feed Manager nicht verfügbar'})
        
        if username not in VIP_ACCOUNTS:
            return jsonify({'error': f'Account @{username} nicht in VIP-Liste'})
        
        # Hole User-Info und Tweets
        user = x_feed_manager.client.get_user(username=username)
        if not user.data:
            return jsonify({'error': f'User @{username} nicht gefunden'})
        
        tweets = x_feed_manager.client.get_users_tweets(
            id=user.data.id,
            max_results=10,
            tweet_fields=['created_at', 'public_metrics']
        )
        
        account_data = {
            'username': username,
            'display_name': user.data.name,
            'description': user.data.description,
            'followers': user.data.public_metrics['followers_count'],
            'following': user.data.public_metrics['following_count'],
            'tweets': []
        }
        
        if tweets.data:
            for tweet in tweets.data:
                account_data['tweets'].append({
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat(),
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'url': f"https://x.com/{username}/status/{tweet.id}"
                })
        
        return jsonify(account_data)
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen von @{username}: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/status')
def get_status():
    """System-Status für Dashboard."""
    return jsonify({
        'x_feed_enabled': x_feed_manager is not None and x_feed_manager.enabled,
        'current_persona': current_persona,
        'vip_accounts_count': len(VIP_ACCOUNTS),
        'personas_available': list(DEFAULT_PERSONAS.keys()),
        'server_time': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🎙️ RadioX Dashboard startet...")
    print("=" * 50)
    
    # Initialisiere X-Feed
    init_x_feed()
    
    # Zeige Status
    print(f"📊 Dashboard: http://localhost:5000")
    print(f"🐦 X-Feed: {'✅ Aktiv' if x_feed_manager and x_feed_manager.enabled else '❌ Deaktiviert'}")
    print(f"👑 VIP-Accounts: {len(VIP_ACCOUNTS)}")
    print(f"🎭 Personas: {len(DEFAULT_PERSONAS)}")
    print("=" * 50)
    
    # Starte Flask Server
    app.run(debug=True, host='0.0.0.0', port=5000) 