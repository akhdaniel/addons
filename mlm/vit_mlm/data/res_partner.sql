--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.14
-- Dumped by pg_dump version 9.1.0
-- Started on 2015-02-09 10:05:22 WIB

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 197 (class 1259 OID 152410)
-- Dependencies: 5 2545
-- Name: res_partner; Type: TABLE; Schema: public; Owner: openerp; Tablespace: 
--

CREATE TABLE res_partner (
    id integer NOT NULL,
    name character varying NOT NULL,
    company_id integer,
    comment text,
    ean13 character varying(13),
    create_date timestamp without time zone,
    color integer,
    image bytea,
    use_parent_address boolean,
    active boolean,
    street character varying,
    supplier boolean,
    user_id integer,
    zip character varying(24),
    title integer,
    function character varying,
    country_id integer,
    parent_id integer,
    employee boolean,
    type character varying,
    email character varying,
    vat character varying,
    website character varying,
    lang character varying,
    fax character varying,
    city character varying,
    street2 character varying,
    phone character varying,
    credit_limit double precision,
    write_date timestamp without time zone,
    date date,
    tz character varying(64),
    write_uid integer,
    display_name character varying,
    customer boolean,
    create_uid integer,
    image_medium bytea,
    mobile character varying,
    ref character varying,
    image_small bytea,
    birthdate character varying,
    is_company boolean,
    state_id integer,
    commercial_partner_id integer,
    notify_email character varying NOT NULL,
    message_last_post timestamp without time zone,
    opt_out boolean,
    signup_type character varying,
    signup_expiration timestamp without time zone,
    signup_token character varying,
    last_reconciliation_date timestamp without time zone,
    debit_limit double precision,
    vat_subjected boolean,
    section_id integer,
    sponsor_id integer,
    code character varying,
    parent_left integer,
    parent_right integer,
    state character varying NOT NULL,
    path character varying,
    path_ltree ltree,
    website_meta_description text,
    website_description text,
    website_meta_keywords character varying,
    website_meta_title character varying,
    website_short_description text,
    website_published boolean,
    calendar_last_notif_ack timestamp without time zone,
    date_localization date,
    partner_latitude numeric,
    partner_longitude numeric,
    partner_weight integer,
    date_review date,
    activation integer,
    date_review_next date,
    date_partnership date,
    assigned_partner_id integer,
    grade_id integer
);


ALTER TABLE public.res_partner OWNER TO openerp;

--
-- TOC entry 4657 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.comment; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.comment IS 'Notes';


--
-- TOC entry 4658 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.ean13; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.ean13 IS 'EAN13';


--
-- TOC entry 4659 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.create_date; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.create_date IS 'Created on';


--
-- TOC entry 4660 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.color; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.color IS 'Color Index';


--
-- TOC entry 4661 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.image; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.image IS 'Image';


--
-- TOC entry 4662 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.use_parent_address; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.use_parent_address IS 'Use Company Address';


--
-- TOC entry 4663 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.active; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.active IS 'Active';


--
-- TOC entry 4664 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.street; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.street IS 'Street';


--
-- TOC entry 4665 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.supplier; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.supplier IS 'Supplier';


--
-- TOC entry 4666 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.user_id; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.user_id IS 'Salesperson';


--
-- TOC entry 4667 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.zip; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.zip IS 'Zip';


--
-- TOC entry 4668 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.title; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.title IS 'Title';


--
-- TOC entry 4669 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.function; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.function IS 'Job Position';


--
-- TOC entry 4670 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.country_id; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.country_id IS 'Country';


--
-- TOC entry 4671 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.parent_id; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.parent_id IS 'Related Company';


--
-- TOC entry 4672 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.employee; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.employee IS 'Employee';


--
-- TOC entry 4673 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.type; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.type IS 'Address Type';


--
-- TOC entry 4674 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.email; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.email IS 'Email';


--
-- TOC entry 4675 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.vat; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.vat IS 'TIN';


--
-- TOC entry 4676 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.website; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.website IS 'Website';


--
-- TOC entry 4677 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.lang; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.lang IS 'Language';


--
-- TOC entry 4678 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.fax; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.fax IS 'Fax';


--
-- TOC entry 4679 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.city; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.city IS 'City';


--
-- TOC entry 4680 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.street2; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.street2 IS 'Street2';


--
-- TOC entry 4681 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.phone; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.phone IS 'Phone';


--
-- TOC entry 4682 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.credit_limit; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.credit_limit IS 'Credit Limit';


--
-- TOC entry 4683 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.write_date; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.write_date IS 'Last Updated on';


--
-- TOC entry 4684 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.date; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.date IS 'Date';


--
-- TOC entry 4685 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.tz; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.tz IS 'Timezone';


--
-- TOC entry 4686 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.write_uid; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.write_uid IS 'Last Updated by';


--
-- TOC entry 4687 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.display_name; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.display_name IS 'Name';


--
-- TOC entry 4688 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.customer; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.customer IS 'Customer';


--
-- TOC entry 4689 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.create_uid; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.create_uid IS 'Created by';


--
-- TOC entry 4690 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.image_medium; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.image_medium IS 'Medium-sized image';


--
-- TOC entry 4691 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.mobile; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.mobile IS 'Mobile';


--
-- TOC entry 4692 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.ref; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.ref IS 'Contact Reference';


--
-- TOC entry 4693 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.image_small; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.image_small IS 'Small-sized image';


--
-- TOC entry 4694 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.birthdate; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.birthdate IS 'Birthdate';


--
-- TOC entry 4695 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.is_company; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.is_company IS 'Is a Company';


--
-- TOC entry 4696 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.state_id; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.state_id IS 'State';


--
-- TOC entry 4697 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.commercial_partner_id; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.commercial_partner_id IS 'Commercial Entity';


--
-- TOC entry 4698 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.notify_email; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.notify_email IS 'Receive Inbox Notifications by Email';


--
-- TOC entry 4699 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.message_last_post; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.message_last_post IS 'Last Message Date';


--
-- TOC entry 4700 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.opt_out; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.opt_out IS 'Opt-Out';


--
-- TOC entry 4701 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.signup_type; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.signup_type IS 'Signup Token Type';


--
-- TOC entry 4702 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.signup_expiration; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.signup_expiration IS 'Signup Expiration';


--
-- TOC entry 4703 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.signup_token; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.signup_token IS 'Signup Token';


--
-- TOC entry 4704 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.last_reconciliation_date; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.last_reconciliation_date IS 'Latest Full Reconciliation Date';


--
-- TOC entry 4705 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.debit_limit; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.debit_limit IS 'Payable Limit';


--
-- TOC entry 4706 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.vat_subjected; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.vat_subjected IS 'VAT Legal Statement';


--
-- TOC entry 4707 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.section_id; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.section_id IS 'Sales Team';


--
-- TOC entry 4708 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.sponsor_id; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.sponsor_id IS 'Sponsor ID';


--
-- TOC entry 4709 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.code; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.code IS 'Code';


--
-- TOC entry 4710 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.state; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.state IS 'Status';


--
-- TOC entry 4711 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.path; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.path IS 'Path';


--
-- TOC entry 4712 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.website_meta_description; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.website_meta_description IS 'Website meta description';


--
-- TOC entry 4713 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.website_description; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.website_description IS 'Website Partner Full Description';


--
-- TOC entry 4714 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.website_meta_keywords; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.website_meta_keywords IS 'Website meta keywords';


--
-- TOC entry 4715 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.website_meta_title; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.website_meta_title IS 'Website meta title';


--
-- TOC entry 4716 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.website_short_description; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.website_short_description IS 'Website Partner Short Description';


--
-- TOC entry 4717 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.website_published; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.website_published IS 'Publish';


--
-- TOC entry 4718 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.calendar_last_notif_ack; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.calendar_last_notif_ack IS 'Last notification marked as read from base Calendar';


--
-- TOC entry 4719 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.date_localization; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.date_localization IS 'Geo Localization Date';


--
-- TOC entry 4720 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.partner_latitude; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.partner_latitude IS 'Geo Latitude';


--
-- TOC entry 4721 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.partner_longitude; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.partner_longitude IS 'Geo Longitude';


--
-- TOC entry 4722 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.partner_weight; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.partner_weight IS 'Grade Weight';


--
-- TOC entry 4723 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.date_review; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.date_review IS 'Latest Partner Review';


--
-- TOC entry 4724 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.activation; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.activation IS 'Activation';


--
-- TOC entry 4725 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.date_review_next; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.date_review_next IS 'Next Partner Review';


--
-- TOC entry 4726 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.date_partnership; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.date_partnership IS 'Partnership Date';


--
-- TOC entry 4727 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.assigned_partner_id; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.assigned_partner_id IS 'Implemented by';


--
-- TOC entry 4728 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN res_partner.grade_id; Type: COMMENT; Schema: public; Owner: openerp
--

COMMENT ON COLUMN res_partner.grade_id IS 'Grade';


--
-- TOC entry 196 (class 1259 OID 152408)
-- Dependencies: 197 5
-- Name: res_partner_id_seq; Type: SEQUENCE; Schema: public; Owner: openerp
--

CREATE SEQUENCE res_partner_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.res_partner_id_seq OWNER TO openerp;

--
-- TOC entry 4729 (class 0 OID 0)
-- Dependencies: 196
-- Name: res_partner_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openerp
--

ALTER SEQUENCE res_partner_id_seq OWNED BY res_partner.id;


--
-- TOC entry 4730 (class 0 OID 0)
-- Dependencies: 196
-- Name: res_partner_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openerp
--

SELECT pg_catalog.setval('res_partner_id_seq', 95, true);


--
-- TOC entry 4627 (class 2604 OID 152413)
-- Dependencies: 196 197 197
-- Name: id; Type: DEFAULT; Schema: public; Owner: openerp
--

ALTER TABLE res_partner ALTER COLUMN id SET DEFAULT nextval('res_partner_id_seq'::regclass);


--
-- TOC entry 4654 (class 0 OID 152410)
-- Dependencies: 197
-- Data for Name: res_partner; Type: TABLE DATA; Schema: public; Owner: openerp
--

COPY res_partner (id, name, company_id, comment, ean13, create_date, color, image, use_parent_address, active, street, supplier, user_id, zip, title, function, country_id, parent_id, employee, type, email, vat, website, lang, fax, city, street2, phone, credit_limit, write_date, date, tz, write_uid, display_name, customer, create_uid, image_medium, mobile, ref, image_small, birthdate, is_company, state_id, commercial_partner_id, notify_email, message_last_post, opt_out, signup_type, signup_expiration, signup_token, last_reconciliation_date, debit_limit, vat_subjected, section_id, sponsor_id, code, parent_left, parent_right, state, path, path_ltree, website_meta_description, website_description, website_meta_keywords, website_meta_title, website_short_description, website_published, calendar_last_notif_ack, date_localization, partner_latitude, partner_longitude, partner_weight, date_review, activation, date_review_next, date_partnership, assigned_partner_id, grade_id) FROM stdin;
85	Andi	1	\N	\N	2015-02-07 10:38:37.000601	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	\N	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	0	2015-02-08 23:12:48.750584	\N	\N	1	Andi	t	1	\N	\N	\N	\N	\N	t	\N	85	always	\N	f	\N	\N	\N	\N	\N	f	\N	\N	076	\N	\N	open	076	076	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
87	Dodo Dukun	1	\N	\N	2015-02-07 10:52:14.620353	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	85	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	0	2015-02-08 07:35:04.067394	\N	\N	1	Dodo Dukun	t	1	\N	\N	\N	\N	\N	t	\N	87	always	\N	f	\N	\N	\N	\N	\N	f	\N	\N	078	\N	\N	open	076.078	076.078	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
89	Dedi	1	\N	\N	2015-02-07 14:24:16.757042	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	86	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	0	2015-02-07 14:24:19.248338	\N	\N	1	Dedi	t	1	\N	\N	\N	\N	\N	t	\N	89	always	\N	f	\N	\N	\N	\N	\N	f	\N	\N	080	\N	\N	open	076.077.080	076.077.080	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
90	Jojo	1	\N	\N	2015-02-07 14:24:58.66527	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	88	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	0	2015-02-08 02:22:23.033161	\N	\N	1	Jojo	t	1	\N	\N	\N	\N	\N	t	\N	90	always	\N	f	\N	\N	\N	\N	\N	f	\N	\N	081	\N	\N	aktif	076.077.079.081	076.077.079.081	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
91	Aji	1	\N	\N	2015-02-07 14:39:51.382882	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	87	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	0	2015-02-08 02:17:56.987664	\N	\N	1	Aji	t	1	\N	\N	\N	\N	\N	t	\N	91	always	\N	f	\N	\N	\N	\N	\N	f	\N	\N	082	\N	\N	aktif	076.078.082	076.078.082	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
93	Noni	1	\N	\N	2015-02-08 02:23:29.453638	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	88	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	0	2015-02-08 02:23:34.233194	\N	\N	1	Noni	t	1	\N	\N	\N	\N	\N	t	\N	93	always	\N	f	\N	\N	\N	\N	\N	f	\N	\N	084	\N	\N	aktif	076.077.079.084	076.077.079.084	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
94	Meli	1	\N	\N	2015-02-08 02:30:59.131512	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	89	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	0	2015-02-08 02:31:00.955272	\N	\N	1	Meli	t	1	\N	\N	\N	\N	\N	t	\N	94	always	\N	f	\N	\N	\N	\N	\N	f	\N	\N	085	\N	\N	open	076.077.080.085	076.077.080.085	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
95	Moni	1	\N	\N	2015-02-08 02:31:14.429967	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	89	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	0	2015-02-08 02:31:20.83126	\N	\N	1	Moni	t	1	\N	\N	\N	\N	\N	t	\N	95	always	\N	f	\N	\N	\N	\N	\N	f	\N	\N	086	\N	\N	aktif	076.077.080.086	076.077.080.086	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
1	Your MLM Company	1	\N	\N	\N	0	\N	\N	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	contact	info@yourcompany.com	\N	http://www.yourcompany.com	\N	\N	\N	\N	\N	0	2015-02-08 07:03:45.432201	\N	\N	1	Your MLM Company	f	\N	\N	\N	\N	\N	\N	t	\N	1	always	\N	\N	\N	\N	\N	\N	0	\N	\N	1	\N	\N	\N	open	\N	\N	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
86	Bani	1	\N	\N	2015-02-07 10:38:46.284763	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	85	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	0	2015-02-07 14:23:06.212229	\N	\N	1	Bani	t	1	\N	\N	\N	\N	\N	t	\N	86	always	\N	f	\N	\N	\N	\N	\N	f	\N	\N	077	\N	\N	open	076.077	076.077	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
88	Doni Dores	1	\N	\N	2015-02-07 10:57:17.287346	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	86	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	0	2015-02-08 07:36:35.67563	\N	\N	1	Doni Dores	t	1	\N	\N	\N	\N	\N	t	\N	88	always	\N	f	\N	\N	\N	\N	\N	f	\N	\N	079	\N	\N	open	076.077.079	076.077.079	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
92	Vera	1	\N	\N	2015-02-07 14:49:43.241147	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	87	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	0	2015-02-08 02:17:32.362302	\N	\N	1	Vera	t	1	\N	\N	\N	\N	\N	t	\N	92	always	\N	f	\N	\N	\N	\N	\N	f	\N	\N	083	\N	\N	aktif	076.078.083	076.078.083	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
4	Public user	1	\N	\N	2015-02-02 07:30:03.31094	0	\\x6956424f5277304b47676f414141414e5355684555674141414a594141414357434141414141415a6169342b4141414d51456c45515652346e4f3263653477563152334876372f666d6276720a506c69515a574558574667574546675142524e4930645a5737657550786c695452684e6257354e6174616d6d6f6161504e4b6d704b52596955756e44467a4555323859596b526169615830680a596855454c4170614b4739306c32565a646d566c325758766e505072482f63314d3364327557646d65507a4237352b39642b374d6d632f387a6a6d2f2b54334f57524a63694d4c6e477942630a4c6d4c5a7945557347376d495a534e4f416d324951414151514141454168425272435970726a6b5649364750706b5846494975484a59594a36442f5773622b393766694a6b33333941305a560a4461386250336c47347868416a446f6657474955634f6966573363654f4672303236513556393830435362713249324235546f343964494c4c2f5941514534746b686c663041424733507a740a612b46473745714a4b455a4c312f495a414e674a757a4d7242707876764375696f375165466373565754734c55454d6f677853683749454263633864566c72616279656f4d34306352666a530a3369686330624330624a6f4f703552356c6b4c54316768636b6243305756316271694632305043422f66694b70713330565569565267556f7a4f675559336d44614861464b6b6d586571354f0a2f58656873545644456332647a5833537a71703158504a545a43525244344b59772b794679424a746156535478474978526b4b6d70365a4e47396e594e5a5551456741796f36365a6e5172540a697a4c50773235304a5966462b4f6d4847375a73756b574b75517a6548314232584a454d6848743130664d342b48484744507751526631497144316f5a377553306862706b66635944576a350a31566754314a656f342b3132765a68594a38716f4f6c61416b72715773476474743273744d57336c664336527957472f6e375a724c766e496830346d634a2b6b73597a71574538684e6d71590a58544d52417a4a574158764f78414267444e2f58706f72654e454c31734c4c7a456246366465445747723041744f4b467a78612f2f386730314e713148784672666d557130464f3655596d620a36723337476363744f70746b7975687a6f53312b4e476962424d5355326e54667531784d425a59705a646f715a6f79475263566576474631597647792f6c51363548516a31316d2b45794d480a5a4834787270692f7a52706b596850564862483054355042636b5665755159594a447054754d3832796b67454b7932643338576734526e7a73492b4d5a5a4352424a615756793444447a716b0a55316873485a496c674f584b436d6549514d6a426c31316a472f6e4578334a6c6c614a423332475577685774316c5478736253385644343446514d33744562496a7354464d755a6b533745370a6d6f4e79634d6e502b71506b624f4a6975624a384d4a4e4d43766a4b5a72474f714250414d695a394859557169787967655a56494f67705665447132644246756652396849614453627431640a39395244523774425843783048412b4c544a55752b384739552b43576c47784b486976635353665331793561414d3252577a38725651796d6e372b36514a735969666b6b71686842596633670a4c3033306e4478775672536c7a4e642f34635a732b437867476271624237663770556e385475514141556e56566247664e6a61574d5558324956306574394834574a575448543858365a70590a6f7a3354534e7a436e54355662416171346855546b514457325a4834517a3737584349696f45774b494c61796b744a5776714b705133504e3170494d6c6c59342f663768343272386c6655770a695a6a4365503557526c78702f33564c4a5141304c6a7757725941596b43537758486d314751413744675054647966426c556841746959464a7a7659485577376f694d3570416c6a61624f370a786a4f6855376774557233564c2f484870394244505a36636c71756532367a734b696b684568744c2b4d413662374a556147424e3344595477444b3071307645643242542f443549774d696b0a2f5655656b62326e624a4e73525a4941566c4657704e65794e68416943616837516b31414e7a5758784730305068615a47584e394c6a4c546e497151347032644a4741672b45346642636e580a77736f5964684c2f5653335158333239594c685336566e76564d5633625749625a44467963414a53544142497056442f586749767857526531522f4e4261415541356766595931497353546b0a3250517361676141696e6c50395358693243546a4268704739355a75553945776a354a7841784e7a6d6a4f4f6a5a454c79576b4749455a41635750387646796741646b46756b72334970614e0a584d53796b65673543492f62454d676b35582f516b566543527a4d51496961386475452f69774452464d5841576d506c6955366f367577687339655436715a3039646773564e64543832614f0a42674174624b6b316d3034556759435a6f6274323748684c4c63746d3134773873325259626b6b4747313764494179417a4d6868317a5733744d796230356743524a4f336530753456306c690a64446f544b33652f75664c657a39637156473750757770476677734f6373482b732f6d67327055484161427137766566664b4e4c52455453626f6c3567424b776a45366e745968492f34462f0a50587a6a704449416f496f33437947396c72344663454245354743524a3952333554736f5a7742494e642b3866454e6242693164516f35696143786a584e635645546e6476664833643377750a733142474f61714d56737041345451746879654441544475394662716a48747950685378796b7950385466632f2b796555794969326e574839736f47787a49366e626e44774f3756393139620a54316b694a6f4c43627954745064655672574e4159487a5472776f744235764141496956777742514f65763246652f31696f69596f586f30464d746f4e33504a774b483153322b396645786d0a4d4475356d61357768306e3772306a4c596a68454666734376716b722f7836574e7843555856302f6650704e6939642f724556453943427352544e5252444b72502f70326276356f352b344f0a4148426752504a6c416156762f454e773153755a6b344441394158736a58495850486b725a61325161494441394e6d4a58577451502b504b326463304f51786f6f4d693065624545526b67520a595062763272487a6e634d61414250452b42595a735a37335645567751524c5441516951506a6f7a774f5734742b7835774a4f536b437946744c6576522f6e7342624e6d543638426f4958590a4738586c735453596f4b41507457336274723331474141775333486c42495362363979676b6b6e76676f444e6b614b6b434a76764c5434564d4e6f474144484d3653316255466c2f2b6678350a6b386156417a43654371536e512f76337648442f3966575a786b4c336657522b5173754a344a495a4978306a514642594b6f46424a326e35306141326d7a68624e4b373977734a2f375064650a6d6364362b36486257696f5a414b6e6775722b414b50776c6d4962553868594463504354494a5932483159506164794a4d2f476c717035373535384f354e61585a4c434d6b65734277456d560a554d686c584e55586d44367572414142446d344a41727479313643724e7a7873796e4541344a6e6335526c2f697779616e584b476d395a6e666e55627457316459484f426f42554d434872410a7667594d2f2b2b764a53524b524c73754f4655354d7a66734f646675424e637450632f795747416d45766144414d474a67594332366448507545516e526449566a51457377756a53453475610a4e6d7a307265495564673943414548487037356d444f395957584a576954426c5a4f357a486d7438364f4b506346486d43622b6a52743174475a796a2f7058446769576e536c5557434e4e590a2f4e6f4347707a536b314b6131323733726855526e476944414d4939783733614d767a426d744a334f78436d49752b323551364e71796e31636b436f64366e764f773731636d5a443532482f0a65622f724c646e394a594f572f4a6338566b31643656677774486133547733376371722b784b4d74725859385637792b656642474b78727a6e5a663761366a5749724d6f334c5053642f612b0a3349644476764d57395a62634a41696a4a755952386c686c453277536e6f5a57646862474d6d465046686565665a3147625833654b726e62574364424c4e42454779785237552f6e783665770a75792f5464345375664373434c484e4c6e6f59416f626c6770417452645650705541413048757373374a48702b6979444a576a504a775074706945417a4368387a445643614c5171314967360a7544725851344a506a756655386d6c33627571522f4c6250516c6b517a436e3056774772506c676a4f554d723945544f6a544934324d505a706b39325a5a2f4f384e76503232786f49366d650a576f77464e49776f3270387a6c426a2b7a3476355074716450397a546d662f34534e6f715a4a664c786f5270612f676c7472574878334e3151396d56477741306b48307061743630747651390a6a4141593434614a3531753250616b616159656c366655584d364f4c422f5a6b735954526b5a75546a376857535372434a4f6a69546a5359594e4d4b414d626a4758577732356258466736440a41476a652b486537725a4c6965665834306d376a4c4c45307662794e44574451366a47696e526d646d3056707579476861616f48786f4d313052494c6e50346a41416a3239656358414f456f0a474e44716a646673624262424f784739575057325749625837575544344b444874422f4a65424b507047337231524f39392f64674e6470574a3457376c384e41734e2f547a4c4542694f454e0a4c3175756857424d545a6b5162524847564e7657636a58392b62416a6a4430656262583341444c77594e692b6d7147454d4d3272586739576c5931726b3447676e68585133462b49705156390a6e644471396464736479774c5a6f52694154575747366f4167465a314b6e5331467549416c6d365157574c646a755a7858706143746b7a464b4e764759506a5147734c526f34573344412b300a516231737531385a684e6f6d7231494b68454c6a4931532b61576b33446e6e7475587943394d4d682b386a4f4a4f4f624a42774c592b33586f476a657655594f2b42376e5937786761624d410a4d476236706d3442697a41717774495977654f307933666b5933645a6c4e4c46584e3833372b753030534b437a596d684c52746166576b313934334e5671354439724c4a2f68486b53515a740a7434686738364c6f692f363378755846573848504b495379486236736177484c534a656c61354f634d435a332b44626565422b73756a4553567643614b4a556e4e4637714f2b416438716d6d0a53466a4265524b68356b5a6f646e7a2f4773476a4c594e6f326b704144467238542b4d31684c44635a5a7963434b62344e654c44737656506b784b53386d6d445967486a594257544a53674e0a342f306b6e692b4575737259793951694361477033472b426656696a4c564a76535171684a655766767a3673326752577a30555277685742493134737152357a546d6e79496d5742456538620a614f664c634a4565307a7745466a4432584e4c6b68544338506744692f3259623779636a68436e42662b506778786f58653431304e476b4a3374654c525a68776e72436d42772f34745856700a56657a5679424845384c546749622b324b6b616368366c494d6e7073304b4831595a6e6844656342697a46685a4844732f423952313744326b766b61774141414141424a52553545726b4a670a67673d3d0a	f	f	\N	f	\N	\N	\N	\N	\N	\N	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	\N	2015-02-02 07:30:03.31094	\N	\N	1	Public user	t	1	\\x6956424f5277304b47676f414141414e535568455567414141494141414143414341594141414444506d484c4141415542306c45515652346e4f3164653277553152662b5a6d5a6674646a790a744251524b4a52484642416f6f6b44684a776252494448386f61415266424242564f4966496b595449324a435969516145395349714e4545453457676d4e69536b4b41743872414b6b59656d0a764b78464b525961586758716448646e7a752b50636d3776766d5a6e482b334f37765a4c4a75334f7a747939393537766e6e764f75532b46694167397946756f6d633541447a4b4c48674c6b0a4f586f496b4f666f495543656f34634165513558706a50516e54424e45365a70516e5a38544e4f4d2b7179716472514e52564767717172346e47745163746b4e444161444d4177445241524e0a302b423275314e4b4b784149774f5679705a534f3035427a424341694961685972626131745255584c313745356375586f65733664463248332b3948494243417171727765723234386359620a4d574441414a53556c4d44723955616b455177476f576b614645587036694a314b584b4741455145777a4467636f5832616a2f3939425071367571776239382b314e66586f36576c425a63750a58554977474c5356626d46684955704c537a467030695138384d41446d4474334c76723337792b2b4e30307a7537734879674545673847517a77634f484b4248486e6d45414e69365646556c0a6c3874466272656258433458716170712b58786c5a535874327255723544634e772b6a4f4971634e575532413845722f37727676614d434141524543592b4636504235797539336b6472744a0a303753515331455563636e332b54325078784f523771424267326a763372336939774f42514864585163724957674c4972623678735a48476a426b54496877576f4b717163567430497071430a53534866662f7a7878305665544e504d5248556b6a61776c4147504e6d6a5643454e7836307946734f35664c35524c2f392b2f666e3571616d6f676f753069516455596745554652464241520a5a7332616864726157674341312b7446653374375276496b2f335a445177504b797370455070324f72435841394f6e547358667658726a646268694745544f67303133772b587a51645230410a304e6257686f4b4341686947415533544d707176654d67362f34566256564e544534414f516d52612b414367367a703850683841594e713061514141546450673950615664515267394f37640a477744535573474b6f71524658657536446f2f4867344d4844324c446867307070396364794c6f756744467533446a382f7676763044514e686d456b6e5937483477454142414942654c31650a6d4b594a76392b666448707966724b6861724e574136514469714c41372f6644372f6544694552494f4a562b5779626a7439392b437743326f34365a5146345467496851586c364f7a7a2f2f0a484c5731745669336268314b536b705330696741784744527035392b4367444f44685633762b655a486f77644f315945664a43672f3836426e48486a786b564e2b332f2f2b3538492f4353610a7476786555564752534e4f706f57494855374e726f4b7171364a7533626473476f4d4e744377514343415143414943616d686f4179512f307346665332746f616363397079447343414a31390a38764468777746302b504275747a746b6e4a2b2f533957505033763262457276647a58796a674232336231783438616c356663344f45514f39516a796a6742326365544945514370713236650a544f4a55416d54746e454257313236334f36462b6d714e7a305151624441626863726c5155314f44686f594741456a4b493142565661512f634f424141496959714f49555a473067714b536b0a424f664f6e557370445a3436786f4948674d6247527053566c514549465751696b4e2f6a366e58717a43466e30744947786f3464693333373971466676333477444d4e5733303545554655560a37653374754872314b76782b503177756c78442b377432374d5750474450463873757166387a4a68776f534965343544356a78515a2b47313131364c384f4f5476546a4f384d777a7a7843520a7332634b5a6130475342626871766a496b534f594d32634f6d7075624153446c7351554149703677644f6e536c4e4c70446a6976552b704342494e4249667a47786b5973574c4141343865500a52334e7a733144527151716634776161707147696f674b416377314149497474674552686d715951784c5050506f755050767049664f667865464961415979473939392f582f79754534302f0a52745a3641636e67304b4644755066656539485330674b6749774959434152536276554d6e685530614e43676b416b726a6a55416b556464774b5a4e6d7a426877675330744c514979312f580a3962514a332b763169716a66726c3237414853306669634c483869544c6d444c6c693159764867784141692f503133514e4532346c6744773964646659385349455141635067783848546e620a42584277352f446877376a39397473426445514e32554a5042384a6e49762f7777772b594e577357414f6572666f627a4b5a6f455a494e767759494641446f4d7658514a6e316361732f446e0a7a70324c5335637543654544446737386843456e4363434333724e6e443434644f785a794c78576f7169716d6f5163434151775a4d6752373975784256565556696f754c4854766d623457630a4a41443376643938387732416a746166616b2f6e63726c676d715967307672313633487131436b78425a79586c6d636273692f484e7343434f487a34634d6a6e564e4a69772f4856563138460a4557484669685869766d6d6157627470524d353541624c726c61714c7079694b554f7454706b7842645855312b765872462f4a62546f37793255464f616f423047474479334d4656713161680a7271354f434a2f765a36504b443066326c36434c77454a65736d514a336e373762514364686d5332575068326b426345534e51416c4e663066664c4a4a77413635765a6c617a397668657a750a774f4b415662544834306c6f306f6a4834304662577876757575737559516677777339635130345467416439726c79356b7442376250476650333865514f6536775678457a6847414e3439510a4641557a5a3837457558506e55463565486a4863473631625941336863726e51324e69494f58506d41456839625943546b624e6a4154327768357a5441444a346131675a334d726c585551560a5259476d61634b6e6c39323858484431724a445447694461694679386256766b37374e6c52433856354451425a4553626d6c566658342f6d356d5955464253676f7149694a393238754f69750a3663644f7759454442326a79354d6c5270334e506d6a534a2f7672727230786e7356755238775351392b7862766e7835684e415652596d34563156566c63456364792f7970677434364b47480a7348587256674349756257635046324d392f764c68713365556b464f45794151434d4474646d506e7a70325950587332674d343451537a774650476851346569736247786d334b614f6551300a41526a446867334471564f6e624d304a6c426432486a7030434f50486a786445796b586b724a504c71747730545a77366455723848772b7974384264526a5a4f39624b4c6e4355416f3632740a4c654633754d2f667633392f7572506a4f4f513841516f4c43354e2b5639376b4b56655273775467734b36694b474b586a6b5444756d50476a456c37767079476e43554130446d44352b57580a58773735625065392b66506e64306d2b6e49536339674a496975587a3333677267666e376f714969584c35384759447a562f696d6774777331585849417a6d385149533368584737336441300a54567938615453546733634a6f2b7662797551716372646b595267316168522b2f665658414a3248514271474953345766476c704b5a71616d6a426b79424141755455424e427279686741410a4d486e795a42415256713161685435392b6b4252464b454e4b696f7173476e544a707735637761444267334b6446613744546c744134534477736233592f587475647a6e68794d2f536e6b640a504d4f58316230735a4e4d30785772666642452b6b47636151495a706d676747672b4b346d4778663470557338705941506568412f756936486b524644774879484430457948506b684f55540a3774354667393231675a7965717171577a784d52444d4d517a325672774369726a45444f7172774a68464e634e70343049684d6847306a686a4e714c4158625665427357626d6d384e78384c0a333836342f66486a78334878346b57787a772b6e7978666649794b6350486c53444152467978505173662f51756e58727848334f442b64526a6a6c772f68324a3770702b48412b47595a44660a3779652f33302b36726c736577643753306b4a627432366c78597358457744617347474453434d636e4d36534a55735332764c39304b46445245515544415a4430754f7433793963754343650a4c5338767030574c4674486d7a5a7670776f554c4d66504e5a6650372f59375a516a356a4241674541714a4332747662597a35332f767835327235394f373330306b74307a7a3333694c33340a2b587275756566457339464949393937346f6b6e62416d2f6f6148424d7538794b614b644c64437256792b614e32386576666e6d6d37522f2f3337792b2f30783630445864644a315057506e0a436e594c41557a5446433163312f57593747397261364f36756a7236384d4d506165484368654a7779466758483868415a4830776f2f7864525557464f42524355525253464956634c7064490a73377136326c615a6d41536e54353857377859554645544e5a304642416332634f5a4e57726c784a323764767036616d707168706371506f546733524a51526767516343416375432f5033330a3337527834305a3636716d6e6150546f305247746d792b58793055464251586b395872464d3557566c5349644f3631487a7366516f554d46436551572f4d45484879526354694b6937372f2f0a50755330455a664c525436666a33772b583953565277426f384f44424e482f2b664872767666666f2b50486a6c766b4f42414b575857497153496b41706d6d53615a6f55434154494d4979340a677169727136505858332b645a73326152583337396f335a7375554b644c76646f684c3562326c7061564c355a56557374397243776b49435141382b2b4b42344c686c317648627432716a4c0a7a54524e49342f48517a36666a7a77655430784346425556306431333330317231717752396b6330634d4d7944494f437757444b7845694941484b726a6c644a5a3836636f665872313950440a447a394d4a53556c63632f5934557654744b6956784763453333444444634a6d534652515449422f2f766b6e516d3076574c4341694d6a53486f6d48527839394e4353763053354655556a540a4e46466571336f5a4d5749454c562b2b6e4c5a743232623575384667304c5a63776d464a414e6c516932584938484d314e545730657656716d6a3137746d57684e45306a54644f452b72567a0a514a4e635564782f4a744e4b6456306e49714c71366d71526e7466724a51413063654a45385679696163744734665470307950796248584a39634231452b765a73724979577270304b5833350a355a643039757a5a6d506d525a5261764c416c334157796f7666504f4f2f54595934395261576d7070624339586d39534a33784849304466766e314443706b6f6d414373726a6c2f414f69570a573234527a3656696b624f6e346650355569717a72426c6a645273464251553062393438577274324c64585731744b31613963537a71386c41557a54704b4e486a394b574c56746f78596f560a4e485871564574446a6676745641567552594a313639595255654a433475364c69476a2b2f506b45674477656a2f4141696f714b7850654a5775424d786a3137396f53515035336c563157560a33473633734356697961437973704a65665046467171717143746e72494a6174454545412b63482b2f6676487a4a44583678575a69645676702f50695169754b45694a55753543464f6e4c6b0a534646687367764933557369326b57757238724b536c453358566b586245657763576d6c6254684f456f73416c714667336c2f50362f584337586244352f5042342f4641307a5330743764440a313358342f58367832564a5877752f33697830384e327a5941434335574c746847474c2f514141682b6235323752714178426144386f6255662f7a7842336276336933793270576736774e520a6672386675713544313356786949585035784e2f4165436d6d3234533738524b4c43616a37377676507448586f41735a626666696273446e38396c756f5178753155314e5453457155395a630a502f2f386338697a6957444b6c436b686d697254462b646a392b37645242533757375055414b576c70646273365762776b693164313146645851304174672b41346c624e70344c4c473058770a664d41544a30346b6c422f2b376271364f767a79797938686563776b4e453054576d6a6b794a4541596d753143414c49652b5150487a3638712f4b594e486a703976505050772f412f716d630a50484c494b345463626a644d30775152696330666d42783277622b39634f46436b54636e4e4261756f313639656f6b7549465939526455415441423564617854787261357a3231736245524e0a54513041684a7a634651306b4c652b71723638484546315954414358797856586b504b35524c77425262724f494577565441413771357374753444526f306344734b396d75777463774f584c0a6c774f41725932632b52306d674378672f702f33424c4a4464745961547a2f394e41446e544577424f73737a6174516f38546c576d53787a58565255424344303047556e67417434374e67780a73596a5471752b562b372f6a78343948334f502f2f2f7a7a7a366a7668494e50434b327171734c526f3063547a583658517537434a303663434142692f554e55524c4d4d32574a736132754c0a734d43646372482f506d2f65764c67574f73634c444d4f495768372b332b3132523777544b7930696f68456a526a6a4b38676367687267423049382f2f6b68456e5248516149684b414c6d510a67776350646c7768777756343473514a793449796f5a75626d3855376371524f546f766a2b72454977494e4656565656495a5765366671495671353439574b4c414479346b59375964726f760a31674a4c6c69794a57554335504876333768587668512f5a3875666d35756159424a4476545a77346b51446e78456a437964793764322b52563676516474534f58666152687730624273435a0a5736577858664c5a5a352b4a714757304b427a6e6e666348434c667954644d55526949626774484b792b3955565658687439392b41394270447a6746334e667a41646141746173636b7744730a3074783232323041344d6974302f312b76396a5a34393133337755512f5a525146753642417764697073566b596c6377334f676c4970484f43792b3845504f334d67334f7a34775a4d7744450a6435466a6d765a4d674d474442774e775468776748467a674e393534492b597a6e506536756a6f416b6132627044684255314e54314454346e5a303764364b686f514771716e5a357a4439520a714b6f71354d596e7073636a61467a666a676e676c4342484f414b42674642787241566b7942584155554372736e42514a787a632b70393838736d517a3034444535566a4148456262697a6a0a674333482b7672367142616d6b79343558777765314a4948742f695a614c4f51324d69644d32644f524632775a3742743237614d6c395675505679396570574934673973786451417a5043420a4177634b3965696b594a414d755556763372775a5147664c352b384f486a77494948374c5058506d6a506966302b4233466931615a43754e5449486c553168594b485a496a5a665875424c740a336273332b766274433843356467434143414d746e4c5273745150524c58776d697477464b496f692b766d7676766f4b5636396544586e57616542796a52303746674445346c5572785078570a667246506e7a377079462b58676f56793975785a374e69784130436f42527a764b486d7550506d5153634d77684a65786375564b414d35742f544c7576504e4f415062476343774a775048310a73724b794e475774613845444e4d75574c5150514d55675537674845306d4b79736367567836332f3434382f466c3244452b4d6844506d6f653975774d6844596746693262426b427a6773480a68313979644b2b32747061494f714e332f667231493842365449506644313862794f38367666783838556f6a4f7a4f624c4473495a7051387138544a6467424a6b7a766565757374414a30710a6e3838427475712f325a3038666671307550664646312f672f506e7a496661414579463362527746744e4e6432544c726564745570784d4136435474397533627864692f4c4641724663356c0a3479466d41486a6c6c56634177504648786e44656934754c452f4c6162424741703459357566396a474959685a735375587230614148447935456b41397230596e6a4f7763654e474e4463330a4f3737314135334335763766727164695351424f6c4f65565a517659694e75795a517341344e392f2f775667662f34674733787354447139396375342f2f3737416344324749556c41626a460a6342636733334d79677347676d4361325938634f4d6473336e67626a53764e345045494c754677757837642b6f4c4e735536644f4257412f61476535535a533861584a7863544661573174740a4862336d4247696142734d776845456b542f654b39383777346350683958705258313876376a6b5a386c463356363563516139657665776665426e505457425859744b6b535248783570374c0a475a66565745684b6271434d43524d6d32483355555a42334530766b6e577a61504a7062756a774a784335736c354c6a79396d475a447758307a537a77754d4a42346541416675326d75326d0a77664d43737246693867564d6745526b5a4a73413565586c414f7937467a336f4873677466647130615141536b31486372574c35344f5457316c595546786344434c55366535425a79424e340a2f2f7676502f6838766f546d62386256414a775172784c71676250417871724834784552304551516c7743794c386b2f6b4133426f487742792b654f4f2b3549366e3162476f44562f6330330a33357a556a2f53673638434e6b516d5169506f486242714234564f4e6e446f334d4e386772392f676451434a526930546b695176462b2b424d36437171686a345376616b38345149774b75450a656a77415a30443278704c746e684d69774b3233337072556a2f5367613842392f62426877304a633945526736326c4f6c494e42546838647978657758486a4b6e6e7a5064687032486f6f570a4338694736644735444e6b37343447365a49627045794a415330754c57485057673879444e544672356d547766313864534561737551676b4141414141456c46546b5375516d43430a	\N	\N	\\x6956424f5277304b47676f414141414e535568455567414141454141414142414341594141414371615848654141414947556c45515652346e4f3162533268545452542b37694f4e70646f690a4a42565861713361556c395552425446742f684152596f6756546457562b704769467273536865364539474643496f676943693445597362466145717362565675744743314b706f4d5570450a6a4c53357954332f4970374a6663794e72626b332b65582f50786953334476337a706b7a35357a353573784549534c43667868717551556f4e2f52534e6b5a4549434b5970766e627570716d0a515647557747565353754543524952734e67746448352b2b73396b735646554e564247424b3841305461687133744d2b662f364d70302b666f722b2f48304e445130676d6b30696c557441300a4462573174566977594146577231364e2b66506e653737445631434a304e3765546f7169454941786c31677346726863675376673473574c726f36465171474378616d6f6e703665774f514c0a5241476d6152495230625a7432327964316a52747a4b4f76716972707569352b50336a7777505a75762b423744434169456254344d78514b7754414d5631315656614771717644785443626a0a7171507275726a4f6f766f5a45774c6c41565656565144674f65325a706f6c4d4a694d2b5a63686b4d676946516743416666763246587a664838465865794b3769565a55564241416c2b6d720a7169712b392f6232556a6162705a6157466b3933344f6356525a473255777a4b6f67432b667554494562737745675535667a4d796d5977763867627141685556465142794d59434c727576430a704a3075456f6c45414b4167385347666155756756506a486a783841674a4752456474313976662b2f6e344175574234392b356466506e794255434f415871426c654e5845505264416462520a7533547045677a445147566c7061764f3850417739752f6644774334634f45434468382b4441426956704339632f4c6b7958364c577a6f6d4b454d366e616135632b64362b6a34634d6550670a77594e4552475159686d3879424b6f41777a416f6e5535544f70305733786b376475775945794779426c414f664e6c73316a635a413430425871752f71716f712f507a35453042753253767a0a655656566f576d614946445872312b48706d6e696e6d2f77545a566a784a7735637751316873656f57796b77414c707a35303567387052454157797962392b2b48646471384d43424134484c0a56704b4d454850333374356541485a2b4c384f795a63765132646d4a6d706f61322f4e426f4b513551535a4175713544307a526234587364485231342f50697836447752425a634d51596c7a0a676c3745434d69546e314f6e546748496b5356643177505043355a554155794e613270716b45366e5259493046416f686c5571687672342b4c3967343834642f6970496b52662f4e4b50752b0a4150502f63714573436b676d6b326873624953694b4968476f31415542646575585375484b4b567a415a4b6b79707a6f362b7644776f554c525141734255706d415578705435382b445141490a68384e514641574b6f6d444368416b4167454f484470564b484947537a5149386c77384e4451484962354d42656558303950546b6843725236414e6c694145744c53304163764d2b372f2b460a77324541514631646e6268584d67524f746e2f426d697563506e32366c50764834334569386e65392f7a75554c5346697a51664d6e446d5458727834555259352f696443355769554c4147510a555768314743514356344358676447766451447644484732783470734e7574374774774a583132414c436441544e4d556978382f6b45366e7857454a6d624c2b4645565a414245686b386d490a6f69674b564657467275756938366c5579765863783438665864632b6666706b65792b51357756416269584a655151416f6b33544e4975796b6a4572674563326e55344c66315555426271750a69774c6b736a663337392f4830614e486f53674b7a7034394b36357a76722b397656327751433531645857694d38774442676348786230544a3036677136744c794d4e74736c56595a5275580a5172796d6830776d51345a68304f6a6f614d4530394f7658722b6e6375584f3063654e4771717973744d33727131617473745731636f47745737654b65745856315a377676334c6c696f73760a524b4e52327274334c3932366459752b6666766d2b657a6f3643675a686c46774839476d414e4d3043354b515a444a4a74322f66707261324e6b38797732587a357333536a6c7556795857370a7537754a794a734164585230534c5046584652567062567231394c35382b647059474441553337444d4679377967574a5544776570354d6e54394c537055734c64745a3676495776795470730a375751696b52423172313639576c414252455331746257694c553354584f303553314e54453856694d65727136697255785a77433245536550587447363961746f30676b5572437a345843590a4e453254626d58787463374f546d6d6e2b50664e6d7a66464d38654f485374593939577256353779714b6f714642494f687a3372545a6b7968545a74326b54763337386e6f727856777472510a6d544e6e5843396e5458743132466c344b32765370456c536a584e627834386646382f73337232626948492b4b304e4451384e764e314f383548624b7a4a53624239326d674f66506e784d410a436f6644592b72733734724d742f6e372b7658725262336d356d59697372734c31337635386d5852636c6a3346786b32432b434776332f2f586e526a317047614e5775576445534a386a37740a74425a6e6b4b717672782f5836426453774d534a452b554b73446271394f56697937743337385349797471526a597a54497630616b425572567267737a5a4d494662736877547339652f62730a415a416a4c76534c6f4641426f6b4a45676c5474334c6e543971356973587a356367434f55325a4f30357778593062524a676548426156534b53496947686b5a49534b69377535756c32392b0a2f667256566963656a2f73792b745a32486a35384b4b7a525a51464d623632374d3858414e4530786b6d3174625144795668575078774641374173432b567768703863346465624836444f310a626d3575426d412f582b427967636247787149625a4c4370336268784130422b61347756414f53564d6a67344b4b343965664945487a35384141447043645078774e725a36757071573574410a435254415668434c786354317672342b635a2f783573306238643150332b664f547030363158554e514434477346383865765449355a2f46464e6b68527a344e726d6d614f4144563274704b0a524554333774337a7a66646869575862743239337a51445357574432374e6b412f45744e57374d396c79396642704366426178722b5551694151426f62573046414e2b5348757743533559730a4153424a7662456d5a4b73307637674157314d6b456e47396e2b397432624b46686f654866523139613976386e77506e656b4d6f494567795a43323764753253756b684451774d745772516f0a4d50666a41586136674851357a4454564c30484b5651717441615178674b4d797a7752426e4d33786569662f65534b4974717a6378736c77705171594e6d3261744c49664b50546e43562f2f0a434947382f4973584c7761517979773759564d41522b5235382b62354b6b69357750315a7558496c414c6e315357327571616e4a396f4b2f46547a6c72566d7a787275534e534477464445770a4d46443241465a736b52457757586262746a50454a7a4b74354556326676397641422f43316a544e39712b7a676b4751627959534355536a556648513334774e477a5941794132754c4b6a2f0a417837466f56333863426f724141414141456c46546b5375516d43430a	\N	f	\N	4	always	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N	\N	\N	open	\N	\N	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
5	Template User	1	\N	\N	2015-02-02 07:31:07.816109	0	\\x6956424f5277304b47676f414141414e5355684555674141414c51414141433043414941414143797235466c4141424138556c45515652346e4f32396161386b5237496c64737a634979496a0a4d2b396178536f57393262766f7764497750775a516639326f4d385342674945444a3765362b6c6d4e386b6d693758634e5a63494e394d484d2f4f49573252317378633238784c58756478630a59737677453759634d7a656a2f2b4e2f2f32393447412f6a7577622f324266774d4135335049446a596278315049446a596278315049446a596278315049446a596278315049446a596278310a5049446a596278315049446a596278315049446a596278315049446a596278315049446a596278315049446a596278315049446a596278315049446a596278315049446a596278315049446a0a596278315049446a596278315049446a596278315049446a596278315049446a596278315049446a596278315049446a596278315049446a5962783135422f374176353167356d61687071470a32355a796739785330314462556d49464b5356694172474369416d4a4535524c6b624667334f7377594c2f543755373257396c755a526a6b782f34312f3472786b7755484d7a456a5a574c570a6e446b33314c626339326d35544b736c3932767546747a3376467879307971787041784b6c4230696c464b43386e346e773136334739336536765656756277736c78666a31645634637a50750a6431494b53744653494b492f39732f3951635a504668794c425a2b65356650482b66516352386570582b53327a573258466c31614c484c62706a5a7a7a70776179706c7a6b346a41424a44740a7253706152457552556e5163644c38667431765a624d6274647478737838313266334d7472312f6836792f474639384d6d30333563582f73447a522b5575424969666f6c723161304f754b540a6f2f62526b2b3664702b336a783378306c4a733235355153633834705a38364a6d5a69494647446d6e424d524b4a352f426359796c694b71554656524c61575555595a5353704653796a434f0a3235322b2f4b5a3838576a33315a2f334678663771347479665358377665685053496a38464d42423550382f4f633376663744343847663839466b2b57692b5779385636326132575464646d0a5969596f454c4968706c41556749376a6944757a53676f6c4967424d6c496879796d69566646395659442b553839506876666632313966626c363932662f7a39376e662f4d627a385a7468730a6969702b476844354b59436a61666a6b4e4c3337506a3939316a393932722f33586e39366b70736d4e303175636d3579596d594171717171674970437a556f674e646d67596c395674524b490a73382b49564545414d5542457a417830445a6978364e4c4a6366764f34334a2b746e2f6e79656272727a646666626e373876507836724c38425042787638475245766f2b6e35376e397a39730a662f322f744d2b6539636572316447365833514e41454368554b4355346944512b68656f4146434967794e6b4136436761662b595a724c2f694968414943627132737a55306f714f6a73616e0a37336176586e61662f65466d3065322b2b4878336654587539317275737a567976384678664e7238366a664c397a356f6e7a7874333375324f6c70336264506b6c4144312b56595631774d490a544768397075754c69676d59346145364352574e3752542b683042454145484254496d4643415173463233334a432f37397678383838665062762f6e3732342f2b2f3177665857506e6437370a4367356d6e4a7a794a352b32762f6e4e36746e3769364f6a356e6a6474323144436c5574785253467a704267416b4142554d67436d6f5143694b4271376f717143776a4d594b5278444956430a2f51394549574c5877387a634e766e30684c73754c56647075553574642f756e7a336176587052374b6a2f754a5469597356727a4c3337642f6671332f5563663961656e792b57795a5749560a465a6b7045427456677844496c4158426251674b4c4a697743467531496f614a46414352694c694a576a6632342b676f7167434a4d6b6c6949754c6c6f6d3265705057794f54726d395248390a762f2f5039754c5676625253377955345473376f6b352b33762f37742b704e503175646e793635746d56685652435a51614455753654754f594c42416c5351684d56523978336f556c7838450a55747544516a6e42524a5039456167515369466d79536d6c784b74312b39454836795a7a32394b2f2f342f3946333863394c36683435364267786d4c6e6a2f387350767466316c2b38736e520a6f306672766d314256455168716c42526330456e5a324f4f44585672456c5456524d67566b775656303942646934524149564230676c3031513151424f7a2b4a6b416f3445544f74567433370a37315058512f5636324f6d726c2b4e2b66352f7763632f413066663838632f36582f353639636e487137505439614a70414657704a714e506d382b3165787a4139486b4d497131627a7430510a514d534d6a32716c4b694478586c5642446a45466d416971536843464d7248354e714d4967356a42524531757a6b3557762f6b746374622f2f6e2f4a38362f756b2f56786e384242684b506a0a2f4d6d6e375563663934386572525a644a694a786d6d4b2b31643239767365527130666956676e4e35597257462f45755875504f575530426d615970525557556d516e554e766e73765033340a5a3476587230544b3774564c6b58766977647762634242543339506a4a2f6e446a3774486a37742b3052456746764b794f61477748655a376b5a7349526e6471625061472b72645a313773660a78417654516e55506d726e4745696574766778556c596845705969534b424d52714775627339506c4c3338316a715863336f7a62376631673265384e4f464c53397a374d762f7a313474326e0a523065726e67675472526c7a583866304e6a77554e7959716671676146584d564244637069435a7a7767775642696d35617a772f4f71413050377435515572714a784256676a4a52337a66760a50466c63584f6733582b2b2f2b57712f326477443658452f6b6e3249304858702f512f626a7a395a6e42777632715a526d587572746c484d2f52754b686235447464446462777763346264530a2f55617278324f654d4d336746582b6f676967384843504f41424255565971494b6e4c693561703938725437364f4e38644a4c2b385876794c786a334178784e5136646e2b636b3779354f540a6e684d724a4a54376841397972384c6631412b642f395a34437767676f53387745786d71616b53474b4353494c6d637a35685a4a754c4571726f77386543764f745a764163473457454656520a55576a4f366551736666774c506e31457a4e2f4846767152782f3041782f71595076676f762f7530503172336d526c562f564e3973696b2b6f4e6d4d452b354b6774694559724f4b707467330a754647612b7976315548484f4b6b4b43532f564459684932464564546d496374537143325353636e7a5a4d6e7a646d6a6c504f68342b4d6567494d495a342f534a37396f7a6839332f614b4e0a5a3234532b42555a2f736d626b306f306d7a32613446445630475252326d434b6731414e744655773350467845667144434655597a45354831626f784e5a69593239773866716439396c37620a646f642b38772f392b6f69514d7830664e552f6557537757475657375438344468646b494142483677505173783348734936327a7248586a476c494c34723361444b696743444a4634556f690a43444f6e3374364d2b556649546c5645693067705255554961444b665036616e373276582f644133377838646877344f54725261382b6c5a63337a534e7a6e687273767044756f7343324e6d0a526f536343433051384c687a2f44645a6b666c586f58543044542f3337696e316a5a336d364841334770453049677077346e374a4a3265385848484f62313750515931444230664f4f48386e0a6e542f75567374463279534b42433238365a574571554245784a4d476d55794d6d6130773030687a67384866384753527841343675536b4572696541457367796d577332576f5766656d54470a4e71434938536f7a637562466f6a6b396135624c67335a624468306358636650336b2f76504d6c646b356770776c30417a425677686549502b49774c7278437954633273384533554a3139720a7147302b5a7546546e626d6f6f54356d4369324754484558432f2f4a524a4e46356743434f794f69784c7a6f30754f6e66487a3249446e2b67644575364d6e54357677384e7a6c4e4c4f63620a346668344d334e724a2b396a516f3368492b794a38484872506e627761744d6749713754435856756f6341455374306c5646546466334a356458344b343854616c68342f34644d7a34674f650a67634e6c534f31574c39713058725a4e7a6962724654725a4639564a306671577767754e49416c4e555452316d5446783552513836557a6f4f4c4f42554366736b4649466949324e6a31546c0a6b4663565a4551455a716861486c6c69557256496e706f375938463945484b44395a45755630524d65464e3248636f34594e77436255764c56657237746d334d54376d544d504f74394969670a71475966545154594a4361716c666c58686c62696a4762757177754c36636854656f6545424a6c664231584865374a4c41544252303143336f4c5939584d3179794f4367355a4b506a394e790a3265516d33624532706766326a6c3578637947792f6562346b53726f3738374554475863346550764a426c577652566d684f4f747572324b796e523568466a4e784b4636454c58516a4541450a554441684d626474577131537a676336437764365751434974462f6835497a3650726335667a746767706e6a6550667030786c3157592b477558615a7a33633941733167356f3573574359300a4f39646369557837575461362b79704b42484e517147374d74717242585273697045534c6e6f364f5539502b6737667168787148444134736a3342796a6b5758556b72666c723366457363360a6636577a567a55794d7638476b376e786867714934332f4867652b63596534584530413834325a4a71646f714d3376554c412f54553879385771626a553236374139557268327551676e46300a7847666e4b5463554356632b7665364571434a534f2b637a344d6c6172417169366e59596b6170687a393578556c46315476305363516f2f666c33335642305a76774371414b4e514e45526d0a683034736d4961503631634949714c45616245734a2b66612f756d487670562f357a6863634353697675642b6d564c36447148684c78517a4265474f6f726d736466304a744e6f664f6e64330a67636e542b64596752346a656752306d4b3461712f614b776c4d474a524b2f6b6d6c32572b6c6f70383433734c544778736e517472592b3162663668472f58446a634d465232366f615364360a4139397458674468684c6f41555355476f65723679424372544e546b436f4e41346753334a59626133414952544d5863766c43416f455371796f51704c3933536a3830536e54457444464b430a4f457a4e793355726c38784145614b6b66612f355547324f417755484d37554e74356b5370386a4c3075416c5842545557512b50776e55454a495246344d5532512f69306b7a6967325837470a5a4d5372344d463831322f35535655474b51435a61523041346b6d4154735347637a74525972612b526c51496d684a534371416432446851634b5345626b46746d314c69304170545345322f0a725242553735695467594a70526345623375397330796b55556833644f544a6d6b4b6f684633655a493079724e6270627635324a6b4b7065416870785242692b4f53584f5763667834424a4c0a447855636d5259397478326e784a5870316d424567646d535a7a4a7a5933495436764f507579553366494a4e353851587050354d2b3262567a36564a364a4178336a366a4c736963394a6f350a3155516b554543354c6f43434b73434a4c4e68537763766d2f795a694a6d4a71576d35614b59572b52657639794f4e4158646d6330532b3558615445544c4d6e5653314473417151756338610a6a364e4149344d76496d737a7079544349354f397158483045507a567a7069557a31316d4e7249555a3445597a43575a585a33455756586e323151565a49594845397147326f614a4467735a0a4f466a4a3054533058504f694e636c686b316d6442574a536a3750346f78746872356b565765572f485a446d6d7169366d4f5a6b56734a443631382f6d75327041614d714d2b6f52674442510a337552634442425558316438694e4f3162696b6c357262566467472b6f56494f43783848436f3663735637526f756645484b3648426f304a49476950694a4b3441526845714962463857306d0a6444496c7069575251625a58485247656246566f63397935587a7054556f45663932426e786f642f77677752727976485445516b356c675263614a7551643142526c674f464279706f65564b0a323436596134714f344f35554b36726241726a3071504d62634e4537742f78624b6d6a79556434594f743875784557596d6d3535324257393457684d546b743170475a454b6f78494653556c0a4277647a32326d376f4f2b36696839354843673463706246456b30444973616b4861617063543453774977416353496a4d6a506d6d6f55693868374f5a357770704947477a61757a536457490a744661743450716f497042496261474441723432307a5a444e574d41665750654c547a6e376a6d6a376442314f4d44456a674d464279666b5274786769386d76587563624b6c37764b4a435a0a69786c6631693943584878726e336b305471742b5561304b4a6f624a43667641704e706b7756612b7a66564d3962327448676778733837583953714d4b6d3362306e52426f4237534f4479340a416a43566e6753777463696849695a464d504d4d377643662f6872542f612f2f7a766c4c6e5461712b302f6261394256635962514370374a4e566b4833324a57376d782b4a774f6555424e530a4a79654b674d526f576d303778594f333876324853715764614435586d4c4758524b54713631704a4936726d616b55774337664d4e4a4262724a5a71495343384758304a6479544f4e3563760a34595771496f694f7571316c6564575471464e776b3059537351497a5544587a3146343372545374504b6956377a587343527446664c706e566d61596a307271546f4c6a496178547265716e0a43672b506864722b642f5552416a56566f6d7331506d65754c4f37736f31703563544c717648377a357138494c6d51364268467032436a6d794241786132726b384f7a5277774d48786449780a4b56474743784d35727647615a704531594b4c563630793841594b4b6f657266684a31675341712f6877416c4d574f6a4b71787637574d2b4e544e4575635a5336493172736a68654e5841490a594359466b38696f7a7459776162614375507041676e32766b524c6c6154324871746945753231714e3337794a2b4c504e445078434663387a627a656b4478757331593833585666597274710a344e546b5150736a4e646836427a57545a7a797a4b2f77624561744a4e547370415a462b4c4c58557879474e67774d484565584d4b5539505568582b7378434b546837425a464b34677067650a774a6f485243436c47545a6d4f73542b56674e6a3976784f6e675656674652594f654d52715276563749477167717662584138564e436c71636f66764a576f6c55772f52577a6c416343426e0a79706d41596a71624746566d30315151636a36684d34694543314c7072786d70656c663975312b716b3949436f4f703547784d41554a645673786b77515a4a694a73466f656c6b50486863710a47756d6d616c4566396a635447426a456837644734524442306259705a7974386f7a4e464541526f6c4d527875754d4e4a534947706e426e496e6f43357a6e76324133417a496d64305258750a4b7330594c6143614c5834706d4752446545395667726d2f4d2b6b3141375a676f6b425549614b544d694e4e7153365a504a5278674f436774755863414b6a3332316438325071662b7343460a4e2b74756730763163475445467a50686a524a414d78756c6b716f67654b695569424561344b3443305341747444724f6c59777a333754433677366b5541316272784e48715056635a7659710a6b4a4c4c6c682f7533763674342f444177656736626a317a4c6a537a336663374b56365444413479597a494f5657494f35355a4b784c6f5165674e684658344c504b34554c465247424b30350a71664f53594e56314d714f47794a4b4b7079706b446c2f325457503144444552694e575570494b55457a554e705552336b66776a6a344d4442784d7446716e74356b726654502b4b433531340a377a6541456d77542f50476c697067376b564f342b544a7a64696f425a702f5737474167684e4d6b7335537166576e6730336f5a4e734c596d44365a4257724e59534776516563624d364e700a553834796a762f45652f6d506a6f4d44427847364258644e736e57706f6c56634b4a5368766f714d4b694d36506666784c6e6a4c796f66436a4d715a7a52452b5a30777a674e6b7a71314f6f0a544833746d6c6f567364416d5963476f7769766a307a79364532694c37643052746c334633735665357159544c547075477435754436694b3763467874737a5539336d78594a6f75626662630a7a516f70544639476b444f2b754573596141426f6d764670696964415443624d585345515a73616473345a73494f6873447a7641484b4e6d7162775a5a474771336f31313969456d367676550a4c513672584d66685351366d78594b37425963465347475078694941314c4370657a452b3057424d3254376b51665335416b49637131713039615156636554795a4162496d63597957324a6d0a7759414948686c30364d6e6459377459594b6a5476566243316868304973386e526336305771644664316a465351384f4845786f576e51643735544d416147713830304c434d68535a56436e0a47544146494b34736744412b644a726c61526751794e6a4a695939794a38516332566e30727671354e5175446e655a7979745a6355744d2b632b306b67706b346d57786d55525831666831320a354a526f7463714c2f6745636633456f684c6a6b724a79365a7361692b37335665626e71344b676d2f335232484c63714b3555355a7962757543643358314f31676d4f7a7555363569374d770a64413063784a4d5271394d42517852566b654e594d382b636d4c6c7055726651444d324e4870513365344467304e317769395363485332586934357238664a352f46744a79583155437331430a6c636d6366417737344f5454684479773757665244426442395647575769374d646a5a6d4e4c516333454832785067346f5a324143535930544a3977694c4877656d6179544a6d7079627a730a4f2b69774c5876692f5a76342b314848345946445a4c4f2f46566d742b704f32615478577053717a3236702b3879764a4f616b4f43594a637130734c4149686d6a545474636b6357565076550a725176376670624f37445a4c6543462b5453355a564145557155617641384c2b65497758304b687362416370596d746d744d31706e386442623063357250547a67774f4851496579463131300a585a4d535379782b4642553337337a6964524c574d2b4e52464778426a7771414b7549426f73715275447a53696561715a4164384e774a6979587956446172574b345055456c4731516c43640a313539716b666c70524d524b64396770444e5a75325543686d68497a59355374514a6d36636a4443342b444177554354553072653536592b64724669317432474b754731367668674b3653570a494f614a527a4e53306a465256397457363546636952426778525038673142486b61593132514d306459417a77394d56797179376a2f753045567178564256574b49716f3536656145774d690a45424d6e79686d4830793377344d424269564a6d5a724c3467346836395a7a7175774b49306c77327354715844716f7735544a62706c4146533155426c6535556e5670335157734f6b632b6f0a3175694a566c787052565238366474486b4f2b4f62464b584b5551525a4b7652576a7543784f4a384a757061367673386a754f427247343650484234564255695251713566326c66524f544e0a412f5179475a556178446c56786830754335774d6c66715945694956314a574661726973524479506271694950645a552b3037437279307950616241717949716444437a7a62702f46646f450a7351697157736d69576f704570425a64782b7431326d376c5148714e4868343453477354697972434a39364a5a6d68514b77555a6c716e48356d413978634d6544434566704c63664552466b0a455656794a697049566c63776f61626378435232775252554b735752644f62454242644c616d6e7a4767496d417344564536644b72464e59764d7a452b5942574e7830634f4b416f3670586e0a4d586d68557758534f3379333175794f59444b6b5273306d7532367953795a2f5a334b4f4a38544e496d6736425630417a2f4530573057436f70685a4f74564631636c4768544566716c72690a386e7839392b522b65346c39743153314643326a3673457759516348446c4755735a525377715a5864794368494a3435465a46774c68457934566d476e7a58794243686f30446c552f4455460a4132764855465656597033425976352f32344f6a2f717839487053357a4c656b30446c75787670314b74795349424c5255715259447965426b6f34697063682b4a3775646c6e496f364467340a634b696f6a43705251567a6a2b5252565a703034794741394b4c524e544c6d626d53494b417338692b68556963302b7a3068354f63395569744b4569356d6d2f633966476956454b617678620a56574c693957514d537941634345315469376b4c4642694b374c5a79494e596f446841636f696946696d415978707959694b756f566c474c497075454e2b515942316d6e63474c464c4e61660a616b54556c6851705238654443557a68684141516956424c5656354b7a4248745132566c7732344e4e39754d6d436c566d4b5a30647a74614743734b49534e5269473142767167416f4a797a0a436e61376f6f65436a634d444235544766626662384d33746e6f6d3672684778766c3071554a53617531304e566e2f737a51696453715941674a61434541385542563243506f2f516d7336650a2b4a725653564d50746c41305a756671744963357a515a644a70707944456a6a464644556d704d615a3564696e354371714259644268485276756d615645514f42686f4843413456326d2b610a3279753658472b6168746f32543379434b34635a4f56566e4c704c55672b594f2b394e4e6c6a7468464750667738617379674a564f7277524b744f614c38695431784f614a343549694177310a74656967696a4c66696262462b56485a456b503462686947515645366142485a2f6a44333965385a4277654f497253353463754c736a726148713062414167666370597841376a375369454a0a544f5137323469514154514842633149792b41346168714f6c5a426c65734f546448524d666b6e556b495371434c79734a51556161785a50594d654a564949537952686562474953636265620a6554634d6d3273647436767454526852687a454f44687853394f7053547135314b4c49667874312b614e76476b734942414b517142444b6259303464574d7a4e746f6b504a797745642b36340a694b6566347175774351496f5247465949437753637a6543335967444259632f30527975507143514b413041494c53496953736e346359692b32465578566a6f3154647965546d74764432450a63586a67454c32394758643762747432474f586d6470633435577839547171506f43435732704861316c52504642596a66424d694d6d7253474b6c35462f6b7144496a43586e41354a434c4b0a7957335969696359344b796154395346674d4e5341474c6e5769637178544a6759634a6a346c6f674971556f695062377374304f625a50624a7231364e567865446a2f7733663362787347420a5178584449496e6173354f2b364f376d6472767375397a6b6949725a34306a73795a75787a4f544e614f6773753866554f3038664f6c74564932556d58304935684c56706459594e654234420a7156617158596e5a506a6f4a7044435777366767372b555433583243466f5648626d6759783932776633782b6b72585a33467a7664346456697654677741464146544b79374e7539624554470a4970476446357068526e505830686f7a2f335047704772344937554f5134544f5a3446546e6334626c6d4b7369624b645a6f74694d4e6d66315335314e69776f4461336b66615369495a786c0a3933565533525566686e452f464b5a4d75746a767277374b56634668676750413759312b3965564933646a32673446445a4e5a69584d6b594a5359774f775263597173794d7a77324e68586a0a4d7461792b70767166716a627252594531696b3532446a73694b70553245587634496b366d316736353834742b4636587a69705178484d505378455255576778676b396b484d6674626e7a390a716c792f4b734e77574d6a4177594c6a366d723834764e686562593735534c463069556f2b414e45696942514638575431334b70484561452b47503632484746616673707956777236435a580a675761797053343467416d68364f4e5138387069793167772b6359464779354e53586d4c65315551424c4c623776353876623334686f626855466a7a4f6735753359714e7a615a382f64582b0a366d6f73705a525270416a716174566f677a575a47444e50775968556a626f763548364645354b3275524d5a6458756a7369494e33576558677664304259484a61516d58784c6368396d57350a3370423246704f6275646e426f6a463568456755596a73382f33722f2b656562417754486755714f595a444c692f336a39314c58707430776248653770736e5765635531676d58343151546a0a5742774152616e466653775677384468527157764d706e526f74567230577152514d3249564647782b533553525243496f415643436f2f31557a69387274795957614c336a6c6154574e53530a544147595a746d505932492b506c352b2b54397865544563546b696c6a674d4668797232653555786b2f4a7550323733512f5a65355a4f3561592b375678765569623249624335556f7747680a45565256703971563834434a6278362b6254566d762b504b777253646c46526c7a697278517336427a50685176776f4161724a6a76782f4b53437a39734338484b445a77734f434134574f620a623639533034364c626e776a746a5a4e6e6269754a314a6a48576b5747644670356963425436684a794c3777364d3357762b784d6953334d74534c4b7070564b67617046373271476a7863780a383675432b304c2b5963676f596f445952496a70712f3077626d2f547a55586562525634414d66664d6c5431386a57392b455a534e2f544c5649725938746e6f336c6f444738553437536b460a3248504a7054494c4d38594c456b52716d42516d6a46537347344d6c496f70447a77524a4b5a3650474e794a6e306d4b656d3237794532796230705162575a2b577154584f5468626d7941360a44724c5a376c362f7a4b2b2f366a593342366451624277794f4842394a532b6561332b795054726863537a4d50433174436c62425241417054596e43436f31386a735155316d4d46553153440a5a5a397768432b73716b6c4e5a6f5165754c4f48593650473945573868465067373034564d34527043394d7a704b566f314a75544d706239766c786534506e7a63624d35524c4742417766480a62696558562b50317a5861377a654d6f4f516d7a6c63706e6e2f37714931522f4d6d5a4f4b3236634b6b4e6b2f38374364375833556a565051304a45486f354d354471413046384938384b320a5a345a7073324b7353654a77543951746a4b67614346575143447a7374742f527a5655355146505578754743413041704f757777624e7068782f76646b4249314f63313830716f53334132700a56485a6c785551302b496f37477345724f7849714b526b564e4551526764595148387a56304b79382b465338574d526972724555553730586a4b71584568456a3843782f58555568753932770a335a627454627666306c686d51757241786b4744413443554e477857753175363375785335735373454761716132685658655654696943494f704771716c4c672f4a504856715a64794a644e0a595237504547633569586d6952545457475444544a4c47716636497761424a505a624a4674496751515a775974594c576f6970463548617a75376f63723135306d79754348735171684f38630a6877364f4d744c56613335315574616e6d32586639476a56534968356144534953364b6f6431486a487a526c427332574b3768344d56497430655332574d35684542325447364b687059694e0a48765549576b30484d546e45484c5a795342335455557751746b783549714c394d4635643731362b7a4e665836574446426736574961326a4646786434764c5665484f37486359536f74396e0a4e3078544e52636a436a424e4a4c5a6e2f774a426e675846486761416a636c4e74703131736b4941314a5046736961714b63614f3062716869795733623079564f5063616b436d71343444620a6a56356679573537574748594e386168537735563365336b2b6e613476746b4e34326a4757314a41332f5252546365546352593042656d63474a3170424468456f686f6c59305a69756174700a4e6d59703668795a69534a76506b68636d325462357061577a4a43697a6f7336525271392f6e7a6c6777366c444d4f34332f4a7732356268304a2f4d5137382b302f66444e6d2b75466a63330a73746e7553356d6178452b624f553035576171654978377a48614b67726c2f79662b325a4a6f50494c4c706d5233485070544b6f56504e5858656c5163436f65645348485a6352745543502b0a436d5647476366623239336c61373236614d664479757a356a6e486f344c417837747662792f586c61376d3633705378614b77566f2f417337596c6d6e7177456e2b6b6f3232516168786c4d0a76755357434f79646f4d674955496f3654416937684762484a494349612f4d6f443830376e4d4b4c7751512f635371574d485551777a435579387674797864362b53714e49333372687837570a4f485331596d4f3330597358744437644c4e6538374e75636b36322b5a36595579387051376341614c4964396f30347556484f6b666c4858526e73526a6b707a656e713634634874467657630a55675749496546437837796a46444f4c55584f4d6c5341717064676962686e4773743374583139737236353475326b503264717763542f414d593634755a4862613931737932342f3570787a0a54757946686165314375615857683139414a55776a55477a563047655737554775714e4e4d423268376a36523761707169367665494634444a454751526c4643455448545a37766458312f4c0a3155577a7655304853337a4e782f304142344378594e69332b3633653367354e546b32546d5a6b3445764b38394a6133426263314b5246616377646a6e6d4961355141425447436f524a6d6f0a4d7332386b46722f4b644c2b6f477055694d6b595737504737446e786c6f4a47374e617132616a6a5747357574316558324677636c7a334e4d5875773439364151347665584453766e7066630a334459744c5a65644346694a6d425171457254324c506e76446837636e7642534d485774737a333274575239354277444d494c5462564a6a7836517973474b7543325a346339765a67434c7a0a6f514c5633544263335778667638623178574b2f2b356663736e3934334239774b4e316355645071386d545937595a7847446d6c784d7a457a6f43356265304c352b48466e365a4642445a350a6954335a523264714a6b774a6f6d6c68696b2b3272613131435552566963512f4e504f51564975496942424252556f70466b395231574559627a664435635634645a6c7562365755517a64460a6264776a634743336b2b32577444526c784d3132364670746d3878437a47772b6950464f356d46534245686f7a6e4c4f6e46345844316f46527269345530584a576c75646945434a714336560a6e764a4c41315247716d6d7353694977737973647765316d66336d35753731596a7a64706c765638364f506567414f414b6f596433313474586938486f61757a6b33564f715253464b7163350a443070754739516b776c6e6d63505669614a6268463274584a684d32534e4870446457555a645436786e37476d71586853655642644267624e6f356c474d74756839764c646e4f624c4e357a0a4c385a39416765412f593566664a55454f36564e3337574c746f564173366161454134415543555437385254432f483443684672725652354a4f78414c546f797252384a696f73414d4968590a4932786a5373537a7655524b4d616f3057757a454d6f64784c4a767466686830324b57626139317544716a43776c386439344d4571324d6335657053793735647450312b4b4c66627262706a0a55734f707377797647676b684a75613665494335786c7731736a5743706f71797738786d73766a326c6b58696e684258346d304358707a547154436a57674464377665767236362f2b5670650a666431744e6e79506b4946374a7a6c557364764b667465555858754461395779574c515a6e7674546138464f5562597054755a3142742f7761524531676253656f645a2f733370513548475a0a514a7343726b47675551334570412b5478734972414b4936374d664e64746875792b75583763766e755178794c7a7a594f75345a4f47793865673469585a39767a682f6a614c316b554572630a3546794c616c446b6b55667568625531415479567a38764b45646c6135386c746b6168785067645174534d736961515564304b6b6c7176324653696d7445514145646e7468347572323931470a46766c597833787a6662675a5832386239784963743764434c33697836737377764878354e5236586f2f575357524a48627358456455616f4252507659535a6d7a665a416845305261526d590a64677566786f6a315766644774515965646272645548487873742b506d2b326769694c35396650323672574f3434456d6976364663532f426f597239546b6c4f744f7865583730456f3230620a4d7a435a794873386961414b6a484130516f76344e4e4a4d79346a61367633716c4a694d6f664136464650444c6c495153467a70454d4a5638595973556d537a325633663776752b313748350a30782f6b3163763768777a6355334141474166393667744a4f582f30792b4d69773475586c342f4f6a7167337778464d7242454d46664d396d56336b7a3163677964774b43576b6a554258790a3076664f583954564a2b457275324b4263575665796b744c6b584573752f33773675726d386d4c62636e2f314b743963372b526559755065676b4d4546362f483958485438756c496c3766620a6d38316d6c346a624e6a4d526b6a556f6a6d6f71354832396774567775544835446e6373444968343945354442366c4f4a7135465a5376665a566149485664557476763978645874626c64450a383875762b665533656f444c35372f6e754765753742746a63304f767675717948702b64724866373466703234796c36346d6b33376c66345042497a6d3130536378777572726f58375052560a6b47454d34716d686a6849704d55416166626a636e33577a564b53496248623756786458546536656e4c362f75556d765875304f7265724739782f3356584c59754c6b756e2f3168392b54640a31627450752f2f7848332b3476746b304f61396f67535972694d547441794b6732416f554d4e676a634c3555477644566b5934595679565354565771484367596f6c347458793252334d4f750a6f6f70537973583137576137507a30354772667235312f6d79347478484f38724d6e4466776248626c612b2f326f3737302f50547465706e567a6533626463715962566347502f4a784d52730a75587a4f5453554351614e686872564c7372684d4c51426d595635454646656a6c6967414336306c3567697a715968496b5745736d39332b363238753269622f396863662f2b452f2b66652f0a323978634831494c3462393933472b31416d415935506c582b7a392f55566239657446314c3139667648683963584f374b54495357645339714261612b412f42724451503473455067394f670a5556315538737231644b66776572516c643639354b484a356666766e35362b6576336864536e6e337961506c596e563763796874552f37756362386c427741522f654b4c7a657159567164740a333365584e7a6576583139446453797239584c524e7130436e75354a424e4a705052523547425567685166446a434d585553596f515151677864546b4b3961747555725349724c62445a66580a743963336d39336552686d3250413538333547426e77413441487a7a7a626239512f6e35416d33546445327a3365322f6556483251786c484f546d69796d53594335737a5142536c67734b420a646471624f4c454b784971734b306f70566b78684c464d74466f7641696d675233512f6a3963336d6d786358524c54752b36747573396d57333339322b654c46504e683358386539423463710a4e7076792b7058755269793674463731362b5743694972497864584e666a2b735673766c6f704d694e51356e73524c5045592f6f537952394146434b576c34564a5143494947494b526144590a442b50313758613732323933417a4574757162763276567941573275726f6562322f73506a5a38414f4143493647346e7736684c7076577158793636785054713476723664764e7175792b690a4b746f314f5a6e6a436e4269496c74613679556c58624a345659565149714b69696f4b674d78544157475159426857393365347572322b48595153773742664c5264746b58712f36557070530a704e786e4a36574f6e774934594e37454b457a55644f326961314c694531305234664a71382b4c567865754c36364e5676335952556f7a65794e5a6d73416752494d6c367544477a546d304e0a6e5035534a7a6d49534866622f6358563766584e7a5443576c4e4b696139756d73624266597534584335456d4a514c64543037303776694a67414f656570503652644e316a655672654f6a6b0a47727468334f3647556135764e747575795733547446327279446d7a7053616a6c43494b5155726d6a4569344d70375573782f475952784c47626537596263625370456d7032572f574336360a70736b4b4e446e6c6c415371776c3144545973486d2b4e5168674b6c4b444d742b36374e32594a716155324c4c712f582f63316d76396e73726d3575642f747832586672766c2b4b716b68700a6b6c757142564b6769705369386f4b717149374653736d576d3833322b6e5a7a75396b5355622f6f7a6b3650566f757561334e4b444543675864753054634d4d455378616442304f71536e390a337a6c2b4b7541516a4b5541325952384b634c4d5143626949677a6c526474306262505a376c5631507779336d7832736c58795455374a3648305477706b7846464b706a4b667468454f38680a52305134576936624a725674307a567453706b6f4e55314f6d56573161584b546d2f31517969677043374577302f306c7a6d3338464d4378584f5a48373144623767695555306f70415955490a496c53456d775a456c424974462b31324e2b7a327732613747386274666a2b6f61746f78703252356736614b4a484a4953796e444d4242526b3150587463752b577934574b53587a6a524e780a53696b3375576b544b6557636d4c6e4a575751556c654f542f4e3537797a392f74646e763772487863652f426b524a392b756e3630312b33497730327930325463704e45696f694d525468780a475a3370626870757538585230654b3872457552595267336d324563686149314f6b7a614d4c7377416256743672724d7a496b354a525a52674e716d615a75634d2b647369326659456b65610a4a6f326c6a4b4e3838736e78737966392f2f6e66767637393736392f37447630393439374351356d367675305871666c6d745a48394e48484f446b66727a6473533268545370596637726e420a6f414559522b54453047794c55707163694767736b6e685878734b4a72577139313753332f722f4569626c7055744d6b6937386b4e6e4367587a5335795579636b35334239744b6d79634e590a4e7276647374382f65724c347a62393136784f397674434c79334a35736239336e4f6d6867344e43345250446f75733530324c424a36664e75382b6170382f532b534d6f44384d344e6733330a665a65627a4d7769496d4b734f5175724d434d704e444e344641756d616d4c4b6e5071755164666b6e4d657869456a544a46556478684b4a487752514b57424377357854706b54453144594e0a4a315931526f324c4a513078745530756f31786a6533313777306c2f2b5a7638775566724c2f39552f766a5a397339667950564e4759667149574f4b36427a714f48527771474b78534d74310a57682f54796247324378454d75526e37705a366434765363562b744d6c496841784732543279616a726a5142334f526b4c694a6a47736455576f576f6942524c396b6d2b464a7341714843540a457767355a2b4f397043676e627071556d464e4b4f535669596b4a4b435a364961465843324a4c5532544a4763724a4759494c436a61354f64342f4854626365695a4b55764c6c4f6c3639780a645356586c3464593733772b4467346352476761626c70715775576b54594e2b7963636e366677385058724d713755494d67673570375a74466d327a574c524e546a6c78346d5431446b715a0a39553242456c464b6e424a7a3141685561436e696955436c4a674f52717162455249514d547a51664a656655744e6e327455776830794b713837585a594b61556d4d4264536f7446592f6d430a5978476d3866676b745974324c4c6c7073705a302f5a706666464e65764267754c6d69336851694e65397276644c2f58512f4e75446773637a4e533266484c615048704d35302b70586578540a4c6b326a7179574f3173313631533458755632305455374d316d79576d4f45704e7751704f6f3553796e535872616958462f464a7a45424b466a6752553167445269466c565474656a657a6e0a7a455255526b324a63303557747a51786d7a71594c5832413164484f6d524f727144427a6b314b5445396f324a516249556f46456444384d32393234587536507a7554524d37322b4668556d0a61563939773938384c3639656c4e7662556736704c4f6c4267475052702f57616a6f3652476d6b364f546d5252342b3778342b626672564d43546c786b335054704c624a625a7562484e52540a696257484b455845556a69742f7050582b7a4c7352426d46464f6e706f6d72466e4a6a4a444252345852376c434f4a614c72746d3243346a68477874744e5a69706c7172437745676f4c59370a4670466133634f775a513041632b616d7958336648492f643432486337306341347834767a38666a4d333378637478744d4f7a547a535664582b486d3573645046507078774f477a315341780a6d705a4f542f5054642f4f37483144626a7a6d5878614a5a7239716a56622f73462f326954596d6957516e6769734e57707671616f6c4a4b38576166674c6338494d7372542b78396770314e0a683066594b6a4b59794b6f5457735745624930476456705336517676705636353832575749575461704b5972477973366a6b57314b4a424c53716c714d314c5674736e396f725779446754610a442b504e375736353270366334656d746a4150325733372b42583331706278384b627574466b455a5665544849654e2f48484177302f46706676776b4c342f322f584a63722f5035655837380a614c46653574796b6c44686c7a7377704a624d4b6938673443694a7a55324d64514f3045486f6e6c414a545953334a5a6f6c2b55504765724d7a3274504249744b6c42454a694552716256520a4568466d426b474b576d6c5a67306b5a4258536e31435246685879544b3656346870694e777358636d5a51735477444d6e4a746b566f765a4e347575615a7030744f724849715849375759340a5074716450743565584f726d6c6d38763034766e6576483678326e4938693846523974787636546c69726f574a32667076666662302f4f6d573072667463746c742f4c4164315a413150385a0a796d697a56596f4158693361496d7246396370554f6746515834705578663230584f324e70577a7770516678435676564a714a357439706f43336c6e583471396b35556952453146523552650a7350783271436f5468465242724b514b466f6c363274516b583947646d387764453145703076644433366554733754647472737458377a554c3435324c312f71646b4f334e396a633648372f0a7230504a4477364f75694b6b362f6a7376486e76672f7a735138374e767533346e66507535485335584a697a3664754e70597a5732464672336e2b3062544e7769424168326577544b56434b0a4b445378723336337645364f7461756d534a6841544d6f4a436845744b68774c374f30696c574d6c4a586e54444b7349593941625251466b727341414145336d74766a32524a51346764574d0a55424578387454674a5645776678796a436f4f6d78454a4d724952434945704d6936355a644f335a4b55526b757873757a72636e352b58324672737466666b6e66506d3576483435374b4c390a37412b7461333577634f544d4a3266352f42474f7a374259344d6e54394f7a5a6f7576574f58472f364c7175615a766b647a4e4b6e34796a71436f78655546356b4b704b63545051467061550a6d73466c6552626861576a74676841556b7a3348346238514d6342414d664d42646156314c63737875534731476a7246366c75696b41666b795056665362437963563771504437457a4e6b460a76507570723667696c544b36443078454a456f3563354e6855717874737132313744736578724c6253372f59725939334e7a667034685666764b4458503779752b6148416b524c6c5447324c0a6f395038377250326f352b6c78303841364c4c76546f3658713337523547784777444157542f4333626e76716b6f4241556f723169645770376e6973504b76366758334a41596a454b314f540a7233554c644d516b415153725a55333273494e4568514441476d774255575a4261314558655031614143417944467564577647447a306f484b63424b6459576c683279456c5a6c595a70656b0a674a7159453173634534565131647039554e4d6d496c703037584b784b434c62336235743650774a686b46655064632f2f6b48627a2f65764c3351634d4137346763693048776f63783866350a7962763579587436637371724e62337a7a754c3070472b4d62637a5a3770536f46436c6a38637876446346413174746d746f536469536a373067437835556e4d626765514e6238785638454b0a5946426f42484e7a4651436e5741394c4249427a4d6a656b507553554f4c4543766c62427a41482f4373545a72736c636d53717877716374436f4935325044564d54445057536f507a35544a0a6937645970706b54626d54317278314a597845705870584d2f436b77694e43327a666e7030596d7378694c7235625a666268382f4731362b534b2b2f7a732b2f4c7139662f53436c73762f4a0a344f6a367446375479536d6650387276504d6e76663953736c74773061646e33793337525a472f53566b6f7855324973556b7178707a2f7151303731744242506b2b5041323334435556416c0a6a4d56775632713270346c62363255526866486868436d416b437656772f46753568524c33387a524a516d547862747377507455563966496c6c43714b4c46646b6b387a7a553542643871680a777057676f456f344f486c7665354f526241682f57307a72674a6f6d4c784b5849696c78312f485a6f2f543053666e36564662482b322b2b48712b7661484f4433543831512b4366417734690a4d4b50742b4e476a356f4f503879652f794d736c466c337a3648793158693259795a6f63444b4e376e30565556587a6d784f2b3346416d55794a7849397274476c4c79724e4c6e476a38614f0a4b756f393939784d63314b6b6c685773787848526c4f412b7169504a4a38596c56694c794f7567416f45584178455331774369736c6f643367434a5041716b466267324979526477687874460a476f567369536b6c55327277746277466e4379315855325a326f57566f7155674575584a4448525268714c766d6d5866535a47626b3933526576506f61586e314b6e2f314a2f3771633778340a4d657a3338732f6952663435344f6a372f4f7a393972305030714b58733866352f666458585a76624a765639312b546b76716a6f474f537750574469536f45773638706d684946565a684f420a31347163616d73675a5375353461636d4168496e587831744c5a683871717836457964624d5538616e697352705151765a5637676135373871366f795a745663434a79494e5a6b4130466d6a0a4f424d314b624e5869706f496549714b323148324962776845337577516944712f784652796c53567a6e775a6c6b525a5651736d513545534e3877353832725635637a726466506f664468610a627838394b6463582b63732f6c612b2b484738332f77534339523843427848365a566f75366667302f654c583761652f58424350625a4f506a2f712b73386a435246585a6d6c4b463167704d0a6667676653744e38317966584e414b6235716a666f374b656455304a6734694d396a4270584238646d70493579517147786130486c4d7a7253536e38336e6f35307956356e724c354941554b0a555976417a626166585a6f69476b6d5a6a43465659535a4f737834777763766f5a46686a6f6d62386b6c4b38784554364f6472594643557a7231654c767539327536467430354f6e773236440a31577048724a6576635875726d332b73654f452f424935756b54373965662f2b68397974686b655063487a6372767131735259417872464970506e6258524d76417579314c567a38466e56540a314a5969466f756e5765634b6d386d6f6d6346456b305a776537583671446d5a41314b5059355639794d4a796348464e6f6941335563326b4e542b54764b5653696e304464764e4c347569670a514c484978634f386c54693763306c496d6164516e7032432f4665375a77354153635459666a4450797558435352366a353430444e50456b417047426d464a4b326953414571667a6b2f56590a35505a32502f3673394d646c63396c2b385566357a2f2f596272642f66396e5476784d637131552b4f30395033387366664e512b655a705736385769363961726851554f537046786c4769780a4f396c39495774646935675546792b524d693073677774347547436c4b4f5a6e33334d386e5a4d3345326f454d4d3552555a55554d55466f766c363857694645385049634e4a6e42646b614f0a7137787a64444d786c4455754b5852526e4e314e444b712f6c59673871387a55336854664364465964566d3951657964534d6e5836476e63694f7251575955694142433757694c4b32624e510a6e72797a4f6a6c757236394b7678793758722f3673727836575735762f783474383765426777677055642b6e78302f61582f79712f666d763272616c7673756e703064743235435a616b576b0a714968594d4b784f465943702b315838316c442f73425771566254363973464a562f49534d396c7244314d4b4a61567865665974685a74497673374e697455722b2b5076592b5a2f616c67590a784e6b3156796c4352485562494e7873313048753161623458656145755873786e634b50356c692f63306c3333575937512b306e564945454369326a7466677552576c44496d586d5956526d0a616e49364f313658496d317a30792f3533666654372f35392f4d2f2f622f2f386132773366334d2b774e38734f5437346150482b682b335253586e794c702b644c6271323664716d61544a670a78557a45336371376c5137736e6c59443374334a38416d5a435178534e7756692f537055344b526c6c42745864304d41686e564a735a612b716c344258794a777a6b354b546c773450446b550a3176586550766465775035776173776977695a31537157324470336c39706b2b696b414d685375727144334d7032626d3032476e3039577975636d394662756b4f7a48592b536b3467634d770a496e5943563556557159677977624b674b536b6e57712f37726d763234376a3936435a312f4e3772355a382b477a37372f655a766d757676437734694c4a66703854764e7a332b352b5043540a746c2b5631624a644c62752b367a68784b61586d5669484d744c675863474b4b4946544676662f496f4444717a664b3767567165336e6d4479567a3168413358355743437147643832574d570a4a6736425a74647630525a474654536d63535972313645776d35524a36557a6278432b3638336c3947364858715a3570484c6d436a2b5933683042494e4a643963556b3632784832593079670a4a44625267344c77713155686c72776b31742b426d62733274303175687547644a2b4e797a5a747258697753564c393550747a65666c387239587542677768646c7a372b74502f662f6d752f0a506b612f6f504f7a6b2b576953796b5251615355556f7778344441474973595a69747849516e63694e424a7976654f464b7739547a4245474a624139496e42623171616677346c516e6c78610a302b55496e3449454b6b5772774a676d5136746b38717141695a337173412f543364416152542b4e364f5643695374527074617a4a3259625a6c32674a6874527653542f66555873563348640a33734264685150354b653563556c67734164686b654645695244644d553239785978554d736744516f6d766579636572667638363358612f796b2b66487633332f33767a752f2f59374862660a4378392f485278454f44374f6e2f356938656b7646302b664e563258466d327a576e59354a52564555537931796258713876575271694a556f2b4b304d635a474777616c4744756f317330510a36392f444e62446245574c46556147576f2b6461796c426b54377a5a7555524530576f385345347250576c5073656b76622f336e4e5559354c74736e62536f79365263496d7739526b4d41360a41735a536665396d4b6734382f33584265684370554f563246613449617a484d3253575a72515a586c2f357975686e5450664f72716e4c4a7a71336d3354436c6c484a4f793057724a3972330a3433496c76393172742b442f2f492f4e31635877562f4878563842683275545a2b38332f2b6c2f5854392f4e784879383770654c56714d4c4e377a43577677324159444555584276356c47450a4f41376232352f3259492f39575a355a544d616475695566596867565a4b78427274703131704f464d506468516638554c4333715a76592f5654554430547376576232664d466c43774d54760a7148774c4d5a47535447437934726965716c795644795a305745387049694b326445594c415571394c52456b43502b454761496d507a56344859704f324a50504e5a75737951656174724a620a6362526162764e65736633354c37756a34375335486634307973334e58354566667755634b644837482f46762f7932666e61646c33793057625a4f53366a534647714c5072792f454c7a744c0a415a6e454c31652f5979704550686d44524772794e5a724654785938415a6f6f75524b4f505779566d5a752f6c7634357a546a6c6d7177562f356a526a77682b6d6757434d463853637a7a750a45586c33454350306f50634244533943713565696e6b68476d646c7362344559777572575148673135734735316752524d67694a31304f65546b47557a4e71516347655a6943675a774658630a764a686b434372485a6d78507444636a4a714b756259686f5034776e5a2f7262663875433872742f6c3739633750417667534e6e4f6a314c483337636666537a667231712b713564644530520a71777a7673784c7a58522f634f306161577945684a796370555a2b47454c3931423376576157704b373366576e614377386d616f6d71704f4f7837645969414e45564668777242674c5554420a395a4c387175325231626877494a6f4f75777342547a44574f4436714a785862492b497970437a655258413652524434643262546f73734b416f5270346e5a444b314864472b545746674e450a564342514a3056304267367a36736a6f4f31565345436c44694478485a4c5563502f693475376a516c382f6c39617679462f44786c384452722f69444439706e7a315a6e4a36742b3065596d0a5764635a573369755537397656466c53785a7050687a38496b376c4541444635336133514f65725041547a7a4e68534a4231534a36724d3774306a734e6a45544d534268497a69644d5058670a6354443572437062642f4a6941734d74477961534b5348493574312f52484966797131554361576a4d33766b7a69585636342b3263392b2b70456c52325257794356554b664d64445268505a0a4f6a4f473345786d70316e384b613175382f79616e505a6c715735337a727a714f794a362b6935393849487339727572693764537148384a4849734f377a7a6a382f4e6d7357687a547455590a6e4473566b77696b435254317762413747716b5555796373647338734e4368357a63764a5735732f7a435a6833526f6735786e4435412b767875342b494b61754c597079527a3635512b46610a7050715a477053536c54753346704132782f5a6a61547064315a6f577a456b2b767959526778367a61534d6935666e3242442b4265705a5164597a7378635363465141676e72776d4f3055310a752b4b537949786177665468564737584e59744e6a6874726950565854636f6e702b6d645a2f7a35353768364f77442b456a69614473646e7646787a596f5a4778623237492b67697677637a0a3357786a4d692f44342f435a69675a5945455148786b71517a4978587846392f56685247764d354979376e65514f426b7569684c396b6d544351496759714b4b794f6b4c6b414555635a785a0a58396d4168584e78577265334e3162704e733132714439316369754d434c487a433553553632317946414a7a2b787845684f42374c6470636738665439766157373234506b463153376462740a74315274735138413945733650754f6d65334e43352b4d7667594d546477752f795558455a4a73486d645361624a4b4556725167354d796f6430345145305549745535596f5251394671386d0a786b6c456a51657a676e324175667554744c666766747757717533705654484c746242436f6e37376f6b574757546b714d7447586b2b674442435a79514b6b4b4b7968524a55756d6a4651460a5143717737702f4d6d42424e56496c5556653956363974506c3053654236304173586b56726a4b63385853732b34324e716945676a665579356c375a723535634e444f6b454571484972744d0a5046494e685a5a53435777513048555438662b3367774f616b767341436c5476432f5835435376615a344c415666797146667163656f665478497554303563687a4b6e4b697171684f417a750a32584e456f585243504d794d523264534a2b56566235504679754e6d4f5a485055374e3778557733476f6c4671656f5274775449694669344a563142367339797a41644348424871355533620a7879575a732b592f51437448776d795030365337513332592b524a70692b37554b434242412b714d33505679614b7775364949566f56424d616959715538702b562f356d634e6874445346640a525a6b483073686149696f536f33345376386b6c517944476a36434262572f7a58632b6b44673369384f57536b7a3557754d31435a5658706842576d4d582b654f324e3273597666757649560a415143794344766349496d44574b6b4772766b4249636274573674333744367a686371634e626c7a5366476b4b6b4e684458326948594f6f696b7a4c494f346f457269794941354c694b43520a786d597071505648564c725a765347324c486f47624f3164684b506a6b68695273637a43527474775747574330573077634f594b782b384c6a707a702b4c5235394b69315a636665545554440a5a3644366245547231674237644a3378634c614b353168506d445062534457305362794735317247576745584652715343644d543645714834696456396e427562557879787778476a616b500a385774596a2f2b6d354344567344466844353470437770376b4f617a5779664466376a657352385270694c3838616a3666776f3545654473584a686a39546d636d6664323258554f6f394d670a2b59304b416732595752682b475844545a2b59704762346f4a583530336c362b78755872345473643275384742796336586a66484a396d5358796f5457584f706458615058506b5245507a640a39427438366a52574738633946614f744741473932547a586e774333464d78694559735a304a33745a7a696274496e644957656f70785673666b6d68706f6e7558744a734b6d5937314354340a7168414e786d346b526952326374345254494e7152486143434c474e6d4f396345745654714e713669576d617a55777a49326d4f6a4c6e554a517032682b6f6c6852443137636c756e3671450a6c657a2f543352386b6f2f58656e303134727641386638442b346d487270482f49474d41414141415355564f524b35435949493d0a	f	t	\N	f	\N	\N	\N	\N	\N	\N	f	contact	\N	\N	\N	en_US	\N	\N	\N	\N	\N	2015-02-03 03:59:02.525944	\N	\N	1	Template User	f	1	\\x6956424f5277304b47676f414141414e535568455567414141494141414143414341594141414444506d484c4141413254556c45515652346e4f32392b354e6b3258486639386b38353936710a6673314d7a32746e33777373466c6949414a61672b49416b696a4a706b72626b6b422b2f4b427a2b4c7833684344747368785730724c4273686d67434a454551414c45416472485032646d5a0a3656645633584d792f55506d72523443494356414a4c714775796469646e713771367276334a736e542b5933762f6c4e2b522f2b2b7a3977506c3266324b565866514766727174646e7872410a4a337839616743663850577041587a433136634738416c666e7872414a337839616743663850577041587a433136634738416c666e7872414a337839616743663850577041587a43313663470a38416c666e7872414a337a5671373641583851532b664676684f5662664c6e39486f435450356958352f662b6e71362f6477596763766e417a634164656f6665484c503432763379442b54660a3569416742565367567441693143706f44594e35386a312f5839626643774f5948376f37624462514a716433414764634b4164377974354e475065466f774e6c484146703145486a6753754d0a7777684e5745334f2b747735503450486a3433484479664f486e5a45684745686a49764c332f58337752696558674f51324b6e754d453277586a74466c6576584339647647556658686633390a42556448497a6476564737634844673871687764566659506f46536c446f345770596968576d6e647544677a4c7336646878395066506a2b6867382f5848502f6f777365502b6f38754138500a506d713477584a5071505848764d6854754a356541334459724b4531592f2b7763507375334c6b3938726e586a6e6a746c30616565365a536c3073474752675868614657696c537343314b550a635267754433654454647577615a30622b30366e382f787a6e6662466964596d6d6d313464474c382b6466582f4f6b3354726e2f77596f483934327a4e59796a554d716c56336a61316c4e700a414f3578706950777a484d44582f72714e5837744e775a7533396c6a622b2b49362f76376a4f4f496d32433934514b39645a714475644f6e4e61767a4e57344f436f4c69596a6746465367360a6f4c57795835644955537243335273547a3979363447762f2b496a762f2f4345662f4f2f6e2f506d6d3265635049726a5a686a6b4a34504e70324139645162514f3767352b776344622f7a610a794e642b61352f6e373937683371317275436a5744427a577130322b316a4178656e634555505674554f683052444d4245415636374f4c637953586567496f67496979484264663239336e6d0a7a6d31652f65786a66764439422f7a722f2b32456233376a676a5935705172366c43585754355542394134584635303366755561762f355044766e4d5a35613838764a4e71693978633662650a734f5a304d6477633634596a6944687534424b5a4155437067706b676f70675a354776435542774d4a7344596f4a6b61464b4333516c48682b476966473139616350765745582f7978592f340a4e2f2f6e59393536737a45756c464b75386937396247766e4457412b5733754861573138385a6371762f4f66482f4c6c4c39396866332b424d744b6e7a6d515433554863743264784b554b590a674e4b4a56453749445337456735583466775645426263776d45366e434369436d65506d4e48656d33734668324654476f664c734d3066632b4b32524f2f65572f422f2f3633322b385563540a34794943784b63684c746835413343483171424e787175764633377658393769793739306934506c416537435a6c7254753864443958447a766e58446773595074713765746a3852484938480a546e6f4763556f52756a7443354a5942443452526d51657730413236623169764a2f595741347646677139383653614831345339777766382b332b375a6d4d776a6b3859334936756e5436780a3568316b42692b38764f44336676386d62337a70486b66375235674a3630326a6436653767326745633442342f48455077334256616e3550446244353341644b6643456f6d414a4f455955790a33356f34487341514646484e49384c70336269343248423676714731776d64654f75612f2b6d39753832762f6549474b4d3031686a4c7363472b3630423343486165306358437638316d2f660a34437476334f5a677563396d636c7166634a64773553346f6c756173502f6b687742796475526d6154305252554f696969506a323557364775754d69784e6b526f494f3634313051687a496f0a72526e646e5459317a4979716864765872764f372f337a4e79566e6e57392f59304a6f79375041323239314c7934444e46563735624f557258396e6e3276554436454b7a68726944392b31720a4c2b4664332f34526b6641414974675473554634466366634d796730334e4d314f494269486177374b6f715a6733554d41343355636635396d686536576d395954784f7464323764754d452f0a2b2b31446e6e75703074614f79653536675a333141437177576a6c33583454662b532b4f6550375a323943553962514a4e7938533170735058352f4d76353638322f6c31556355783342577a0a3850424f476f7749754e4a7858414c326c554651463172336647385946514b716d664e7248413171696f765157736561734277724c3778347946642b32546c39644d624a34386134594365440a675a3330414349522b434877796f7448664f61565978426c307a724f5a535848435241484951306864333947375a6a48447030444f445138513562347a446f69594367644335646a6d71346e0a506c4d777a4330386856304770644f6d67306c6743745952366268456c7243787a6a694d765048726c5264666866586174756e6e727132644e41414962502f65692f43725839766e357655620a39436c32577a795643505a556462736a6662767446565742444167644b485068514f4c633136774853775944525331776f4b6a355a566f593251456c506d2f4f4942536f6f314c716b7875360a674f6a3250623037766348522f704c58586a7667376a4d4c65767346334c5366592b327341646a6b76506a6967746465333064564d66647444716361694676733667427777504c37677273690a497052534542464d4a6435725942696d73647364775378327035714365735237716869475939436875784f2f435a71427458415067714f7171495a48635465734f394d30596461787166445a0a7a3432382b6871307a5137366633625541467148355145383938494252306548624e6157447a7557414a624a76714f416f67377534654a565064412f6356526b472f57372b4e384131546f6c0a623066482f7570786257772f4134694d4934446c726439783678694371574e75394e5a7855343575434c65664b3953783743516f744a73477342476566376e79366d7637374e556c676d33540a754844466c753438416b455251556f55636f49626f506c79446465657877516f626f703635764d2b372b42494278307769662b4551516d554f59444d5231346b73514f41674a7a64505642490a4532714a3339323667586145797033622b7a7a335171564e7532634275326b4172664f5a7a31566565575542486a66666572393851575a6a45525845545255635638397349494d346a7a54650a4f76486738787a774a2f61335754347343387a4f4c46452f77745637742f6b5841597035654b675a70544a76595a416f7a5476574c594f464e4d386d334831472b657a6e39544951334b47630a634f6653514c4f675a6430344f6d41635275626e48696d666f434c7a4752446666774c453053304748482b725175394b4a4943322f6434634845594734524575356b4f706f676a47354b41310a67384a30514f345a4e7841666f4b5567706f464871464f4b527058526a53704b4e364f62737a68776274774f654e6b36364134566933624f41316758626830583774785a4d41795661524d6f0a472b53757a4b39396a747074727644465938344449765a35683368364d7949766b656c6c5247632b6d30563862724f4f4b336a5637652b627249574c4e2b6a6d644465735135383633586f690a68307033364459486c5158725470384d74386843396865566736504b546d312f6474414175686d336e6e467533366b7336684b58515054674a793957352f4965414961494d6c6439524a4c360a472b6e4339733152413469664b5a6356517447492f69577a68546d6c6b2f513463367967534c7932526b4b4a474b705164553438515776454455505669456c6332442b7350484e76774d51750a72324d483173345a67426b382b354a77383162464c4866316a31477a7a51307863726546572b352b4762323757584142504b4a7a784c656577707834623374693931392b38765a384d412b6f0a574c74683373453643537748546c416b483261556e4b31336567386779637a6f6272674b4c6b4a3335647131777230584244794f67563235387a7479475538776255323466576467755638690a6f50707067624d70694753705655414d7479635150342f396133546967646b4d466a377843332f4b4e6467542b66385431504c3466676155727168456e53415952334d4e6173354a2f756f460a71776a696c655769384d787a4c55676c39716b482b496b316b7a3457433968626a43673139747273307563304d44313742376f6d4d376737576b433649433549466d7a6f6e70746636504d620a79347a6f355a737a78625230353748484a564e4a78544a463144787656435077394e3652724559364d496851696f417156516f6c6155467a32566d3063334355694f4d4f5a594d376c51576f0a4f48763768635659342b6133634f6355785330656a75564479364d5531797a6a646d4c6e3269587459363445756c7569675048364b4f3049765274464262456578304f5351794e74374767680a7a54434a4932364a3979632f51495275555646556e5445497077504e4f6e545034384354666c616f315a6c6133786b6232416b4475477930554136764b5876375133377a695a524e774f55790a6b684d697541495139546a396f7a35376963395a48416d4b6267306c647531384c4d6957424b6f613772786270476d326465636c344f4d734e436d797253313064347250364b4c68417156450a4446416b50496b6d6761534c554c5277634753733167456737634c6143514f414f5a567a6a6d38712b2f734663614854364534656d73472f647a4f4b6837733241734d503339446a504c50590a675a425a516f396448304253484247474263706e50627843776e776556614174726938696d55376174744c5945796a615771303433704e2f6f454c7650514a54683437546d714561715768520a352b4367385044423941752b75332f3932706b595950614a787a634c682f733136566d42384d336e763775686f7476637a654d464351596c78322b752f47574655504b46346d5239494a39620a766c386c436b68714d365662737551732b54724c387a397244717042463266324e4a4a6c6f56696c4b4b566f63685267474170614b753543485376586a755853646e59674574774e443541500a7739573466684f572b77556f34454b5173384d6a5747444369636c486a743074517a71466e7656376e5a3947416a53345239336642653839383363694b4367424851556e7343656649444f490a546861584971647741366d793954444245776843535463434e695a6a6a4e6d62454547716479684434656977423337567475574e4b31303759514143796449523967386e74417175796342420a34775a69436658474475325a53306c692f3536566e44674d59733231505a476f3057634643544f4c57474347685a4d52504d655041754531524a41734261744759576c4c4e387633347772640a4c313270524f6d366c6a68716d74763239614d4b423963444a4f70505644657663753241445634754561416b4a537344766d3351357548675451785265664949526c78776c326a76386967440a7577527336354a6b4559385373586a51743744345753657166743474434a397a42544776783943492f75334a68303859444a646f497153526b41477152466e5938382b634b5277646455522f0a724e78386857736e504141514f30364671526b304b4335736b6f645078472f786b4754377631487438376e4949786c5a4f2b483338324e376c496364454c50746a31776c5573756b6b45554d0a366b6e6a6a734d3573416c44697150754e504e3046327a545568456e474d4e68494c31625643584d6f495852646e4f364361724f654e68526a57615458566737345145694749736a594a71430a57796371694d6b54726a64654a466e58436342486b764562726c717a5769685a7978654a42794d5750334f4a6343303851626834546161484a6d64414c494f2f4a2f4a366355577155724d650a34475274514335766e3545745a6a6853424e464b5851777a4159334649465256684235473830534d634a56724a7a78416f4c6643596c6b6f47696d537554483169594a534e48497a6331427a0a5242733953367556324c565448716d694763586a77526153795067397134686442444551622b47476465594f4a703950504479466464797a533867362f596e7963353442455963672b4a59590a4574593554543238565333307246455763615a4f744a594a7a4a584d71313437595141514a4a766c736a435862475547555952745052343375677630434c4a456f30513748386246464470620a737164333643354a4559767646517451687a79766364756d6354315a7836494b5768423370486c36435748576e464735424a416b41306e566f4b4d464c423279492b596558674d693576434f0a4767796c706c6c632f6270794138683444436d77767a2f6b3773324b6668376e5259496e454d68675646386d39334476497251475134457567642f686248647335503042785161354e4d38510a68393537355068754e4a757a447165314a3769447564746a7230666861656f4243307379694c5970706379326144534c4938634e624a714450735546744d35527874577648546946637365720a634f31614466544e4176627450585a55644f66615a545a6734615a4e67697971596e6832386c6a337950654641484f3634783542684876502b76786c5242393876746a564a445173474433520a76426b516a74645a3776613438706b5a4a4361586a4b4f5352574d33696963366d54775153336252596c48514759612b3472554442674267714253755861395a586239384f473453685235350a346d35466e6857426f4d644f613038387a4a353574383145494d6a756e32775245386e577354414b6e32734b324357534f446559534c7032742b3331694d6375686a78756c473062477135680a634169545331517353326f47694f487137423971594233707761357958666b524146454772735734666d4f6b564b573154752b4a796d6b50743231477a776454584f6b7a5756414b654249390a7333574c506f4d3345753165376e6a764e44547138566b4c364234416a7155796949747676555a3370366745306d692b4e6370756f512f77354a337250547557744f4374302f4e61724763770a3668624970526538433963505268614c786d72643043736d434f3649427744567773326241375549534b524d454f79646f744867456256317a51444d67366d544b654d576842484e326f44690a4c6847315a357a6f346c68537a4f616a5144534d516a7862784e31424c4a74504d37577359586a716a6737422f796f70472b4e7a2f6943526b5a52524755744256466c555a53693639565a460a464d7934645764674847756f6b5678784d484431486944767559717a5046413255385736527253764d2f6b33617652466f6f37655a75434151504161546b33533930397277704d38624356540a4d636d5363626a7331426649584d437a3439694a6e64304e616c576359417570675539474c344c3148686b4659557872363667364b6a56696c77497467534f52516b75362b4b33624338626c0a697436767669423039515a6749436a644f314e37784c3362317a6a61573243745264457645623775686b694a4b486f62325474657376627573526372676656334c68733658415362496d736f0a6174754948614c415a4f616f646a786254614c6a72472f66503765647a634767346545425646483344426964576d62304b4a5247385367453455347078743679636e787a48317574554e316b0a73657471317734634165466d313631782f2b523962743234786e4b7833476f41744f373033684750676f3731324b56523041466336436262514733716f65586a42504f6d39376d74653637700a523230676772724c574b5033714f573767456c672f3845564d486f5049436d6150755033744b6c6478694735464d6e476b456737707a6d4f63566850455a67654c7665343650655a3270724c0a484f5071316734594142464659356733466f734246346b484b514953556670572f456c36426d52527944467a72505674354f3943524f395a2f52507065506434502f45413278534235557a5a0a6a6b4a524e48657735525245684e3537304d415177573147445a3873356c69797a384f4c396178586945614a32516d6f756c746f6a6731446f666b6155514e522b68586a5162746841415a560a4333754c45524261623754576f4d557546374941704948687a7a556939336e6e653962794132656661527061694c54736962545350476f4e6b526e49746c4d4969457168527a4648504477500a6e73626a547448344131433035674d4f747a2b6e695542364b636e4f6f755177757443614a313273634852745a446d5575625a305a65767159774179384a366833545a466c4e6164726830380a7146527a7061395067644b4a70767033466d43733577664e4a4645636e594c6672305654447361542b6d4830506f487045336c2b5373455130472f76766d31436262306e4842325250795a490a4d566f7a714c4939367a334c784c314663426a4559414f4e362b7374436b5534334479755044675354732f38537247416e54414141447a4f62754f792f302b31526f36654c7a474c4e4d34380a4933744a4b4c676269314c2b4b727075655a5a4c476f39495573656a4e6c39717853584b77374f385449424363533658416569424e3269423256553451526f4e336f456c484b30776c6f676c0a4a7163574d4f2b5952426f71356d7938305477527a42362f397a4a6865514b782b6757766e5441415352476e61623042797a79644761587a4c54736f6c46745343325471306657562b5838300a626377334d6572764562644c6e746a5a74654f434a6b484475714e6c4468524a46393544397155484e6d48576b794179747858424e45584d34506b51497a33557442484458476954493058700a335768546a77356b675762477568736e6a78757256643032746c3756326f30594946316b6130367a4361505256514c584e347643692f69324d7567753455703156756d4947393962783370480a5259694d7a464f2f78374f6877366961374e32576644374c5946446d654f495356484c766c4b704170626367646f67495773766c6131434b706f50774f44374d6e595a6862517051615643380a6172435a48495a614f4473314e7175325a54356431646f4e443043514c71627a4978342b586e507a6f4b4c446b4255395a2b4d683743526c7273466d57675a527a3839634f3449396d4e49370a3449706b78322f766c396f4276563957436c754c5645364b4a464d6e6c4d546d4170484e76594745395531543150764b6b4d544f6b705453336e474e48542b6e714f59576f684471714866610a756a4f317a76473149315162335378364550725665594864384141435275585252777665652b386835395071435a3265794d557458786536554e4547326b6a7350746c427a4d5768784179630a75617772574a643039545064792b4f346d656b676951624f656b527550666741633271593135444d524a71424450485a6e75586b794235312b7a746e576c4876547158694167395054396d630a48694132454c4b6c56777347586230424f4a515367782f65663874353950457036383061383735317931477a7a324a4d64367846536b567a334b62493463567851737852784c4c53463872680a5a684d7544627a5238334d446666516e3348325566363248713763756449763451504b42696a2f52496b36556e5875535364326a347a6a517155676e776250745050434a545463754e684e760a6668644f48734977634f5670344a5562674f6456744b6e7a30594f4a36376476634861783576486a387a685838327931626e6a766d486c5172544f773639304373322b2b4c612f327a4c6e640a6e645969414a744c7864364437675742465a69487a70385466583554373545706943514b4751393647365137394768455443617849384572702f644f537a58782b642f572b34535a633359780a6358352b7876503362764c4f3279732b6672794f47734d5663774b75334142673772434a4b502b5a3437744d76584636646f4857676e6a6d38506c7a556146715366416c4f487171496674650a306d4f51715a615a5562525174515937324a576942533261696d4678726c744376615630616c573052434e497252722f37306e396d68584130684256684649316a64525349436f3467696f6c0a395961454b73703676614a5a3535586e6e7566696447596a585633364e362b6443414b42624e3477767638586a6235633864787a437a43593170754d2b474d616d47454d4a5374326e6e712f0a76614f6c737534644e35384c6857783675507561354833447342344d5571314b6d364933514d52432b4b6b4a72725a6c4a63575975623446616e71666a35654d4d62777a444b455534684a470a326e705178546264364c3146783541363638324778796372336e374c574b3039696b55377348624341376a444d436a54424e2f342b675876766e654b3951324b55685a5264664d65455865740a48756d66357663466d6b642f586c474e5558445a4e464a726541554973455a4b4d6e717a523744493551345176617a7a56364b534b444b33474151435747744274514b56716b4b744e59476a0a59416935514f2f52426834534d574e51327a484b364a77387575442f2f6f50376e4a343168754654537468327a526936717648325732656f444967617079656e3466626e306939522b544d500a4c6d43664f745055775a7a4e5a714a76676f35746c7346566a37527344683762314f6c5a4f4770544670585366574d67765966434a366e354f37566f38736a336d59662b514f2b526e3354760a6c352b396272524e427a453230785443305431696c665056686d465162683466387433766e724a5a54636b6976747237446a746941504e53466461627a7168487443616358467851456e34740a5373373843656b3174356e342b55546257416b45304f667559506374527138344b70366c59434a3954452b687174474c4f6a6567657153624d376a6a7769574e584e6e4f424a72784279304f0a4a596d6c2b667135726a694d776d534e7a52704775635636466133694f744f5872336a746c4145454d62667a7764744c506e6a50574c645675476233614c426f635442374132754a796b6d300a57556e4a427953352f63564475464653705350703359706c2b5a644d3335496a3049504c5a2b5a4d6334436e4b65346f756d554e423261514a57636e677330656a435146364d54786b41616f0a566d696244522b386638616233363559707232377350746868344c41656455692f4f694878764c34684f4f3745314f2f6e565476534f464d674779764b6c323330697875346461313143522b0a7469336f30354a51346b57535552776c34745962673954304b6e4f7735336a7a494b416d71424f436b7846676c6c706f31726639686a323954434761554b4c2b3732773250565445484a70500a6650446869722f383969714d596f6545496e664f4145546837474c4478772f5772433655746d6c49716e43536c5439524b424a4e4a473643536a5a70494a516b6952595055595a706167774c0a3363724a5148494a7941356a59743666355051785653696c6250762b6753326f35424c45306c6f563063713062705161684657336a744b78394135526748516d57514e43577930344f5a6b590a68737472324957316577615135377064334f546973664434374954447658323652303776466d5067316a36463646636846446c646b414a544378444858534b486c776a77656e4e6d796539670a3753516b5041554e624b6a78774d7969583643317741486d6e48396566524e36675757774343417453435a544e7136734e793161306e716e594478656e2f48687538376a44363554744630350a436654483130374641504d7178586e34594f537474786f6e46342b6a313836444671343141726135684777695343314231795a364445566a5a694151657236532b72344970536931316d33500a58716b613966306b676b52306e7077694b645368556c494258455570343443576d43632f6c75435752346551554b51776c424a6a5a497451786f4631572f5032323265383977355a563969740a74584d65414b42554f443978336e33336c4d39654f50416355347047757164636930656256664f59417161445974306f4f637244504c5239656b397433353446485a764670594f714e5866700a47706576682f6a73545a2b51486d6866794e4d5968556844315954576b6c644170487742507773714156327636557a7277746e4a794b62314746752f5932736e5059413775426972387a30650a6662546b39507773635064737870764c766c4639793753754d386668573335656e4e32456c39435a54474a62446f46495a41375766567434536a59684a6e6c7a424d416f47743743653468410a434b5436535059767a746c4571704d4d4656626e4a337a7744707839644c446c45753761326b6b44454946616a656e6b6748652b76382b3748333649573664376f2f575774546a4a414336720a62566c5643766a5773655a4d552f44357177686f4d6f6c556334786270494a54736f306a796f2f3676465379683643454b6d6a6570584432305744614a7350706b6449786b30624a556e49450a6d52383965737a3333317a783847454a7247414831303461674875636c32666e6e512f655866486f38597031327a4331614d4c6f67657767325545383964514564734e6d4366634565537a310a4143526c344b7a334b506b3654504e4143484763635050577757597779537971653033704b4c334873416a3336426d306c6e724248726c697933344236383735367077505033416550777a6c0a6b46304c2f7561316b7759413451564b6461623179506d6a517a352b634971494d59786a4247793567305067613362724d62496c496b4869367952386872534c627275453365506e705770790a4e2b5179324d765063677053414b4c41564f7373455750356459316a517a7a502f51596539505148447839782f353372394c4d62314746334457416e673842356c654b737a6970766673735a0a3968357738395968516b34414b554c7263766c675578362b446c46434a766c455563474c6a4f464a6c66592b52535a5261735142696d32624e4570522b7452776d5a4841454b364b374350660a337a3171425171394e3661704a5862676e463563384e34486a336e2f485757314771696a37307a652f2b4e725a7a31416b447443552b6678435253576e4a3676574730323063557668546f6b0a456d696531626351686171617539387a6f4378524f5a77376a7057592f53737835534537416d4f49564968485a4b6f34684543567a4d4d6945673475706353783463453555495253433755550a32745434384b504850487a6e4c6e3139674a5464336632773478354173736d797253747666652b51565875507a3735796c30475036564e6a57455174494757593642324b4745314a556167550a66706f696343765a746830612f3045434d665353616d594b616d6750774561307847653730684d4e46493930722f644f733241577a3933486a6a4e4e47387a687766736a6d7a5755756874610a51482f64326c6b50414c4d58634462727a72732f564262316b453262574531725a4968677a4c57674e66554174715250526169347047612f617042476f306c6e32396a52633535414b53456b0a566456534f316a5451504c72367345636d75665a426c4d315745485a6f464b4b73467064384e5a37482f48753977353566444c6a444c73442b2f363074644d4741435370456934756e4c4f500a627650756a78357863765934577264376a796d6579644d4c646442553570445a39546f7168586c55504e6b65376c674b56446e573034425368454a4b4b70416e6e74413244577642375a73320a795657754a64492f435539316572376930656b70626233672b392b7032425170366936376633674b4441434c4857746d2f50472f6e2f6a7776634b4442342f35385037446d42506b527439590a59506f2b64784e6c355936456772476f4558514153564b70626e2f4270575262474d6c4d506b563879784a75566d684e61475a4d66514f74522f62687a6e6f3138666a736a44624264484b620a38335062696b6274387536487038414135767458617a434861332b523957726b76592f65352b523842643469554d73697536705361673233443648384b556b546b38447a6878497158556a550a466a513568386f5437434d50615667525255753263496c5461786a576a446567384f464844774d76364866342b683932706d615573767537483359384350794a4a6361666666326333332f6c0a4c746475664d5150336e71507a3733384c4d4f694d696a52752b666766517273766d683038467271426c6c6e6d682f717250376855553255796c6161446b73426968357059436c422b6535750a4d446d627962616730734f4846337a77385831575a30656376312b5a576d4d634c385773643333747641643463705543552b7638364d306c5333324f3478736a373333344d536e35546446730a2f63362b50364651613256556a65484f41707265416142716e50757a4f6c6752595369363752624f4756443062424f7653474946485257597a486a7a6e5863355072374a7463564c2f4f56330a54734f623848513866486a4b44414267584d41662f394544644c724a473139366d622f382f672b352f2f4178725275625a7079764a715965354e484e464c57446e73316b5974467732674c500a70625647323078304330474b747435736a536361565a32704e61773172426d7261574a71453937685974313438346676382b4a7a782b6a36576237353959354a32346b6845442f4c65736f750a46345a42754c6859382f626247777258325474633874306676734e4844782f5461556e6c446761765a4463666449704b646948335650654b614837623470312f5438316f6c71316c5a424e490a6a7143566a4348576d38356676766b4f332f794c372f4872762f4961313564332b4d3533506d49636e344a442f3866575532634137734c4259655562582f2b49722f2f52475a393934566c4f0a48702f7835392f2b495439363733363266526c7432744174524b4f69527a2b36687166573644326f3237306c5a627842444a7479756a58456a59347874656731624c316e61376879637272690a427a2f36674a507a433834754c6a6835434f74567a683353703838416e713467454d4268484176767658664f743737562b637258526d346548374a5a4e64373734474f6d5a74772b7673372b0a336f4c4e70744f613458754c6e4f65544873474377436b7549664743305631543562506a556d4a775257594452597a7a5465507832515833377a2f6935507963352b2f6535494d48312f6d7a0a50372f50577a38345968796675723045504955473441537231686f38507031414f38382b63347562683066632f2f6768623739336e355054433136346435763959555348676d306d4b4548580a626b45735971684a4335386e6b322f4c784a45534469553668553750567652707730655054766e6f34534d4b79723362747a6e6148336e32376a4567584b78377a416a61626454337036366e0a7a674167382f5569515162747873482b486e7437413366724d573371765058426654372b2b4448503372334e7a654e44786c4c52576c6a736a5767716a37657030747147576b764b786756430a61416254465043514b447a343643452f657664446d6a7433626c336e384f417746554647626c79377a74376847444f416b6c32326e566a316c4b796e3067434d7242524f4d664c317a7645420a517832516f727a307768327533396a6a2f734d5644303865383959484833446e786e58754868394837324232382f6257614a755a56795a5568456b5563324f3176754439447a376d2f734e480a6c4671356458796432386348484f34747959597962687764676e547533595a7637346559354e58332b76377336366b79674c6c4c317a79594f4f743159375870484f377673643434376875470a73584b306630517453323564322b66426f314e5736386233662f512b362b397457433472792f306c67305435566f757761644666654c712b5948572b59616a4b596c7877353859784277636a0a792b55655653746142785a6a51515432397059736c6d756b47506755476b4c4e75465163657a704d5961634e514f5153547032356670744e352f536b38385858372f4447627877682f6a34710a796e495a67356c374e307836514c77794d75344e574c654932733875324b77616d796e6d4471326e616476765637577972414f4878794d485230734f6c6b734f392f646f4f654a6e4c43504c0a7663706955536d6c4d67795635546a773847544e312f374a3837544e4f582f7772392f6d38467068735642716c566c574b4e444a7137754e662b50614b514f59482f593852715931364330520a58686632463557585839726e3649627a705463476274786463662f4245427a2f785943754f7a344b7454624f456461624e654b774845663239776247653764356648724236636b46773143340a57452f556f686968495644727948496347455946633751495a6f32442f5433323938666f4679797048473664672f304650337a766844737672666e396633474e4f74376b7759664b573239640a635071346f63577051794359556c49396874314343612f5541483738676363755434302b68474770584c734f693458684f6e48394a727a2b2b704c587637444136356f4848322b34652b75590a59546d43436173574c575344447577746f497054454b626d624e5962334361476f747938766b2b704138754c4e587637493576576d4b5a6f3870786177373077314d4a69574c4159467977580a492f4f63417458514d53674448423373632f33776b4866657638397a7a3637354c2f2f62512f37695479346f6977316e7039436d777570634f542b48396171684a5977685a307074446545710a44654a4b444342374d4c636f6e50656f7977396a5a572f66514472372b3456377a773138397457426538393331693130576737324f6a6f6f42387562334c343255497653724c4e5a625942670a41745a613253736a5936316f4353326531706559746444726254425a522b7341586c694d6866316c7a4377454f44785949464959687442384c7955475538327a51736452474f7541614f48560a563535684d3355757a746563587177357648584f722f3554342b6a364874505a48742f2f64756537333776673477664a577270515670736b736459745a2f584b696b645859674442773439670a726f676778646c624b6939395a736c72767754373131656f4e6f37326c5676482b78776637584e77644d417756487275314e614e4e6b3030633161726954624e2b547873656f7464567058710a41384e513846576a6c7046614f704d30436750446d465047454a616a73467773634666476f54443154696d466c7630463052386f624459783571576f3463326f5a65526762384831673332470a4f6f516d494d72702b59724870366463753337437335387a3269535576733933767758662f6659464a7966425357677457452f6c696a714766364547344a36373352317a35664267355055760a566536394e454535342b6278794976504833507a787650734c516538422f392b357647744c7159747a332b3958744f6168583751584e63487149587151643157565a624a3346474e5a7446530a4b7a614f5735575159597a715836713751625a336d77656265427843386e32616f76342f6a6a57316951434e46764f705256667833694a6d4473355453473866582b66756e52753839676f590a6a6365505631792f387a485076396178706e7a346f7758662b68506e343439586f5275514855792f53423742333630425249704e617945443231764d42767a384677617533586e4d395776470a5379386638736f4c74316b73686d4462456d65346d4e42366a3235626e476b7a3453363031674b5833376149435768324476645a764c764847426d54714e354a7a4f2f724c5a513761306b530a5341734353572b477974785631434b664e356a574c6471386870722f6c6c415662363078444536626a476e6467456a377a7334326c434b4d343443624d7934576a42624b5a4c574f374f30560a50762f537947737633575671452b2b386438717465782f7a3447506e38596437664f38764f6f39504a756f4174517061552b2f69372f41522f5a3059774a792b54524f63587a696c566c35380a5a6544467a78693162766a4336306538384f4978653876434f4f797871434f31564e617459564e6e5a52644d463536544e324c486231715059557a467163536f5744454a5a5735693577794c0a496572304c5a67395a53434374793730456b66454c506d75434974785249737962597779774b43437a705049697756667747647157583143554e4951486167787343796c5a315044774a7a650a476f367757612b3457447671776d4978556f7451686f46534b6f76522b637a4c657a7a332f4247625a727a2f39675833586e6a4179556e6c37546372622f2b673053386179365767513259510a66776670354e2b61415479686f4d4930775762743742384d6650346677505537786b73764b462f35366a5645344742357949326a6134676f6d3962597444586e4632764f31343268464e796e0a545031434373627a583935366a79614f556967454362514d425738784436695a785a53526a4b5a4342364251527243706f7a6f507073786d6b6537344644752b782f675274415156764c54730a436d35454c3247506a754f6545764457516f476b4467576e3478616755736670715448633837337151753972616f46614a3659656e6e4373533637764c394543792b4745752f6555715476660a2f4e4e7a376a362f34654639356430664b6d636e515947764131746832622b746750452f3251446d38386f644e757351596a6936507644734338617a7a31582b34542f6135356c37417131770a382f6757423473392b74513575316946616c65796563574476476b6534324a536f475565355a6964334949525a367955677072525350322b4649396b48686c72676e6b4b516f71436c6d7a2f0a54734a6e4a645842746f644a444a5657523757674a59786e736a56464b7155494e7157455441644c69706e586f4a78484b687443314d73695445694d714f754f4a5344556965504b7a466b310a35654c69424a5843636d3967555a5963336a686950573334796c6365386b74764c506a676e6334662f62387276762b44695975486c5a4d546f39544146703638372f3870362b6332674363760a6f453878796d3235564737634646372f777369586633566762782b7548783179382f6f7852574b486e703566344736733167336f71636e7649634259596b4b597a477a4c416d4d74455a52740a4a6f59794248314c6f56683043497235646c655544415462464a38334c457149534771495066677345704939685855634b455859724676792f3255724752436a34564d30516f687159736d680a45485347506348376b4b70684a51506343415a64504c75576c476b643039434873616255486345327a6c4a314b63624668624d704d493454366f58624e3235546972432f4f4f50772b6b64380a2b594879375438742f506d666e664c3445577a5767745959544a486331702f6245483575412f447370473035796676326a594576663358424c2f2f36534658686857647663724333787a54420a4e4456574c564b3261597157616d73644b54456c314d795157724845354b4e7033324c43686861716868436b6136644e387a54766748337837507276485739784a43437044644364746e47470a6857393370366673754730737047564673786e556f59556362526c436d79693467754339595461336841485649515569536f6b2b784e347374594b45747245306768726541524b44434561540a6461504e6573505a6d6835394b3436316954324a7a7a31634c44682b355356573931626376766b78723335787a62652f71587a37547a7150486b32304455694e3251672f372f715a4457412b0a596c734c676162466f76426276334f447a3333426b634635366358626a47566b7149566d547250475a744e69444a79574144344536724b47455532687a71554b777841377647394142364c4c0a31364f6252386149684551392b2f5571577050524d786c31534b514f786171426c4d6751536f2f36767054552b4f3967536b6d6c546c56445a416771575534485552584776514542706b326e0a4649313541683630736d4b61675353684b797946556b754952307a686564784432645331704353646f784c5a7872416f32624957744c4d79784c57364163575a4e6f324e4f787456446b536f0a6465446c462b397737356b62334c72356744642b7066504e502b3738346238395a3733704e4856712f666d5979442b7a415551564c6f59342f715066504f4c6543797465654b587a366974330a55423059636d726d2b576244656a30466e74364361313848702f566734317137484e77416b6f494c554d654361417866694f61636a6c536872564d47784a4c705a30454d475641616b585a590a373367716366524e42343857727a34354a6b595a4b6a4d4c4c6f5a4a476a49554c4b6c686c76336d6252504855556c705761486748683670754e4b6d467273647966644347614942316452690a49736b6d486a367a734b577a395272757772416f306231454b4a685a617a42552b7159544e465a416c4b6c31787247797631785347486e6c7854755964636268506a667544727a377654332b0a6e333933796a51356934587773354a532f364d4d594e62506d795a6e733461585874376e713738783875726e52703635653852693734446c73452b74634c467172466562614d4a49736351340a4a3276323142467a644855414359617457387176524f3946494730467075345a3141335577664165732f6c55417077704876794c736351756d387770576b49667549526d76787549784d2b6c0a6834416a35524b474c6b68452f6736466f493576587939515377684b5454334f6236465179727a62776a753443386b475a787a4463356a446b4564594a44466868434c70425630794b386d660a4f525170775378795a353566674d4e6d59356974306172733634425365656d46573978375a7350374c35397a35316e682f2f76446962642b654d473469474d475a736d6276775544414f666b0a55656647386368582f2b4753467a386a2f5072586a71686c776548796b446f4f624659624c74617074577564576c505348592f7557725067337063555a484b6f745954516f6869313574544e0a75655966366b7441446d35794b4b4e676130564b696b4262534d6a326a4f5a4c4b546b675568694736506462722f763268704350634e594d43466c3430424b457a2b3643646d55594a4170530a416d67515243587342676a42366c49554d306e352b6b67745654586e45586761536541497778422f7479364d5433353249525647504f494c43323368635654616c424e5053747737733036660a437165745557746c6637466b71435050506c65342b387a49735065596539383734692b2b656348446a7a6363486633485963762f51514e77682f4d7a3438347a533737326d776438365a63580a37422f43337549616833744c4e72317a666e6147653438624b4a6441554f2b57455858632f746e614661474c55547a4b7343596c4e62754d6f6b6f78597571586543683075434a75714d525a0a567957356657494d6f6a485230374f7a46376144495657456f555a3048794b514b516f6c5964536c784f6a4847446e6a5646635935707a43636e63546b7546504a4f42474e49304d517a7a380a655542304556496e4f4a744e557356454a4b35464e414b32316d32625a646738444d766a642b595668706451445771374f56706a434559776b6a616365576363526737336a706a61794a642b0a65654c56563457376479762f3776383634365037612f6232395438494b2f2b4e42754165352f327a39305a2b37312f65345055334b724b705048506e5667783573735a367651474c644b36340a4951696c3146544f43416b32536b6974422b416944466f754561304378636d526234705a7065716c34464b6e5561584562764f415938564463466c6165494e61517a426950585730434358310a666e5157683749634b3265684f6a4c556b766a2b524231696a4c744b704a314f7a376230304341757952707136553672524a4e4a636345544e4d4b793931436434754869313731525379714f0a45654b57516d516a4f616369304d73616e3947364d5a53614d59656938346e5a6e56496a5668694736463571466e433457575246793858493833656534514e3578472f2b647548323759482f0a3558393678496366626c67732f756261776b384e476559335447766e3173334b662f327662764c6c4e355973354a4237643235685a6c797356307a72614a70776c4e614e7159636b6d316c4f0a31637844763763576f4975416568774e49666b657756487255775277414e615965714e4c424958695563795a3237504161624e316c756a6536546d5a49774b6e51686450656a6330437947480a656637775046706d466f4d6d687a334d4d6e453974663438535369397859783366654c6d5748646349396a7437584b30624153626746594b696b704e3958485a496f387a755755377767616c0a614d317049356f69315050736761416a7a64646d506f745578505659396a65734e3430326457376475453652506237307977762b753339317a50477477725432762f4a4d66337a39684165590a3364466d41384d6f2f4e506648666a7371794f482b396459314945704f3258634a4c746c77774269744774346747454f796e704856436c6c43477150434d4d517970317a376c74716f56626f0a42723146435859652b57695361566136574557694335675a66343869454d514e5734356a36674c4e5931364563566741495159647767385a41576f4762424c486834677731494768444269640a626861654b6d6e69565858625356534b52682f6945504f44473531695274556841692b427356596b67534e4979626b78573956377a344555637a453635576f6b65686972524942596869464d0a763858513653364b756f56534b544350734462726543384d67334b3433476579675a632f65384a2f3972736a2f2f502f324e6c732f4b39745750327048734173327246662f2b4b5372337a310a4e6a6575487a46717056746e765a356271774c4173537a596844426a3750354f514736714569315a2f584c73577a4e6a453056776a4968776538397873616e4459396d475663546f725156350a51364933763830426e414b694b5141566272573752666c59596b617664634d497a7635382f6f703258454a777576664f31427375516e646a73676e546a4256556f5167754953746936615a370a70425830336b493176486a5378495058344749354a55793234325a4559674b5a6537536f6953704643764d7363745755714f6d646f685754494b79676f583055476b5743574e2f4f476567350a706a35714c353270545578396a6448526f7477344f754166664f6b477233396850774c7376365a6e34616647414e36684c70777666486e677a7645525931335157725248615135576345684a0a74546a507a655a64536f355a38797a61514e65493067566e4b414b7547516942444b6d7951576a76436b366657544a4647584f77596f68467a77486d505041703676367a386455615564694d0a4c3551536e6b4552787052346d336f59563156426834684c4a6b76786b4c7a342b446f77684c55495254536f584270377276666b2b586d347a436f467a786d414c70455353673656626e6c790a46515538524167574d6677776e4349526c347a706f33764f71437961515357675936426e5955784b4c5745596f584645444b674b6a4a6e656b317a696c614e7265337a2b4b366438357a764f0a6569302f6c5854796b306541527443374b4d4c784d3071704d63576a3938744254624f59736d667745336c2b57466c4d366961637549572b76396e386570416b616c684731714b4b4a4f6c6a0a686c4f6a65327475786779795230774e5438773941755655394d7138337757684245704931436130436a54446b3142695463417a6d657545546b425664474e52657964754b6958534f584d4a0a417a666f456b776630556a4c744370594247654f5a53595372322b5a7a64627439555a32307a4663357666426e4667327a38425049334f714e514e477a336e456652357556534b516c6451390a314e424831694a34443361547537465a7a644931787330376974614372634c722b59383172767a6b456544786f6a345a4b6343644433306576547250326f5559766851342f5a504e6b6462620a31765646697157706f53743031796970316872777163575946795155746d646871506d3938784f74576332447941596b535a6f795834796b5277785a37347a416853346b66467879394574670a79364839482f3941315267393533686368306a71426f44716e4b624a37504a5361547a7965524d48496c61512f507a353961616852463553683843365579543169444a6f6a54384a5047586a0a5374454175736a30636174646c444f5154534975456458346430704f5378554a78724c4f5a6568495664765538596d665369623443512f67446c4c67327655684a426b3952524973746653470a634e50544650317a4d62493172466b30696a4132793632557370323230533241483748344f53554d4c514c783346306c79413978647361355a30622b6f346b7a733179363979442b425549350a6a474d456f766e5a574f414261704b617634494f4774334450672b465944747852416844435a65716557514955352b6f5770696255734a4e786d655849706e6661344139466d4e7161676c470a6b437052432f43594c43496c644164724b55466353613836464a324c6b4667716d3830464868566848437443584d736742556c745a414663616b7841485377306b5373556a364e694e63554d0a34384e72492b76563946504a4a44396841475a773430626c63352f66703176683747786962786d342f4e5162617248375a76564e62786c64704958484b725474374e367763594563357468520a3136304f7a33784857795233774b7a5837796e78486b68697049325831396d7352365574706477737034504e335073353642453078737a79784e486c6244393754736b387a314341787177770a4a6d4136797a326c78306e4d77754e61342f635938336761385479626b30513679397248586446514e635078496d696f566764785a6559377a43586a764a62674b57525a32764e61656d6f670a43766c76693167736442466d7937416f77765843357a2b2f783539507a746e5a547736732b503842456d644645366b6b716f4d41414141415355564f524b35435949493d0a	\N	\N	\\x6956424f5277304b47676f414141414e535568455567414141454141414142414341594141414371615848654141415252556c45515652346e4f32623234396b3131584766327676633671710a7137756e702b66534d2b4e4a596c7645495a456a45636a4e35434a4651594863684a515145554b34764944454935642f41496b2f41434568386351545045524367676375436b5151425167680a46795842775250626965306b6e736d4d50544d3966616e75716a706e72375634574c7436624355697756566d6b4d6957526c303658564f3139376658355674726653322f2f457566636634660a723353764e33437631343841754e6362754e66725277446336773363363958636979394e535244353375634f6d4335652f652b736c7830416b546a7759716b3638356e54393459626d414d4f0a4b6346674247326279466e71652b486c42754e6c4130416b62746e554f5477797073633938376b78484362477034534e4c534533546d716779513339484134506e4f656636306b34343832470a39665745694f44752b4d754577387343514a69336337436e5447664b325a33454f3936317a577366486e50682f4471584c6f7a5a4f6a3167625a7a4a674f4e4d706a3358767a766a326175480a50506166457a37337a7764637639367875646d797353456e514b78387236746d67694b436d724f3371357a6445543730697a76383748737573626d3253654374674448766f58516c446955670a57526931695a77626f48446e384a692f2f2b52312f756f766272432f4339766e476e4a61505167724257427853382f666d50506d74362f7a32372f37342b79634f5133412f734755726a664d0a44486551444b34474568616778544531484b64745730366661686d76446268365934382f2b654f6e2b50786e702b796362306e4e616b46594751434c714837725675483162786a772b332f770a4f6a61475a396e6250304b3151424979524c527a777848636f616a694c6f67345a6f61716f65723066513870632b6e434f7331677a682f3934546635314e394f4f48652b4a613351456c62470a413053457963545a326e5a2b352f6365596d4e3468743239435735473079516145564c4f4552793547396879456e4943675a4e443553774d4269315a6e4b765839746e6654667a6d623933500a5778345a636d64585757566d574130414570732f504f6a352b512b66352f4b46632b7a74483548456b515a4555706949657877794a564a4b4a41535268487663666a784c67434675694468740a466d3774487448504d782f39745974736e55354d7079394f726375736c5143516b3342303646793454336a662b792b6a72716835484567455278444a3853386c5842787878354e39373161530a59594352634163546f573168392f614d43786547764f50643678784e4371757967705735774e465565654e62546e466d63344f6a77304a4f594f36494a79514a4f5473704f306b454c4c34320a2b5749544352495942705a496c70426b31527243756e70566a69664b543735707a4d5a36517a65446c4a6533677555426b47423371504c5752376141524e3858556b726831306e49346b434b0a577a564241456c41537069425579334237753749584841783341776a305353597a6f534c6c316f65654567344f6a4a573451524c41354354304d316736307a6d6c6138366a646255427042530a67686459755144684545474459786b6d48687552684c6d484a6168684674595276784e4b37776a4f665a6548416443796d3264464c6a436447706366454337664e32513655306878713236470a75324575714963706d7a694959413775686c533033496a334634744d6b594d4773374143432b364174627a6d3451467434316a764c4773474b774767464f66733970434d6f4d567253684e550a424d647842586646565845333141784a676e6b396f494e364850786b5232356f7156615145316b614345396a36375352476b6556373174562f6b2f57306741345964595837317644535052710a7542416272366e4d335842313343502f6e7851347071674b596e4a79456847683133684f416c6d6b753279594771555962647577736435534c4e362f7a466f6141464f5178726e2f6752617a0a656b415878423331656d687845492b664c716871424d374b414d504d485658464c53776f4a534f4a4244743049336e454643637a576d76595070765162766c4175425141556d3961784e6a590a4e71444231564254444d6655735171454b7069464e566874416a68784f4b734579643178736371573551585a4959365a4570544f474c544331686e6f79704b6e5a78586c73496362714961760a4c32354c6b4c6a743474784e425236733042307a5141496b4e3064536c4c796c424c4471477461557770724d484165365971786c5a377a5a343735384346734f6745714252384f4d654e31300a636f534571534970595a484c5343514d515652784361436731766b53566845756f34435178436b47357545655a674669626c4945324f7071797a4c43705141516f425459504455674e3436720a67345770467977496b436553455335786b762b6c39673055635545314141677742504e34376d593154684155576f316b554972524e41745763533842454b4555342b7a5a41536b4c383034700a7664473043516b69447a696c4746597a6e45536644425042745049416957427052476c7376534d35324f4c69506562516d38557a6e505678773241594c6c5272795a643068715764715054470a2b664d4442734e4d4b525a2b62516f6d6c4b4b55344c716b61734b753162524e672f575a6f2b61564a7a6934492f4b43444f4b4f75704a776d736f6c53352f5932566c6a626478512b6769610a4c3355746e775a64365079412b335a4f597936594f30576a73496e6935755156785a5343415872532f6c617272385650796d55587755704e697855494155694761732b6748584c6850734f390a517933462f3731584147414a737a6e6a3059443572413836613471356767724646444f6c714749616658425471382b6a597153616671524c6a637941566d73515849336548506545476c67420a61547161746a2b704c4f3852414d48466d32464470345653394f535a46536a6d574b6e446a74722f567a4f4b4f63554d6938592f716f736f48382b644f4c683638416848514f4d444a416d7a0a726b4e634f4c657a74747a3257514550454947753638414d6b595270625767344e41496b4b415a4969714c476e535a484e386773474b4b71316338536b71664944694b344f7061636c4d4f310a7445537870474c4d65325633747766617066612f7441734d576a6a63485848312b6a36535975495466653567695762554e466543346e706b44724f776d4b4a612b6277486d554970706b476f0a636f70307142456253696d5947365964316a6467513067462f4b555434755541634b455a7749327277764d334433457861494c38574848365569696c5244765171766c54554333524c6370790a306778563959674c37676735324b4a456b4378465434716f6d6c6935397533457752316e4f4a536c706b5a4c4157424161677a586c734f3968736e78495a6e45764f754378366677587a576e0a464b5576706334464a4f61435a6e516c446d674f71664b4273415a46657733756b496a67615570586c476b335933363877577a6531526235505149416779596e356a506a632f2b36437a4a6e0a4565305778553158464373576c4e616a416a534a48702b5653483232795030713962594e393970437a786c316f53754b47755447324e7566382f6e50376a4865534c677352346558417342780a556f61556c595064456264333534676f693736673974486c4b615a594e4d4c697469334b5871316d446446554f616b4945564b4b324b46396a3568696269544a474233374e77636337686d440a67645478386b7466797a644544455a6a7548454e726a792b692b63532f6c79432f676943476a556142764f54656e417a785971474e6267693471516b714e346c51566172536b77774c2f51360a353874666d6b6557615668366172773841413435522f6e376e536462446f373261544b6b56472b37464e78365375316669546857764449395277577943456b57524d696a6b685368715850410a596b5a76696b7650733938353575613145653351567a496157456c50304948684d50484d4e3479624e79636e6a5a4a536a4f496541784750473164314f6a56556e4b5a78784b4e78476a4e420a5262433432636f5353796e4d3534576345744a30505057454d7a3247647267617a6342714144426f68735a304d754a72587a6d6d73306c4d68724c556e71424843697a315a6a4f49422f33740a4e5735646b6b5144584153585247394b3662774f555a336347446575482f444531345331555671692f6e767857746c6b4b43576e62524a5058736e6376724e504f346a4f54796c2b3067556d0a3564722b6a6f4d58725a5663416d7159564930476168494a526c6d706356634f2b4e70585a787766724e4f4f3745587a68715832765a71506957413848426d336e787679784a4e487a4c704a0a5449456b7172734563554258544f344f51684d70576d6c4b5466694c30626652647831393139466b342b617449353636736b34376947433571766e77366d527944726c3154424e50507272470a7a547533596861594571354f72375550534a3332434a67727173614a45615167513330707a48756c39344a4959715a3758486b3055753177794d70754831594a414a4552786d764b746163480a58486d30342b6265445653707845624a57556770537470464d35556b70436256426d71687146464b5a49496d4a576264684f7658433839634f55584f685a5258642f76774d67435157796a610a632b4e62462b6736343837654864713269546c426951616e752b4a416b32716355454f393050644b55634e6363544f36627335336e722f4f6f3138596365756d4d56727a5a586e50393679560a4b3058646862554e353176664b4a78716634786e6e337557336231445449537543775949314f47493076643938495661444d314c52784b6e3635516e6e6e6d616935757635706e4842347a470a74562f2b6678384161484f6936497a5066506f514a504746727a7a477254763770417a466c56494b302b6d4d36627a48444c71755a31344b376b4a474f4a684d75664c4e7131782f2f6862370a7434664d7074314b574e2f3357792b44546a426f37746f3438395454757a7a796e6774634f674f506666305a746a593275587a78444676626d777747625a7849424c656f474766396e4776580a623348723968366e4e6a64352b44555063753370435a4b4d6e464e566a7135327251774153595163786747633254476f466f627447706466645a366d79587a37326d3065662b5971613966580a57423833744c6b6c705554583930796d4d3662484d77614441512f6466356b7a5a7a5a5a333342736d746a6655345a6a5954533871787931465757434a6563435666586d30506651643835300a61706a4332624d4433766a326c6a613374494d684f2b6650737247787a763742495965544b62743752787a377641364668593378674163766e324d34484c4735736362362b68717a325a524c0a722b6834377764332b4f792f334f5a6754316b665a396f424e4733554947624c75635a4c41694436384b4859324a394530374e70653961336844662b39496974375a366665744d57353364610a7442756952576d626c6f30314a306e693750596d6c79383538336d686155423770326b7a34394749334361535a4e7963396255787a53447a43372f53384d4272573635647a547a356d484c6a0a7578302b476541434778765144714b6b74706551496e356f414554754b6b47504a6a436247704a37486e783177344d504e627a31625a633466333741785a31546a4564444a67664f3862526a0a706a334878306549434f3167794e5a67574955505374736f6253506b71683963414e7431496163644e41316e4e725a6f323559502f747735544a52627577667337585a3834664e376650334b0a6c476565634852504749347a362b736e617277663269702b73464a5549456c5131654d6a352f685932626d596550674e41393738794a6a58503379653078736a696d624b584e67394f47592b0a373145743948306668387431567768656a4e365651544d67686c77676c74436148646f3275727a524a5149744d537764446d4c36744c6d2b78766f346b7762476444726a79754e37665048660a442f6a7146326663757045596a595878756f52373146623853774a6749586433647737336e666e4d7548532f384d3533722f4f327432337a717376626941795948505963546e706d335377610a4842726a72326251344f4b6b4f723755586e456e57422b326f49483074652b5832685239776343637669756b7069466c367543306c736564307259746f31484c7876714930397472534a727a0a374c563950763976742f6e30703436342f6c315947795132546c584a2f6e3844785063465147726a596a49787073664f66612f492f4d78374e336a6e753835793464775773366b774f6577340a6e45366a636b74793074354f64597137694935397236533845464e554d33666965584f336e5a306b525731516a4e796d4f6c394a53426130567a444962535a55704f41693946315978366e4e0a4d616533317467343556782f2f70422f2b73666e2b4d796e6a6e6a754f7179764a635962636a4a6e2f41454178415a4c63665a334378746269586639374472762b2b414f4633644f303830530a4233737a6a75637a4a50754a414b4a7046706361493242586f31636c355a444a536656745530504e615272424e41716c30426c476553744e416a4e53586c68486c4d755346732b44743558650a61504b4c5a584c714d4d774e353839764d466f5862743763352b2f2b2b6961662f6f634a6b304e6a6137754a377a56655a4134764169416c4f4a34617878506a345a395934324f2f657062580a766534636c41473364342b5a6454315a4243565547795477597148627255314d64344655612f6f55427130616a56494931566654784546652b427767353544486c6d4c684b677452524736710a554d4b71746a682b7069513144526f69304e6539724931476e4e34614d42775a6a7a39356d302f3832533650665758472b4a5177586b73763468416e4149674973356b78507a592b2f5046740a33762b426335772b7463332b6e59355a4e36385658565630574a53797163366c315130786955304375516c7867796d317578734273476b54566f656a59536b525943576c6b452f59597459660a4d6c6c70774b734f79466e3048394d4a384843334d6d367264585257454173353573623669444e6e427577664866444a76376e44583335696c2b456f4d527a656462316d635868565a334c590a382b752f63593650665051425a6b655a4f37666d7a4574664652704e624e7964334353534a38797165714e655a434e4e4644746d43426c623648327a784c54582f4f544757326c67494366460a6b546c49637471636759525a69546c684656513351545644652b41704242634a4267733246445a4d5474426b515a49776e78647533584c5731376634324d664844456677353339366d375a740a79446c6951724d772f634e39342b4533725047686a3779532b58484477663473617668473843496b67647a6b75386f747a376758636b366b51594e587a592f696d41747454676943314d68750a6c6a42676b424f30625a3045515638684765515856447675574172614f306f35767447724335466f5252674f323941694368524a6d42744e546c564545645967596d68524a676454594d44370a503744446c3738303452745865725a4f5a315158524368466a72393458326151472b34633947466d33744349774d427241384e77792b6a69792f494163555649394c5651615a756d61762b460a684b44466b4362523575707a6455356f4e61674e307775656532694f3269594f526e57494d42366a6252716b45564a565662735953767970485a3550564b4e465132505974693365684d4c6b0a634c2f6e7a4537693471584d66337970592b763043317841652b66386859597a32794e75504438446d6a68414a534e686f6c473552654375756a33334b6e65746d79422b4a796c56695273300a62585236542f354b684a433574316e75366f54727a55735332766275454e53715654564e2b48515349586c596b3653774a716357595553625043576862584b49615751524a4250534f7275370a5061653352357a663657746367763843564b70724572377461444541414141415355564f524b35435949493d0a	\N	f	\N	5	always	\N	f	\N	\N	\N	\N	0	\N	\N	1	\N	\N	\N	open	\N	\N	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
3	Administrator	1	\N	\N	2015-02-02 07:30:03.31094	0	\N	f	t	\N	f	\N	\N	\N	\N	\N	\N	f	contact	admin@example.com	\N	\N	en_US	\N	\N	\N	\N	\N	2015-02-02 07:30:52.897364	\N	\N	1	Administrator	f	1	\N	\N	\N	\N	\N	f	\N	3	none	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N	1	1	open	\N	\N	\N	\N	\N	\N	\N	t	\N	\N	0.0	0.0	0	\N	\N	\N	\N	\N	\N
\.


--
-- TOC entry 4638 (class 2606 OID 152418)
-- Dependencies: 197 197
-- Name: res_partner_pkey; Type: CONSTRAINT; Schema: public; Owner: openerp; Tablespace: 
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_pkey PRIMARY KEY (id);


--
-- TOC entry 4628 (class 1259 OID 164279)
-- Dependencies: 3797 197
-- Name: path_gist_idx; Type: INDEX; Schema: public; Owner: openerp; Tablespace: 
--

CREATE INDEX path_gist_idx ON res_partner USING gist (path_ltree);


--
-- TOC entry 4629 (class 1259 OID 173746)
-- Dependencies: 197
-- Name: res_partner_activation_index; Type: INDEX; Schema: public; Owner: openerp; Tablespace: 
--

CREATE INDEX res_partner_activation_index ON res_partner USING btree (activation);


--
-- TOC entry 4630 (class 1259 OID 153094)
-- Dependencies: 197
-- Name: res_partner_company_id_index; Type: INDEX; Schema: public; Owner: openerp; Tablespace: 
--

CREATE INDEX res_partner_company_id_index ON res_partner USING btree (company_id);


--
-- TOC entry 4631 (class 1259 OID 153096)
-- Dependencies: 197
-- Name: res_partner_date_index; Type: INDEX; Schema: public; Owner: openerp; Tablespace: 
--

CREATE INDEX res_partner_date_index ON res_partner USING btree (date);


--
-- TOC entry 4632 (class 1259 OID 153097)
-- Dependencies: 197
-- Name: res_partner_display_name_index; Type: INDEX; Schema: public; Owner: openerp; Tablespace: 
--

CREATE INDEX res_partner_display_name_index ON res_partner USING btree (display_name);


--
-- TOC entry 4633 (class 1259 OID 153098)
-- Dependencies: 197
-- Name: res_partner_name_index; Type: INDEX; Schema: public; Owner: openerp; Tablespace: 
--

CREATE INDEX res_partner_name_index ON res_partner USING btree (name);


--
-- TOC entry 4634 (class 1259 OID 153095)
-- Dependencies: 197
-- Name: res_partner_parent_id_index; Type: INDEX; Schema: public; Owner: openerp; Tablespace: 
--

CREATE INDEX res_partner_parent_id_index ON res_partner USING btree (parent_id);


--
-- TOC entry 4635 (class 1259 OID 164241)
-- Dependencies: 197
-- Name: res_partner_parent_left_index; Type: INDEX; Schema: public; Owner: openerp; Tablespace: 
--

CREATE INDEX res_partner_parent_left_index ON res_partner USING btree (parent_left);


--
-- TOC entry 4636 (class 1259 OID 164242)
-- Dependencies: 197
-- Name: res_partner_parent_right_index; Type: INDEX; Schema: public; Owner: openerp; Tablespace: 
--

CREATE INDEX res_partner_parent_right_index ON res_partner USING btree (parent_right);


--
-- TOC entry 4639 (class 1259 OID 153099)
-- Dependencies: 197
-- Name: res_partner_ref_index; Type: INDEX; Schema: public; Owner: openerp; Tablespace: 
--

CREATE INDEX res_partner_ref_index ON res_partner USING btree (ref);


--
-- TOC entry 4641 (class 2606 OID 173814)
-- Dependencies: 977 197
-- Name: res_partner_activation_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_activation_fkey FOREIGN KEY (activation) REFERENCES res_partner_activation(id) ON DELETE SET NULL;


--
-- TOC entry 4640 (class 2606 OID 173819)
-- Dependencies: 4637 197 197
-- Name: res_partner_assigned_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_assigned_partner_id_fkey FOREIGN KEY (assigned_partner_id) REFERENCES res_partner(id) ON DELETE SET NULL;


--
-- TOC entry 4651 (class 2606 OID 154242)
-- Dependencies: 4637 197 197
-- Name: res_partner_commercial_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_commercial_partner_id_fkey FOREIGN KEY (commercial_partner_id) REFERENCES res_partner(id) ON DELETE SET NULL;


--
-- TOC entry 4650 (class 2606 OID 154247)
-- Dependencies: 195 197
-- Name: res_partner_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_company_id_fkey FOREIGN KEY (company_id) REFERENCES res_company(id) ON DELETE SET NULL;


--
-- TOC entry 4649 (class 2606 OID 154252)
-- Dependencies: 282 197
-- Name: res_partner_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_country_id_fkey FOREIGN KEY (country_id) REFERENCES res_country(id) ON DELETE RESTRICT;


--
-- TOC entry 4652 (class 2606 OID 154237)
-- Dependencies: 177 197
-- Name: res_partner_create_uid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_create_uid_fkey FOREIGN KEY (create_uid) REFERENCES res_users(id) ON DELETE SET NULL;


--
-- TOC entry 4642 (class 2606 OID 173809)
-- Dependencies: 975 197
-- Name: res_partner_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES res_partner_grade(id) ON DELETE SET NULL;


--
-- TOC entry 4645 (class 2606 OID 154272)
-- Dependencies: 4637 197 197
-- Name: res_partner_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES res_partner(id) ON DELETE SET NULL;


--
-- TOC entry 4644 (class 2606 OID 161288)
-- Dependencies: 739 197
-- Name: res_partner_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_section_id_fkey FOREIGN KEY (section_id) REFERENCES crm_case_section(id) ON DELETE SET NULL;


--
-- TOC entry 4643 (class 2606 OID 162118)
-- Dependencies: 4637 197 197
-- Name: res_partner_sponsor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_sponsor_id_fkey FOREIGN KEY (sponsor_id) REFERENCES res_partner(id) ON DELETE SET NULL;


--
-- TOC entry 4648 (class 2606 OID 154257)
-- Dependencies: 287 197
-- Name: res_partner_state_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_state_id_fkey FOREIGN KEY (state_id) REFERENCES res_country_state(id) ON DELETE RESTRICT;


--
-- TOC entry 4646 (class 2606 OID 154267)
-- Dependencies: 292 197
-- Name: res_partner_title_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_title_fkey FOREIGN KEY (title) REFERENCES res_partner_title(id) ON DELETE SET NULL;


--
-- TOC entry 4653 (class 2606 OID 154232)
-- Dependencies: 177 197
-- Name: res_partner_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_user_id_fkey FOREIGN KEY (user_id) REFERENCES res_users(id) ON DELETE SET NULL;


--
-- TOC entry 4647 (class 2606 OID 154262)
-- Dependencies: 177 197
-- Name: res_partner_write_uid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openerp
--

ALTER TABLE ONLY res_partner
    ADD CONSTRAINT res_partner_write_uid_fkey FOREIGN KEY (write_uid) REFERENCES res_users(id) ON DELETE SET NULL;


-- Completed on 2015-02-09 10:05:23 WIB

--
-- PostgreSQL database dump complete
--

