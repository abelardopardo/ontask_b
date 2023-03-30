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
-- Name: __ONTASK_WORKFLOW_TABLE_1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_1" (
    key double precision,
    text1 text,
    text2 text,
    double1 double precision,
    double2 double precision,
    bool1 text,
    bool2 text,
    date1 timestamp with time zone,
    date2 timestamp with time zone
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_1; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_1" (key, text1, text2, double1, double2, bool1, bool2, date1, date2) FROM stdin;
1	d1_t1_1	\N	111	\N	true	\N	2018-01-01 01:00:00+10:30	\N
2	d2_t1_2	\N	112	\N	false	\N	2018-01-01 02:00:00+10:30	\N
3	\N	d1_t2_3	\N	123	\N	false	\N	2018-01-02 03:00:00+10:30
4	\N	d1_t2_4	\N	124	\N	true	\N	2018-01-02 04:00:00+10:30
5	d1_t1_5	\N	115	\N	false	\N	2018-01-01 05:00:00+10:30	\N
6	d1_t1_6	\N	116	\N	true	\N	2018-01-01 06:00:00+10:30	\N
7	\N	d1_t2_7	\N	126	\N	true	\N	2018-01-02 07:00:00+10:30
8	\N	d1_t2_8	\N	127	\N	false	\N	2018-01-02 08:00:00+10:30
\.


--
-- PostgreSQL database dump complete
--

