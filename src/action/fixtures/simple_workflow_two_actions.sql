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
-- Name: __ONTASK_WORKFLOW_TABLE_108; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_108" (
    age double precision,
    email text,
    sid bigint,
    name text,
    registered boolean,
    "when" timestamp without time zone
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_108; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_108" (age, email, sid, name, registered, "when") FROM stdin;
12	student1@bogus.com	1	Student One	t	2017-10-10 13:33:44
12.0999999999999996	student2@bogus.com	2	Student Two	f	2017-10-10 13:32:44
13.1999999999999993	student3@bogus.com	3	Student Three	t	2017-10-10 13:32:44
\.


--
-- PostgreSQL database dump complete
--

