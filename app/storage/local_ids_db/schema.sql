PRAGMA foreign_keys = ON;

-- Drop everything (clean start)
DROP TABLE IF EXISTS photos;

-- Minimal index table for your API
CREATE TABLE photos (
  id TEXT PRIMARY KEY,                 -- UUID (string)
  original_filename TEXT NOT NULL,     -- client filename (for auditing)
  created_at TEXT NOT NULL             -- ISO8601 UTC (string)
);

-- Fast paging by newest
CREATE INDEX idx_photos_created_at ON photos (created_at DESC);
