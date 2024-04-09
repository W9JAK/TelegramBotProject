-- migrate:up

ALTER TABLE orders
ADD COLUMN subscription_discount_applied BOOLEAN DEFAULT FALSE,
DROP COLUMN IF EXISTS courier_delivery,
DROP COLUMN IF EXISTS delivery_selected,
ADD COLUMN is_partial_payment BOOLEAN DEFAULT FALSE;

ALTER TABLE items
ADD COLUMN super_speed_up_amount NUMERIC DEFAULT 0,
ADD COLUMN super_speed_up_time VARCHAR(255) DEFAULT NULL,
DROP COLUMN IF EXISTS additional_delivery_cost;

-- migrate:down