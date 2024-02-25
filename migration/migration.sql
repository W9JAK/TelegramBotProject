CREATE TABLE IF NOT EXISTS public.orders
(
    order_id integer NOT NULL DEFAULT nextval('orders_order_id_seq'::regclass),
    user_id bigint NOT NULL,
    item_id character varying(255) COLLATE pg_catalog."default" NOT NULL,
    amount numeric NOT NULL,
    description text COLLATE pg_catalog."default",
    delivery_selected boolean,
    order_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    message_id integer,
    project_title text COLLATE pg_catalog."default",
    project_description text COLLATE pg_catalog."default",
    project_requirements text COLLATE pg_catalog."default",
    speed_up boolean DEFAULT false,
    courier_delivery boolean DEFAULT false,
    education_institution_name text COLLATE pg_catalog."default",
    has_contents boolean DEFAULT false,
    contents text COLLATE pg_catalog."default",
    project_description_file_id character varying(255) COLLATE pg_catalog."default",
    file_name character varying(255) COLLATE pg_catalog."default",
    file_size integer,
    source_of_information character varying(255) COLLATE pg_catalog."default",
    promo_code character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT orders_pkey PRIMARY KEY (order_id)
);
CREATE TABLE IF NOT EXISTS public.items
(
    item_id integer NOT NULL DEFAULT nextval('items_item_id_seq'::regclass),
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    amount numeric NOT NULL,
    description text COLLATE pg_catalog."default" NOT NULL,
    custom_description text COLLATE pg_catalog."default",
    speed_up_amount numeric,
    speed_up_time character varying(255) COLLATE pg_catalog."default",
    additional_delivery_cost numeric DEFAULT 500,
    CONSTRAINT items_pkey PRIMARY KEY (item_id)
);
CREATE TABLE IF NOT EXISTS public.users
(
    user_id bigint NOT NULL,
    username character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT users_pkey PRIMARY KEY (user_id)
);