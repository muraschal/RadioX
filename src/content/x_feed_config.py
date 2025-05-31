#!/usr/bin/env python3
"""
X-Feed Konfiguration für RadioX
Manuell kuratierte VIP-Accounts für Bitcoin-Maximalist Content
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class XAccount:
    """Konfiguration für einen X-Account."""
    username: str
    display_name: str
    category: str
    priority: float  # 0.0 - 1.0
    keywords: List[str]
    persona_style: str
    description: str

# Manuell kuratierte VIP-Accounts
VIP_ACCOUNTS: Dict[str, XAccount] = {
    "saylor": XAccount(
        username="saylor",
        display_name="Michael Saylor",
        category="bitcoin_og",
        priority=1.0,
        keywords=["bitcoin", "digital property", "energy", "scarcity", "store of value"],
        persona_style="philosophical_maximalist",
        description="MicroStrategy CEO, Bitcoin-Evangelist, Digital Property Philosoph"
    ),
    
    "jack": XAccount(
        username="jack",
        display_name="Jack Dorsey",
        category="bitcoin_og", 
        priority=0.95,
        keywords=["bitcoin", "lightning", "decentralization", "freedom"],
        persona_style="minimalist_maximalist",
        description="Twitter-Gründer, Bitcoin-Maximalist, Dezentralisierungs-Verfechter"
    ),
    
    "jackmallers": XAccount(
        username="jackmallers",
        display_name="Jack Mallers",
        category="lightning_expert",
        priority=0.9,
        keywords=["lightning", "strike", "payments", "adoption", "el salvador"],
        persona_style="energetic_builder",
        description="Strike CEO, Lightning Network Pioneer, Bitcoin-Adoption Catalyst"
    ),
    
    "giacomozucco": XAccount(
        username="giacomozucco",
        display_name="Giacomo Zucco",
        category="bitcoin_educator",
        priority=0.85,
        keywords=["plan b", "education", "technical", "scaling", "philosophy"],
        persona_style="technical_educator",
        description="Bitcoin-Educator, Plan B Verfechter, Technischer Analyst"
    ),
    
    "sunnydecree": XAccount(
        username="sunnydecree", 
        display_name="Sunny Decree",
        category="content_creator",
        priority=0.8,
        keywords=["content", "education", "community", "adoption"],
        persona_style="community_builder",
        description="Bitcoin-Content Creator, Community Builder, Educator"
    ),
    
    "WatcherGuru": XAccount(
        username="WatcherGuru",
        display_name="Watcher Guru",
        category="news_aggregator",
        priority=0.75,
        keywords=["breaking", "news", "market", "updates", "alerts"],
        persona_style="news_reporter",
        description="Crypto News Aggregator, Market Updates, Breaking News"
    )
}

# Kategorien für Content-Filtering
CONTENT_CATEGORIES = {
    "bitcoin_og": {
        "weight": 1.0,
        "intro_style": "Bitcoin-OG {name} meldet sich:",
        "outro_style": "Das war Alpha von {name}!"
    },
    "lightning_expert": {
        "weight": 0.9,
        "intro_style": "Lightning-Update von {name}:",
        "outro_style": "Mehr Lightning-Power von {name}!"
    },
    "bitcoin_educator": {
        "weight": 0.85,
        "intro_style": "Bitcoin-Education mit {name}:",
        "outro_style": "Lernt von {name}, Leute!"
    },
    "content_creator": {
        "weight": 0.8,
        "intro_style": "Community-Update von {name}:",
        "outro_style": "Danke für den Content, {name}!"
    },
    "news_aggregator": {
        "weight": 0.75,
        "intro_style": "Breaking News von {name}:",
        "outro_style": "Bleibt informiert mit {name}!"
    }
}

# Relevanz-Keywords für Filtering
RELEVANCE_KEYWORDS = {
    "high_priority": [
        "bitcoin", "btc", "lightning", "sats", "hodl", "stack sats",
        "digital property", "store of value", "sound money", "hard money",
        "adoption", "orange pill", "bitcoin standard", "hyperbitcoinization"
    ],
    "medium_priority": [
        "crypto", "blockchain", "decentralization", "self custody",
        "not your keys", "peer to peer", "censorship resistance",
        "monetary policy", "inflation", "fiat"
    ],
    "low_priority": [
        "altcoin", "shitcoin", "defi", "nft", "web3", "metaverse"
    ]
}

# Persona-spezifische Tweet-Interpretationen
PERSONA_INTERPRETATIONS = {
    "maximalist": {
        "saylor": "Der Bitcoin-Prophet Saylor verkündet wieder die Wahrheit:",
        "jack": "Jack Dorsey, der Twitter-Gründer und Bitcoin-Maximalist:",
        "jackmallers": "Lightning-Jack Mallers mit heißen Updates:",
        "giacomozucco": "Der italienische Bitcoin-Philosoph Giacomo:",
        "sunnydecree": "Community-Builder Sunny mit Bitcoin-Wisdom:",
        "WatcherGuru": "Breaking News aus dem Bitcoin-Universum:"
    },
    "cyberpunk": {
        "saylor": "Incoming transmission from digital property architect Saylor:",
        "jack": "Decentralization advocate Jack transmits:",
        "jackmallers": "Lightning protocol engineer Mallers reports:",
        "giacomozucco": "Bitcoin protocol analyst Giacomo signals:",
        "sunnydecree": "Community node Sunny broadcasts:",
        "WatcherGuru": "Network alert from Watcher Guru:"
    },
    "retro": {
        "saylor": "Hey Leute, der Bitcoin-Guru Saylor hat was zu sagen:",
        "jack": "Twitter-Legende Jack mit Bitcoin-Vibes:",
        "jackmallers": "Lightning-Rockstar Jack Mallers meldet sich:",
        "giacomozucco": "Der coole Giacomo aus Italien mit Bitcoin-Facts:",
        "sunnydecree": "Sunny bringt die guten Bitcoin-Vibes:",
        "WatcherGuru": "News-Flash von den Watcher Guru Jungs:"
    }
}

# Tweet-Filtering Konfiguration
TWEET_FILTER_CONFIG = {
    "min_engagement": 100,  # Mindest-Likes/Retweets
    "max_age_hours": 24,    # Maximales Alter in Stunden
    "exclude_replies": True, # Keine Antworten
    "exclude_retweets": False, # Retweets erlaubt (für News-Accounts)
    "min_length": 20,       # Mindest-Zeichenanzahl
    "max_length": 280       # Maximum für Radio-Tauglichkeit
}

def get_account_by_username(username: str) -> XAccount:
    """Holt Account-Konfiguration nach Username."""
    return VIP_ACCOUNTS.get(username.lower())

def get_accounts_by_category(category: str) -> List[XAccount]:
    """Holt alle Accounts einer Kategorie."""
    return [acc for acc in VIP_ACCOUNTS.values() if acc.category == category]

def get_high_priority_accounts() -> List[XAccount]:
    """Holt alle High-Priority Accounts (>= 0.9)."""
    return [acc for acc in VIP_ACCOUNTS.values() if acc.priority >= 0.9]

def get_persona_intro(persona: str, username: str) -> str:
    """Generiert Persona-spezifische Intro für Tweet."""
    intros = PERSONA_INTERPRETATIONS.get(persona, {})
    return intros.get(username, f"Update von @{username}:") 