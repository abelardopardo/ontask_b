--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2
-- Dumped by pg_dump version 12.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: __ONTASK_WORKFLOW_TABLE_108; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_108" (
    age double precision,
    email text,
    sid bigint,
    name text,
    registered boolean,
    "when" timestamp with time zone
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_108; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_108" (age, email, sid, name, registered, "when") FROM stdin;
12	student01@bogus.com	1	Student One	t	2017-10-10 13:33:44+10:30
12.1	student02@bogus.com	2	Student Two	f	2017-10-10 11:02:44+10:30
13.2	student03@bogus.com	3	Student Three	t	2017-10-10 11:02:44+10:30
\.


--
-- PostgreSQL database dump complete
--

