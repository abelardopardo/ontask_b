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
-- Name: __ONTASK_WORKFLOW_TABLE_149; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_149" (
    email text,
    sid bigint,
    age double precision,
    name text,
    registered boolean,
    "when" timestamp with time zone
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_149; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_149" (email, sid, age, name, registered, "when") FROM stdin;
student01@bogus.com	1	12	Carmelo Coton	t	2017-10-10 22:03:44+10:30
student02@bogus.com	2	12.1	Carmelo Coton	f	2017-10-10 22:02:44+10:30
student03@bogus.com	3	13.2	Carmelo Coton22	t	2017-10-10 22:02:44+10:30
\.


--
-- PostgreSQL database dump complete
--

