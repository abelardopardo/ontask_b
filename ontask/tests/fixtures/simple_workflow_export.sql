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
-- Name: __ONTASK_WORKFLOW_TABLE_140; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_140" (
    email text,
    sid bigint,
    "WAM" double precision,
    credits bigint,
    days_online double precision,
    difficult_week01 text,
    difficult_week02 text,
    first_name text,
    first_session timestamp with time zone,
    gender text,
    "group" text,
    induction boolean,
    last_name text,
    mt_total double precision,
    q01 bigint,
    q02 bigint,
    q03 bigint,
    q04 bigint,
    q05 bigint,
    q06 bigint,
    q07 bigint,
    q08 bigint,
    q09 bigint,
    q10 bigint,
    took_mt boolean,
    video_1 bigint,
    video_2 bigint,
    video_3 bigint
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_140; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_140" (email, sid, "WAM", credits, days_online, difficult_week01, difficult_week02, first_name, first_session, gender, "group", induction, last_name, mt_total, q01, q02, q03, q04, q05, q06, q07, q08, q09, q10, took_mt, video_1, video_2, video_3) FROM stdin;
ydtd7245@bogus.com	322843525	60.2	120	2			Alica	2017-08-01 08:30:00+09:30	female	GR01	t	Aarons	6	1	1	1	0	0	1	0	0	1	1	t	1	1	0
sufd4890@bogus.com	353424637	55.2	124	6			Cai	2017-08-01 08:30:00+09:30	female	GR03	t	Chia	5	1	1	0	1	0	0	1	0	0	1	t	1	0	0
mqjf6366@bogus.com	353125038	77.2	124	9			Sean	2017-08-08 08:30:00+09:30	male	GR04	f	De Gruchy	0	0	0	0	0	0	0	0	0	0	0	f	0	1	0
zvza6671@bogus.com	306222554	75.2	128	0			Cui	2017-08-08 08:30:00+09:30	female	GR01	t	Hao	5	1	0	1	0	0	1	0	0	1	1	t	0	0	1
axem6505@bogus.com	386061509	71.2	120	0			Zhi	2017-08-01 08:30:00+09:30	female	GR02	t	Hung	6	0	0	0	0	1	1	1	1	1	1	t	1	1	1
nkxm1160@bogus.com	340893132	88.2	124	3			Yue You	2017-08-08 08:30:00+09:30	female	GR03	f	Liang	5	1	0	1	0	0	0	1	1	1	0	t	0	0	0
zyjt4743@bogus.com	306187565	54.2	120	\N			Daniel	2017-08-01 08:30:00+09:30	male	GR03	t	Rechner	\N	0	0	0	0	0	0	0	0	0	0	f	1	1	0
bemm5981@bogus.com	302221812	51.2	124	1			Aaron	2017-08-08 08:30:00+09:30	male	GR04	t	Moses	4	1	0	0	1	1	1	0	0	0	0	t	0	1	0
pzrg4784@bogus.com	366888585	62.2	128	7			Wen	2017-08-01 08:30:00+09:30	male	GR03	t	Wan	5	1	1	0	0	0	1	1	1	0	0	t	1	0	0
wtnq9773@bogus.com	303746256	63.2	122	8			Shi	2017-08-08 08:30:00+09:30	male	GR02	f	Tang	3	0	0	0	0	1	0	0	1	0	1	t	1	1	0
glpm2733@bogus.com	301871719	77.2	120	6			Dong	2017-08-08 08:30:00+09:30	male	GR03	t	Yuan	4	0	1	0	1	1	0	1	0	0	0	t	1	0	1
kmgo5805@bogus.com	341018836	88.2	124	2			Leah	2017-08-01 08:30:00+09:30	female	GR04	f	Zeal	6	1	1	1	0	0	1	1	0	0	1	t	1	1	1
\.


--
-- PostgreSQL database dump complete
--

