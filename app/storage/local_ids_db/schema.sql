-- Clean + recreate (dev-friendly; in prod you'd use migrations)
DROP TABLE IF EXISTS photos;

-- Monotonic sequence for "newest first" (no timestamps needed)
CREATE TABLE photos (
  seq BIGSERIAL PRIMARY KEY,          -- insertion order (newest = highest)
  uuid  TEXT NOT NULL UNIQUE,           -- your UUID
  original_filename TEXT NOT NULL
);
