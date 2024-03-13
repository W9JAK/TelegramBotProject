-- migrate:up

ALTER TABLE public.items
ADD COLUMN institution_type VARCHAR(255);

ALTER TABLE users
ADD COLUMN institution_type VARCHAR(255);

ALTER TABLE orders
ADD COLUMN institution_type VARCHAR(255);

ALTER TABLE orders
ADD COLUMN contact_method VARCHAR(255);

-- migrate:down
