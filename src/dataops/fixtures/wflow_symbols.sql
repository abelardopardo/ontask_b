--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.3
-- Dumped by pg_dump version 9.6.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: __ONTASK_WORKFLOW_TABLE_149; Type: TABLE; Schema: public; Owner: ontask
--

CREATE TABLE "__ONTASK_WORKFLOW_TABLE_149" (
    email text,
    sid bigint,
    age double precision,
    name text,
    registered boolean,
    "when" timestamp without time zone
);


ALTER TABLE "__ONTASK_WORKFLOW_TABLE_149" OWNER TO ontask;

--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_149; Type: TABLE DATA; Schema: public; Owner: ontask
--

COPY "__ONTASK_WORKFLOW_TABLE_149" (email, sid, age, name, registered, "when") FROM stdin;
student1@bogus.com	1	12	Carmelo Coton	t	2017-10-11 00:33:44
student2@bogus.com	2	12.0999999999999996	Carmelo Coton	f	2017-10-11 00:32:44
student3@bogus.com	3	13.1999999999999993	Carmelo Coton22	t	2017-10-11 00:32:44
\.


--
-- PostgreSQL database dump complete
--

