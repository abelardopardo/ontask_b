--
-- PostgreSQL database dump
--

-- Dumped from database version 11.2
-- Dumped by pg_dump version 11.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: __ONTASK_WORKFLOW_TABLE_1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_1" (
    sid bigint,
    name text,
    email text,
    "!#$%&()*+,-./\:;<=>?@[]^_`{|}~ 1" double precision,
    registered boolean,
    "when" timestamp with time zone
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_1; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_1" (sid, name, email, "!#$%&()*+,-./\:;<=>?@[]^_`{|}~ 1", registered, "when") FROM stdin;
1	Carmelo Coton	student1@bogus.com	12	t	2017-10-11 11:03:44+10:30
2	Carmelo Coton	student2@bogus.com	12.0999999999999996	f	2017-10-11 11:02:44+10:30
3	Carmelo Coton2	student3@bogus.com	13.1999999999999993	t	2017-10-11 11:02:44+10:30
\.


--
-- PostgreSQL database dump complete
--

