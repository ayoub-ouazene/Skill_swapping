-- Run this once in Neon SQL Editor (or psql) if `users` existed before the `bio` field was added.
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio VARCHAR(2000);
