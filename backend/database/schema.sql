-- RadioX Database Schema V2
-- Skalierbare, kategoriebasierte Struktur

-- Content Categories - Hauptkategorien für News/Content
CREATE TABLE content_categories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50), -- Emoji oder Icon-Name
    color VARCHAR(7), -- Hex Color für UI
    is_active BOOLEAN DEFAULT true,
    priority_level INTEGER DEFAULT 1, -- 1=highest, 5=lowest
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content Sources - Flexible Quellen (X Accounts, RSS, APIs)
CREATE TABLE content_sources (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    category_id UUID REFERENCES content_categories(id) ON DELETE CASCADE,
    source_type VARCHAR(20) NOT NULL, -- 'twitter', 'rss', 'api', 'manual'
    name VARCHAR(100) NOT NULL,
    identifier VARCHAR(200) NOT NULL, -- Twitter Handle, RSS URL, API Endpoint
    display_name VARCHAR(100),
    description TEXT,
    avatar_url TEXT,
    follower_count INTEGER,
    is_active BOOLEAN DEFAULT true,
    priority_level INTEGER DEFAULT 1,
    check_interval_minutes INTEGER DEFAULT 15,
    last_checked_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB, -- Flexible zusätzliche Daten
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Streams Table - Erweitert um Kategorien-Mix
CREATE TABLE streams (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_minutes INTEGER DEFAULT 60,
    persona VARCHAR(50) DEFAULT 'cyberpunk',
    status VARCHAR(20) DEFAULT 'planned', -- planned, generating, completed, failed
    category_mix JSONB, -- {"bitcoin": 40, "wirtschaft": 30, "sport": 20, "lokal": 10}
    generated_at TIMESTAMP WITH TIME ZONE,
    file_url TEXT,
    file_size_mb DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Spotify Tracks - Unverändert
CREATE TABLE spotify_tracks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stream_id UUID REFERENCES streams(id) ON DELETE CASCADE,
    spotify_url VARCHAR(500) NOT NULL,
    track_name VARCHAR(255),
    artist_name VARCHAR(255),
    duration_ms INTEGER,
    youtube_url VARCHAR(500),
    local_file_path TEXT,
    position_in_stream INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- News Content - Erweitert um Kategorien und Quellen
CREATE TABLE news_content (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stream_id UUID REFERENCES streams(id) ON DELETE CASCADE,
    category_id UUID REFERENCES content_categories(id),
    source_id UUID REFERENCES content_sources(id),
    content_type VARCHAR(20) NOT NULL, -- 'tweet', 'rss', 'weather', 'api'
    original_text TEXT NOT NULL,
    ai_summary TEXT,
    relevance_score DECIMAL(3,2), -- 0.0 - 1.0
    sentiment_score DECIMAL(3,2), -- -1.0 bis 1.0 (negativ bis positiv)
    position_in_stream INTEGER,
    voice_file_path TEXT,
    metadata JSONB, -- Hashtags, Mentions, Links, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Stream Segments - Unverändert
CREATE TABLE stream_segments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stream_id UUID REFERENCES streams(id) ON DELETE CASCADE,
    segment_type VARCHAR(20) NOT NULL, -- 'music', 'news', 'intro', 'outro', 'ad'
    content_id UUID,
    start_time_seconds INTEGER,
    duration_seconds INTEGER,
    file_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generation Logs - Unverändert
CREATE TABLE generation_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stream_id UUID REFERENCES streams(id) ON DELETE CASCADE,
    step VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content Rules - Automatische Filterregeln pro Kategorie
CREATE TABLE content_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    category_id UUID REFERENCES content_categories(id) ON DELETE CASCADE,
    rule_type VARCHAR(20) NOT NULL, -- 'keyword', 'hashtag', 'mention', 'sentiment'
    rule_value TEXT NOT NULL, -- Keyword, #hashtag, @mention
    action VARCHAR(20) NOT NULL, -- 'include', 'exclude', 'boost', 'lower'
    weight DECIMAL(3,2) DEFAULT 1.0, -- Gewichtung für Relevance Score
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes für Performance
CREATE INDEX idx_streams_status ON streams(status);
CREATE INDEX idx_streams_created_at ON streams(created_at);
CREATE INDEX idx_content_categories_slug ON content_categories(slug);
CREATE INDEX idx_content_sources_category ON content_sources(category_id);
CREATE INDEX idx_content_sources_type ON content_sources(source_type);
CREATE INDEX idx_content_sources_active ON content_sources(is_active);
CREATE INDEX idx_news_content_stream_id ON news_content(stream_id);
CREATE INDEX idx_news_content_category ON news_content(category_id);
CREATE INDEX idx_news_content_source ON news_content(source_id);
CREATE INDEX idx_news_content_relevance ON news_content(relevance_score);
CREATE INDEX idx_spotify_tracks_stream_id ON spotify_tracks(stream_id);
CREATE INDEX idx_stream_segments_stream_id ON stream_segments(stream_id);
CREATE INDEX idx_generation_logs_stream_id ON generation_logs(stream_id);
CREATE INDEX idx_content_rules_category ON content_rules(category_id);

-- Initial Data - Content Categories
INSERT INTO content_categories (name, slug, description, icon, color, priority_level) VALUES
('Bitcoin & Crypto', 'bitcoin', 'Bitcoin, Kryptowährungen, DeFi, Web3', '₿', '#F7931A', 1),
('Wirtschaft & Finanzen', 'wirtschaft', 'Börse, Unternehmen, Märkte, Inflation', '📈', '#2E8B57', 2),
('Technologie', 'tech', 'AI, Software, Hardware, Startups', '🤖', '#4169E1', 2),
('Weltpolitik', 'politik', 'Internationale Politik, Wahlen, Geopolitik', '🌍', '#DC143C', 3),
('Sport', 'sport', 'Fußball, Basketball, Olympia, E-Sports', '⚽', '#FF6347', 4),
('Lokale News', 'lokal', 'Deutschland, Europa, regionale Ereignisse', '🏛️', '#9370DB', 3),
('Wissenschaft', 'wissenschaft', 'Forschung, Medizin, Klima, Space', '🔬', '#20B2AA', 4),
('Entertainment', 'entertainment', 'Filme, Musik, Gaming, Celebrities', '🎬', '#FF1493', 5);

-- Initial Data - Bitcoin Content Sources (deine ursprüngliche Liste)
INSERT INTO content_sources (category_id, source_type, name, identifier, display_name, description, priority_level) VALUES
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'twitter', 'saylor', 'saylor', 'Michael Saylor', 'MicroStrategy CEO, Bitcoin Maximalist', 1),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'twitter', 'jack', 'jack', 'Jack Dorsey', 'Twitter Gründer, Bitcoin Advocate', 1),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'twitter', 'elonmusk', 'elonmusk', 'Elon Musk', 'Tesla CEO, Crypto Wildcard', 2),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'twitter', 'APompliano', 'APompliano', 'Anthony Pompliano', 'Bitcoin Podcaster & Investor', 2),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'twitter', 'PeterMcCormack', 'PeterMcCormack', 'Peter McCormack', 'What Bitcoin Did Host', 2),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'twitter', 'nvk', 'nvk', 'Rodolfo Novak', 'Coinkite CEO, Hardware Security', 3),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'twitter', 'lopp', 'lopp', 'Jameson Lopp', 'Bitcoin Security Expert', 3),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'twitter', 'starkness', 'starkness', 'Elizabeth Stark', 'Lightning Labs CEO', 3),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'twitter', 'pierre_rochard', 'pierre_rochard', 'Pierre Rochard', 'Bitcoin Developer & Educator', 3);

-- Wirtschaft Content Sources
INSERT INTO content_sources (category_id, source_type, name, identifier, display_name, description, priority_level) VALUES
((SELECT id FROM content_categories WHERE slug = 'wirtschaft'), 'twitter', 'business', 'business', 'Business', 'Twitter Business News', 1),
((SELECT id FROM content_categories WHERE slug = 'wirtschaft'), 'twitter', 'markets', 'markets', 'Markets', 'Financial Markets Updates', 1),
((SELECT id FROM content_categories WHERE slug = 'wirtschaft'), 'rss', 'handelsblatt', 'https://www.handelsblatt.com/contentexport/feed/schlagzeilen', 'Handelsblatt', 'Deutsche Wirtschaftsnachrichten', 1),
((SELECT id FROM content_categories WHERE slug = 'wirtschaft'), 'rss', 'finanzen_net', 'https://www.finanzen.net/rss/news', 'Finanzen.net', 'Börse und Finanzen', 2);

-- Tech Content Sources
INSERT INTO content_sources (category_id, source_type, name, identifier, display_name, description, priority_level) VALUES
((SELECT id FROM content_categories WHERE slug = 'tech'), 'twitter', 'verge', 'verge', 'The Verge', 'Tech News & Reviews', 1),
((SELECT id FROM content_categories WHERE slug = 'tech'), 'twitter', 'techcrunch', 'techcrunch', 'TechCrunch', 'Startup & Tech News', 1),
((SELECT id FROM content_categories WHERE slug = 'tech'), 'rss', 'heise', 'https://www.heise.de/rss/heise-atom.xml', 'Heise Online', 'Deutsche Tech News', 1);

-- Sport Content Sources
INSERT INTO content_sources (category_id, source_type, name, identifier, display_name, description, priority_level) VALUES
((SELECT id FROM content_categories WHERE slug = 'sport'), 'twitter', 'espn', 'espn', 'ESPN', 'Sports News & Updates', 1),
((SELECT id FROM content_categories WHERE slug = 'sport'), 'rss', 'kicker', 'https://www.kicker.de/news/fussball/bundesliga/startseite/rss.xml', 'Kicker', 'Deutsche Fußball News', 1);

-- Lokale News Sources
INSERT INTO content_sources (category_id, source_type, name, identifier, display_name, description, priority_level) VALUES
((SELECT id FROM content_categories WHERE slug = 'lokal'), 'rss', 'tagesschau', 'https://www.tagesschau.de/xml/rss2/', 'Tagesschau', 'Deutsche Nachrichten', 1),
((SELECT id FROM content_categories WHERE slug = 'lokal'), 'rss', 'spiegel', 'https://www.spiegel.de/schlagzeilen/index.rss', 'Spiegel Online', 'Deutsche News & Politik', 1);

-- Content Rules - Bitcoin Keywords
INSERT INTO content_rules (category_id, rule_type, rule_value, action, weight) VALUES
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'keyword', 'bitcoin', 'boost', 1.5),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'keyword', 'btc', 'boost', 1.5),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'keyword', 'cryptocurrency', 'include', 1.2),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'keyword', 'blockchain', 'include', 1.1),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'hashtag', '#bitcoin', 'boost', 1.8),
((SELECT id FROM content_categories WHERE slug = 'bitcoin'), 'hashtag', '#btc', 'boost', 1.8);

-- RLS (Row Level Security)
ALTER TABLE content_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE streams ENABLE ROW LEVEL SECURITY;
ALTER TABLE spotify_tracks ENABLE ROW LEVEL SECURITY;
ALTER TABLE news_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE stream_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE generation_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_rules ENABLE ROW LEVEL SECURITY; 