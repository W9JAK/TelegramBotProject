-- migrate:up

ALTER TABLE items
ADD COLUMN standard_completion_time VARCHAR(255);

ALTER TABLE orders
ADD COLUMN partial_payment_completed BOOLEAN DEFAULT FALSE,
ADD COLUMN payment_status integer DEFAULT 0,
ADD COLUMN order_status integer DEFAULT 0,
ADD COLUMN is_visible boolean DEFAULT true;

-- migrate:down