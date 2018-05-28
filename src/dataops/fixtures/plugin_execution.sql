--
-- PostgreSQL database dump
--

-- Dumped from database version 10.3
-- Dumped by pg_dump version 10.3

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
-- Name: __ONTASK_WORKFLOW_TABLE_35; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_35" (
    email text,
    "student id" bigint,
    "A1" bigint,
    "A2" bigint
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_35; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_35" (email, "student id", "A1", "A2") FROM stdin;
fake_addess1@bogus_email.com	111	0	1
fake_addess3@bogus_email.com	333	1	1
fake_addess2@bogus_email.com	222	1	0
\.


--
-- PostgreSQL database dump complete
--

