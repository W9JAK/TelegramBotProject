-- migrate:up

ALTER TABLE users 
    ALTER COLUMN user_id TYPE  bigint;

-- migrate:down
