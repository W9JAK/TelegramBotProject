-- migrate:up

ALTER TABLE orders
ADD COLUMN is_visible boolean DEFAULT true;

-- migrate:down