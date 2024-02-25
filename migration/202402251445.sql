-- migrate:up

CREATE TABLE IF NOT EXISTS public.users
(
    user_id INT NOT NULL,
    username character varying(255),
    CONSTRAINT users_pkey PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS public.orders
(
    order_id BIGSERIAL PRIMARY KEY,
    user_id bigint NOT NULL,
    item_id character varying(255),
    amount numeric NOT NULL,
    description text,
    delivery_selected boolean,
    order_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    message_id integer,
    project_title text,
    project_description text,
    project_requirements text,
    speed_up boolean DEFAULT false,
    courier_delivery boolean DEFAULT false,
    education_institution_name text,
    has_contents boolean DEFAULT false,
    contents text,
    project_description_file_id character varying(255),
    file_name character varying(255),
    file_size integer,
    source_of_information character varying(255),
    promo_code character varying(50)
);

CREATE TABLE IF NOT EXISTS public.items
(
    item_id BIGSERIAL PRIMARY KEY,
    name character varying(255),
    amount numeric NOT NULL,
    description text,
    custom_description text,
    speed_up_amount numeric,
    speed_up_time character varying(255),
    additional_delivery_cost numeric DEFAULT 500
);

-- migrate:down