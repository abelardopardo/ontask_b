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
    sid bigint,
    name text,
    email text,
    "Tutorial activity" text,
    "Presentation" text
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_1; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_1" (sid, name, email, "Tutorial activity", "Presentation") FROM stdin;
1	User One	student1@bogus.com	\N	\N
2	User Two	student2@bogus.com	\N	\N
3	User Three	student3@bogus.com	\N	\N
4	User Four	student4@bogus.com	\N	\N
5	User Five	student5@bogus.com	\N	\N
6	User Six	student6@bogus.com	\N	\N
7	User Seven	student7@bogus.com	\N	\N
8	User Eight	student8@bogus.com	\N	\N
9	User Nine	student9@bogus.com	\N	\N
10	User Ten	student10@bogus.com	\N	\N
11	User Eleven	student11@bogus.com	\N	\N
12	User Twelve	student12@bogus.com	\N	\N
\.


--
-- PostgreSQL database dump complete
--

