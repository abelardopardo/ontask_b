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
-- Name: __ONTASK_WORKFLOW_TABLE_112; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."__ONTASK_WORKFLOW_TABLE_112" (
    c0 bigint,
    c1 bigint,
    c2 bigint,
    c3 bigint,
    c4 bigint,
    c5 bigint,
    c6 bigint,
    c7 bigint,
    c8 bigint,
    c9 bigint,
    c91 boolean,
    c92 boolean
);


--
-- Data for Name: __ONTASK_WORKFLOW_TABLE_112; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."__ONTASK_WORKFLOW_TABLE_112" (c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c91, c92) FROM stdin;
0	9	1	2	8	3	0	8	0	8	t	f
1	0	5	7	1	5	9	7	0	7	t	f
2	0	1	2	3	8	3	9	0	2	f	f
3	1	8	2	4	9	5	9	3	6	f	t
4	2	3	5	1	8	0	2	3	8	f	t
5	7	1	4	1	0	8	1	6	0	f	f
6	2	9	4	0	4	7	8	5	6	f	t
7	0	9	0	2	4	4	5	7	8	f	t
8	5	5	3	9	9	8	5	9	1	f	f
9	0	8	6	9	5	5	6	6	3	t	f
10	7	2	5	7	1	1	2	8	3	t	t
11	4	9	7	5	4	7	1	9	8	t	t
12	1	1	0	0	7	0	1	1	9	f	t
13	0	8	5	8	6	6	7	8	5	f	f
14	9	4	1	6	4	7	1	6	8	f	t
15	1	4	9	2	3	3	3	8	2	f	f
16	8	2	5	6	0	4	1	2	3	t	t
17	8	7	1	6	0	2	8	0	9	f	t
18	8	1	0	2	5	0	0	2	4	t	f
19	0	4	2	8	0	5	7	1	8	f	f
20	6	0	8	5	3	2	9	9	2	t	t
21	1	2	8	2	6	6	5	1	6	f	t
22	7	0	8	9	9	7	0	9	6	f	t
23	3	7	2	3	6	9	1	3	9	t	f
24	5	8	9	9	8	0	1	2	9	f	t
25	5	7	3	4	4	4	8	7	3	f	f
26	0	6	6	1	6	0	2	7	1	f	t
27	3	0	8	0	3	7	8	6	9	t	t
28	4	1	2	3	1	5	9	8	0	t	t
29	9	4	9	8	3	9	1	8	6	t	t
30	1	2	7	4	5	0	9	7	9	f	t
31	5	2	7	1	2	9	9	6	2	f	f
32	8	2	9	2	7	1	1	1	1	f	t
33	8	0	6	1	6	7	1	5	8	t	t
34	4	8	2	0	5	8	4	4	1	t	t
35	8	7	7	8	6	1	5	9	8	f	f
36	0	2	6	8	1	4	5	2	0	t	f
37	4	5	0	1	9	2	7	2	9	f	f
38	6	2	3	4	7	1	6	5	0	f	t
39	8	1	3	7	1	9	7	9	6	f	f
40	1	0	2	2	4	1	0	7	8	f	f
41	3	0	6	0	2	7	0	7	3	t	f
42	3	2	0	3	6	2	7	5	4	f	t
43	5	9	5	1	2	6	4	8	9	t	t
44	6	7	2	3	5	7	4	2	1	t	f
45	6	4	7	6	2	8	0	1	9	f	f
46	1	8	5	1	6	1	5	6	4	t	t
47	7	4	9	8	7	5	0	7	9	t	t
48	6	2	0	1	1	7	8	1	8	t	t
49	7	4	5	9	2	3	9	1	7	t	f
50	5	8	1	3	5	2	9	0	9	f	f
51	2	5	8	8	0	8	2	1	1	f	f
52	3	4	2	5	0	2	6	0	4	t	t
53	9	1	2	7	2	3	4	3	2	f	f
54	2	2	9	0	1	8	3	0	1	f	f
55	1	9	9	2	1	5	2	4	5	f	f
56	5	3	8	6	5	2	6	7	5	f	t
57	2	7	6	5	2	6	4	4	1	t	t
58	9	8	1	8	7	6	5	6	2	t	t
59	0	2	4	4	4	6	9	8	8	f	t
60	4	7	3	9	3	4	1	1	1	f	t
61	4	4	5	5	7	5	1	5	3	f	t
62	5	3	6	9	1	2	2	9	6	t	f
63	9	5	6	5	4	8	9	2	4	t	t
64	2	3	3	7	7	6	3	0	8	t	f
65	6	9	1	6	5	4	4	8	9	f	t
66	8	4	5	5	9	7	6	6	7	f	f
67	5	8	4	5	9	5	7	1	1	t	f
68	3	4	1	8	2	2	3	0	5	t	f
69	0	8	9	7	0	5	7	7	7	t	t
70	9	1	6	6	7	4	2	1	7	t	t
71	7	4	3	4	2	3	0	8	3	t	f
72	2	3	4	7	5	3	0	7	6	f	t
73	0	4	7	6	0	1	9	5	6	t	t
74	0	0	3	5	4	2	2	4	2	f	t
75	7	1	2	3	7	8	0	7	9	t	f
76	8	9	0	6	0	6	3	7	8	f	t
77	9	8	0	6	5	7	7	4	8	t	t
78	8	8	1	5	5	0	3	8	9	f	f
79	0	3	3	2	5	5	2	7	4	t	f
80	6	4	8	3	8	2	4	0	9	t	t
81	5	9	2	4	6	0	1	4	4	f	t
82	2	9	8	7	8	9	4	1	1	f	t
83	1	5	1	9	1	6	3	0	5	t	t
84	5	7	1	9	5	4	0	7	2	t	f
85	4	0	1	6	0	0	4	0	0	f	t
86	5	9	3	8	0	2	9	5	2	f	t
87	9	7	2	8	9	1	6	2	6	f	t
88	5	7	8	1	8	5	3	3	6	f	t
89	3	4	1	9	8	1	5	9	6	t	t
90	2	3	3	0	5	8	8	0	7	f	f
91	7	4	3	3	3	3	5	9	7	f	f
92	6	0	7	1	2	1	0	7	8	t	t
93	6	5	2	0	9	1	3	9	0	f	t
94	3	3	8	2	4	9	0	8	8	f	t
95	6	9	2	7	4	5	7	0	3	t	f
96	4	0	3	3	8	9	6	3	0	t	f
97	2	3	8	2	1	0	8	9	6	t	t
98	8	0	4	6	1	4	6	3	2	f	t
99	8	5	0	0	1	8	6	8	0	f	t
\.


--
-- PostgreSQL database dump complete
--

