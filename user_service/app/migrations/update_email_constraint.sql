-- Drop existing index and constraint
DROP INDEX IF EXISTS ix_users_email;

-- Create new partial index that only includes non-deleted users
CREATE UNIQUE INDEX ix_users_email ON users(email) WHERE deleted_at IS NULL;
