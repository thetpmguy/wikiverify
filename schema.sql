-- WikiVerify Database Schema
-- Run this to set up the database

-- Citations table
CREATE TABLE IF NOT EXISTS citations (
    id SERIAL PRIMARY KEY,
    wikipedia_article VARCHAR(500) NOT NULL,
    wikipedia_language VARCHAR(10) DEFAULT 'en',
    citation_number INTEGER,
    source_url TEXT,
    source_doi VARCHAR(100),
    source_title TEXT,
    source_authors TEXT,
    source_journal VARCHAR(500),
    source_year INTEGER,
    snapshot_url TEXT,
    snapshot_date TIMESTAMP,
    last_checked TIMESTAMP,
    status VARCHAR(50) DEFAULT 'unchecked',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Findings table
CREATE TABLE IF NOT EXISTS findings (
    id SERIAL PRIMARY KEY,
    citation_id INTEGER REFERENCES citations(id),
    wikipedia_article VARCHAR(500) NOT NULL,
    problem_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    details TEXT,
    found_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reporting_status VARCHAR(50) DEFAULT 'pending',
    resolved_date TIMESTAMP,
    false_positive BOOLEAN DEFAULT FALSE
);

-- Retractions cache
CREATE TABLE IF NOT EXISTS retractions_cache (
    id SERIAL PRIMARY KEY,
    doi VARCHAR(100) UNIQUE,
    paper_title TEXT,
    retraction_date DATE,
    retraction_reason TEXT,
    source VARCHAR(100),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_citations_doi ON citations(source_doi);
CREATE INDEX IF NOT EXISTS idx_citations_status ON citations(status);
CREATE INDEX IF NOT EXISTS idx_citations_article ON citations(wikipedia_article);
CREATE INDEX IF NOT EXISTS idx_findings_status ON findings(reporting_status);
CREATE INDEX IF NOT EXISTS idx_findings_article ON findings(wikipedia_article);
CREATE INDEX IF NOT EXISTS idx_retractions_doi ON retractions_cache(doi);
