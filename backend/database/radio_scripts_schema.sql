-- RadioX Radio Scripts Table Schema
-- Speichert generierte Radio-Skripte mit allen Metadaten

CREATE TABLE IF NOT EXISTS radio_scripts (
    id TEXT PRIMARY KEY,
    station_type TEXT NOT NULL,
    target_hour TIMESTAMPTZ NOT NULL,
    total_duration_seconds INTEGER NOT NULL DEFAULT 0,
    segment_count INTEGER NOT NULL DEFAULT 0,
    news_count INTEGER NOT NULL DEFAULT 0,
    tweet_count INTEGER NOT NULL DEFAULT 0,
    weather_city TEXT,
    script_data JSONB NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'generated',
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('generated', 'gpt_enhanced', 'audio_ready', 'published')),
    CONSTRAINT valid_station_type CHECK (station_type IN ('breaking_news', 'zueri_style', 'bitcoin_og', 'tradfi_news', 'tech_insider', 'swiss_local'))
);

-- Indexes für bessere Performance
CREATE INDEX IF NOT EXISTS idx_radio_scripts_station_type ON radio_scripts(station_type);
CREATE INDEX IF NOT EXISTS idx_radio_scripts_target_hour ON radio_scripts(target_hour);
CREATE INDEX IF NOT EXISTS idx_radio_scripts_created_at ON radio_scripts(created_at);
CREATE INDEX IF NOT EXISTS idx_radio_scripts_status ON radio_scripts(status);

-- RLS (Row Level Security) aktivieren
ALTER TABLE radio_scripts ENABLE ROW LEVEL SECURITY;

-- Policy für authenticated users
CREATE POLICY IF NOT EXISTS "Allow all operations for authenticated users" ON radio_scripts
    FOR ALL USING (auth.role() = 'authenticated');

-- Policy für anon users (read-only)
CREATE POLICY IF NOT EXISTS "Allow read for anon users" ON radio_scripts
    FOR SELECT USING (true);

-- Kommentare
COMMENT ON TABLE radio_scripts IS 'Speichert generierte Radio-Skripte mit allen Segmenten und Metadaten';
COMMENT ON COLUMN radio_scripts.id IS 'Eindeutige Script ID (z.B. breaking_news_20250601_23_abc123)';
COMMENT ON COLUMN radio_scripts.station_type IS 'Radio Station Type (breaking_news, zueri_style, etc.)';
COMMENT ON COLUMN radio_scripts.target_hour IS 'Ziel-Stunde für die das Skript generiert wurde';
COMMENT ON COLUMN radio_scripts.script_data IS 'Komplettes Skript mit allen Segmenten als JSON';
COMMENT ON COLUMN radio_scripts.metadata IS 'Zusätzliche Metadaten (News-Quellen, Bitcoin Accounts, etc.)';
COMMENT ON COLUMN radio_scripts.status IS 'Status des Skripts (generated, gpt_enhanced, audio_ready, published)';

-- Beispiel-Query für Entwicklung
-- SELECT id, station_type, target_hour, total_duration_seconds, status, created_at 
-- FROM radio_scripts 
-- WHERE station_type = 'breaking_news' 
-- ORDER BY created_at DESC 
-- LIMIT 10; 