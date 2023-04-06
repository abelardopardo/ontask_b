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
-- Name: __ONTASK_WORKFLOW_TABLE_5; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_5" (
    age double precision,
    email text,
    sid bigint,
    another text,
    name text,
    one text,
    registered boolean,
    "when" timestamp with time zone
);


--
-- Name: __ONTASK_WORKFLOW_TABLE_6; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_6" (
    sid bigint,
    name text,
    email text,
    age double precision,
    registered boolean,
    "when" timestamp with time zone
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_5; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_5" (age, email, sid, another, name, one, registered, "when") FROM stdin;
12	student01@bogus.com	1	bbb	Carmelo Coton	aaa	t	2017-10-10 22:03:44+10:30
12.1	student02@bogus.com	2	aaa	Carmelo Coton	bbb	f	2017-10-10 22:02:44+10:30
13.2	student03@bogus.com	3	bbb	Carmelo Coton2	aaa	t	2017-10-10 22:02:44+10:30
\.


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_6; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_6" (sid, name, email, age, registered, "when") FROM stdin;
1	Carmelo Coton	student1@bogus.com	12	t	2017-10-11 11:03:44+10:30
2	Carmelo Coton	student2@bogus.com	12.1	f	2017-10-11 11:02:44+10:30
3	Carmelo Coton2	student3@bogus.com	13.2	t	2017-10-11 11:02:44+10:30
\.


--
-- PostgreSQL database dump complete
--

