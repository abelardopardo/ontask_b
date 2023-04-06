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
-- Name: __ONTASK_WORKFLOW_TABLE_2; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_2" (
    "SID" bigint,
    email text,
    "Structure" text,
    "Presentation" text
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_2; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_2" ("SID", email, "Structure", "Presentation") FROM stdin;
333306652	qvrr9413@bogus.com	Medium	High
319549896	ttqp9766@bogus.com	Poor	High
396913155	pzaz8370@bogus.com	High	High
352120481	ucdx8510@bogus.com	High	Medium
363393232	tdrv2640@bogus.com	High	Medium
326285587	isim6886@bogus.com	High	Medium
384087855	kjbc6748@bogus.com	Medium	Medium
300773633	euhz6532@bogus.com	High	High
317547296	ckrn7263@bogus.com	High	High
388963652	tcnf7608@bogus.com	High	High
315500979	zqdk2609@bogus.com	High	High
330794979	olie8242@bogus.com	Medium	Poor
394589352	ctfh9946@bogus.com	High	Medium
320250819	tjxk6150@bogus.com	High	High
360594548	euho9752@bogus.com	Poor	High
\.


--
-- PostgreSQL database dump complete
--

