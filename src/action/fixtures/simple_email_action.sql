--
-- PostgreSQL database dump
--

-- Dumped from database version 10.4
-- Dumped by pg_dump version 10.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
-- SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: __ONTASK_WORKFLOW_TABLE_5; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_5" (
    age double precision,
    email text,
    sid bigint,
    "EmailRead_1" bigint,
    another text,
    name text,
    one text,
    registered boolean,
    "when" timestamp without time zone
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_5; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_5" (age, email, sid, "EmailRead_1", another, name, one, registered, "when") FROM stdin;
12	student01@bogus.com	1	0	bbb	Carmelo Coton	aaa	t	2017-10-11 00:33:44
12.0999999999999996	student02@bogus.com	2	0	aaa	Carmelo Coton	bbb	f	2017-10-11 00:32:44
13.1999999999999993	student03@bogus.com	3	0	bbb	Carmelo Coton2	aaa	t	2017-10-11 00:32:44
\.


--
-- PostgreSQL database dump complete
--

