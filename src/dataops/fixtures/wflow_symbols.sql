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
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: __ONTASK_WORKFLOW_TABLE_149; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_149" (
    email text,
    sid bigint,
    age double precision,
    name text,
    registered boolean,
    "when" timestamp without time zone
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_149; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_149" (email, sid, age, name, registered, "when") FROM stdin;
student01@bogus.com	1	12	Carmelo Coton	t	2017-10-11 00:33:44
student02@bogus.com	2	12.0999999999999996	Carmelo Coton	f	2017-10-11 00:32:44
student03@bogus.com	3	13.1999999999999993	Carmelo Coton22	t	2017-10-11 00:32:44
\.


--
-- PostgreSQL database dump complete
--

