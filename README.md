# The Unofficial Guide — Project 1

---

## Domain

**Santa Clara University (SCU) Student Survival Guide** — professor reviews, campus dining, housing, and campus life from the student perspective.

SCU's official channels (course catalogs, housing guides, the university website) describe what exists but not what it's actually like. The real knowledge lives in Rate My Professors reviews, student newspaper articles, dorm ranking sites, and food allergy community guides — scattered across a dozen sources that students have to hunt down individually. A student asking "Which professor is best for the ENG1A requirement?" or "How do dining points actually work?" needs to cross-reference six different websites to get a complete answer. This system makes that informal, student-generated knowledge searchable in one place.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors — Stephen Carroll (English) | Student reviews | https://www.ratemyprofessors.com/professor/406086 |
| 2 | Rate My Professors — David Keaton (English) | Student reviews | https://www.ratemyprofessors.com/professor/2045818 |
| 3 | Rate My Professors — Sumana Sur (OMIS) | Student reviews | https://www.ratemyprofessors.com/professor/125677 |
| 4 | Rate My Professors — Ye Cai (Finance) | Student reviews | https://www.ratemyprofessors.com/professor/1589515 |
| 5 | Rate My Professors — Sina Heydari (Mechanical Engineering) | Student reviews | https://www.ratemyprofessors.com/professor/2978478 |
| 6 | Rate My Professors — Tony Nguyen (Finance) | Student reviews | https://www.ratemyprofessors.com/professor/726495 |
| 7 | Rate My Professors — Kirk Glaser (Creative Writing) | Student reviews | https://www.ratemyprofessors.com/professor/664664 |
| 8 | Rate My Professors — Lawrence Nelson (Philosophy) | Student reviews | https://www.ratemyprofessors.com/professor/13997 |
| 9 | The Santa Clara — Top 10 Professors | Student newspaper article | https://www.thesantaclara.org/blog/top-10-santa-clara-professors |
| 10 | The Santa Clara — Food Insecurity Article | Student newspaper article | https://www.thesantaclara.org/blog/food-insecurity-remains-a-continual-challenge-at-santa-clara-university |
| 11 | SCU Official Dining Services | University webpage | https://www.scu.edu/auxiliary-services/dining-services/ |
| 12 | SCU Official Dining Plans 2025-26 | University webpage | https://www.scu.edu/auxiliary-services/dining-services/dining-plans/ |
| 13 | RateMyDorm — SCU Freshman Dorms Ranked | Dorm review site | https://www.ratemydorm.com/freshman-dorms-ranked/santa-clara-university |
| 14 | Princeton Review — SCU Profile | College review platform | https://www.princetonreview.com/college/santa-clara-university-1023579 |
| 15 | Appily — SCU Student Reviews | College review platform | https://www.appily.com/colleges/santa-clara-university/reviews |
| 16 | Spokin Campus Guide — SCU Food Allergy Info | Food allergy community guide | https://www.spokin.com/food-allergy-friendly-campus-guide-santa-clara-university |
| 17 | CollegeVine — SCU Campus Life FAQ | College advising platform | https://www.collegevine.com/faq/127434/campus-life-at-santa-clara-university-what-s-it-like |

---

## Document Ingestion Pipeline

Documents were collected as plain `.txt` files by fetching content from Rate My Professors, SCU's student newspaper, official university pages, and college review platforms. Each file follows a consistent structure: a `SOURCE:` line, a `URL:` line, then the substantive content.

The ingestion pipeline (`ingest.py`) runs three steps:

1. **Load** — reads every `.txt` file in `documents/` using Python's `pathlib`
2. **Clean** — strips the `SOURCE:` and `URL:` header lines from each file (metadata that would pollute embeddings), then collapses runs of 3+ blank lines into two to normalize whitespace
3. **Chunk** — splits the cleaned text into overlapping character-level chunks and attaches the source filename as metadata to each chunk

The output is a list of dicts: `{"text": str, "source": str, "chunk_index": int}`, ready to be embedded in Milestone 4.

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 80 characters

**Why these choices fit your documents:**
The corpus is mostly short, opinion-based review text (1–5 sentences per review) mixed with structured factual content (dining plans, dorm descriptions). A 400-character chunk captures 2–4 sentences — enough to hold a complete student opinion or a single factual claim (e.g., "Professor X's exams are curved and focus on lecture slides") without merging unrelated reviews together. Longer chunks would blend multiple opinions about different aspects of a professor into one embedding, making it harder to match specific queries.

The 80-character overlap (~20% of chunk size) prevents key information from being lost at chunk boundaries. If a review mentions a professor's exam policy in the last sentence of one chunk and elaborates in the next, either chunk remains retrievable. Paragraph-based splitting was considered but rejected because document formatting is inconsistent — some sources use line breaks, others use run-on prose — making fixed-size chunking with overlap more reliable.

**Preprocessing:** The ingestion pipeline strips `SOURCE:` and `URL:` header lines from the top of each document and collapses runs of 3+ blank lines into two, removing document metadata that would pollute embeddings without contributing semantic content.

**Sample chunks:**

> **[1] source: rmp_ye_cai.txt, chunk 0**
> `Rating: 5.0/5 | Difficulty: 2.4/5 | Would Take Again: 100% REVIEW 1 (FNCE121, Dec 14, 2024) — Quality 5, Difficulty 3, Grade B: "Cai is an amazing professor. She goes at a perfect pace for you to understand the material. Homework is on Connect and is very similar to problems done in class. No group projects! Midterms/Final are definitely more challenging but it's doable. She allows cheat sheet for them too."`

> **[2] source: scu_dorms_ratemydorm.txt, chunk 0**
> `96% of SCU freshmen live on campus. Here is how freshman dorms rank based on student reviews: #1 CAMPISI HALL (Rating: 3.9/5, 3 reviews) - Ideal for students who prefer quiet study environments - Positioned near the library and gym — convenient for academics`

> **[3] source: scu_dining_plans.txt, chunk 0**
> `HOW DINING POINTS WORK: 1 dining point = $1. There are no "meal swipes" — all purchases deduct points from your balance. This means no wasted swipes for missed meals, but you must budget carefully because points can run out.`

> **[4] source: rmp_lawrence_nelson.txt, chunk 3**
> `"DO NOT TAKE THIS PROFESSOR. I signed up for this class seeing all these positive reviews but i was extremely wrong. While the material is interesting, Professor Nelson is an extremely unreasonable grader. He is harsh and unclear with the criteria for content." Tags: Tough grader, Lots of homework, Test heavy`

> **[5] source: scu_campus_life_collegevine.txt, chunk 7**
> `Top employers: Amazon, Microsoft, Google. Notable alumni: Leon Panetta (former Secretary of Defense/CIA Director), Steve Nash (NBA All-Star), Khaled Hosseini (author of The Kite Runner), Janet Napolitano (former Arizona Governor)`

**Final chunk count:** 119 chunks across 17 documents

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (local, no API key required)

**Production tradeoff reflection:**
`all-MiniLM-L6-v2` is the right choice for this project — it runs entirely locally with no API cost or rate limits and produces strong semantic similarity results for short English text. For a production deployment serving real SCU students, I would weigh the following tradeoffs:

- **OpenAI text-embedding-3-small**: Higher accuracy on nuanced queries at ~$0.02 per 1M tokens. Introduces API dependency and network latency, but is cost-effective at scale.
- **multilingual-e5-large**: Essential if serving international students who query in Chinese, Spanish, or Vietnamese — `all-MiniLM-L6-v2` is English-only. SCU's student body is ~20% international, so multilingual support would matter in production.
- **Context length**: `all-MiniLM-L6-v2` handles up to 256 tokens (~400 characters), which matches our chunk size. For larger document types like full PDFs or long handbooks, a model with 512+ token context would be necessary.
- **Local vs. API**: Local inference offers zero latency cost and full data privacy, which matters if documents contain sensitive student information. An API-hosted model would be preferable only when accuracy gains clearly outweigh the privacy and cost tradeoffs.

---

## Retrieval Test Results

**Query 1:** "What do students say about Professor Ye Cai's exams?"
- Top chunks returned: `rmp_ye_cai.txt` chunk 0 (distance: 0.36), `rmp_ye_cai.txt` chunk 5 (0.40), `rmp_ye_cai.txt` chunk 4 (0.45)
- Why relevant: All three chunks are directly from the Ye Cai review file. Chunk 0 contains the review describing exams as "challenging but doable" with cheat sheets allowed; chunk 5 contains the summary section. The query closely matches the semantic content of these chunks.

**Query 2:** "Which freshman dorm is best for quiet studying?"
- Top chunks returned: `scu_dorms_ratemydorm.txt` chunk 0 (distance: 0.23), chunk 1 (0.38), chunk 6 (0.39)
- Why relevant: Chunk 0 opens with the dorm rankings and explicitly labels Campisi Hall as "ideal for students who prefer quiet study environments." The 0.23 distance score indicates near-perfect semantic match — the strongest retrieval result across all test queries.

**Query 3:** "What happens to unused dining points at the end of the quarter?"
- Top chunks returned: `scu_dining_plans.txt` chunk 0 (distance: 0.34), chunk 3 (0.41), `food_insecurity_thesantaclara.txt` chunk 5 (0.44)
- Why relevant: Chunk 0 directly explains the 1-point-per-dollar system and no-swipe structure; chunk 3 covers Dining Plus carryover rules. The third result from the food insecurity article is partially relevant — it mentions dining points in the context of students donating surplus.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are the SCU Unofficial Guide — a helpful assistant that answers questions about
Santa Clara University using ONLY the information provided in the documents below.

Rules you must follow:
1. Answer using ONLY the information in the provided document excerpts. Do not use
   your general knowledge about universities, professors, or dining.
2. If the provided excerpts do not contain enough information to answer the question,
   respond with: "I don't have enough information in my documents to answer that."
3. Be specific and cite which document your answer comes from.
4. Keep answers concise and directly useful to a current or incoming SCU student.
```

**How source attribution is surfaced in the response:**
Attribution works at two levels. First, the system prompt explicitly instructs the LLM to cite which document each piece of information comes from (e.g., "According to rmp_ye_cai.txt..."). Second, the `ask()` function in `query.py` programmatically collects the source filenames from all retrieved chunks and returns them as a separate `sources` list, which the Gradio UI displays in a dedicated "Retrieved from" field below the answer. This means source attribution is guaranteed in the UI regardless of whether the LLM includes citations in its prose.

---

## Example Responses

**Response 1 — grounded answer with source attribution:**

Query: What do students say about Professor Ye Cai's exams in FNCE121?

Answer: According to Document 1 — rmp_ye_cai.txt, students say that Professor Ye Cai's
midterms and final exams in FNCE121 are "definitely more challenging but it's doable" and
that she allows a "cheat sheet" on exams. Additionally, Document 3 — rmp_ye_cai.txt mentions
that her lectures are clear and helpful, and that if you attend classes, you'll likely do well.

Retrieved from:
- rmp_ye_cai.txt
- rmp_tony_nguyen.txt
- rmp_lawrence_nelson.txt

---

**Response 2 — grounded answer with source attribution:**

Query: Which freshman dorm at SCU is best for students who want a quiet study environment?

Answer: According to Document 1 — scu_dorms_ratemydorm.txt, CAMPISI HALL is ideal for
students who prefer quiet study environments. It is positioned near the library and gym for
easy academic access, though its bathrooms are noted as a weak point and it has a limited
social atmosphere.

Retrieved from:
- scu_dorms_ratemydorm.txt
- scu_campus_life_princetonreview.txt

---

**Response 3 — out-of-scope refusal:**

Query: Is there anything my documents don't cover, like parking on campus?

Answer: I don't have enough information in my documents to answer that, specifically regarding
parking on campus. The provided excerpts focus on dorms, dining services, and campus life,
but do not mention parking.

Retrieved from:
- scu_dorms_ratemydorm.txt
- scu_dining_services.txt
- scu_campus_life_collegevine.txt

---

## Query Interface

**Interface type:** Gradio web UI, accessible at `http://localhost:7860` after running `python app.py`.

**Input fields:**
- **Your question** (text box) — the user's plain-language question about SCU
- **Filter by topic** (dropdown) — optionally restrict retrieval to one category: All topics, Professor reviews, Dining, Housing, or Campus life

**Output fields:**
- **Conversation panel** — displays the full multi-turn chat history; each assistant response includes the answer text and a "Retrieved from:" list of source filenames
- **Clear conversation** button — resets the chat history to start a new session

**Sample interaction transcript:**

```
User:       Which freshman dorm is best for a quiet study environment?
            [Filter: Housing]
SCU Guide:  According to scu_dorms_ratemydorm.txt, CAMPISI HALL is ideal for quiet
            study environments, positioned near the library and gym. Rated 3.9/5.

            Retrieved from: scu_dorms_ratemydorm.txt

User:       What about laundry in that dorm?

SCU Guide:  The documents mention that Sobrato Hall has insufficient washers and dryers
            requiring creative scheduling, but do not provide specific laundry details
            for Campisi Hall.

            Retrieved from: scu_dorms_ratemydorm.txt
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Prof. Ye Cai's exams in FNCE121? | Challenging but doable; cheat sheet allowed; mirrors class material | Exams are challenging but doable; cheat sheet allowed; attend class to do well | Relevant (top 3 from rmp_ye_cai.txt, distances 0.36-0.45) | Accurate |
| 2 | Which freshman dorm is best for a quiet study environment? | Campisi Hall (near library/gym, quiet culture); Finn Hall also quiet | Campisi Hall is ideal for quiet study environments | Relevant (top chunks from scu_dorms_ratemydorm.txt, distance 0.23) | Accurate |
| 3 | How do SCU dining points work and what happens to unused points? | 1pt=$1; up to 100 pts carry to next quarter; Dining Plus carries to graduation | Correctly explained 1pt=$1, 100-point carryover, Dining Plus carryover year-to-year | Relevant (top 3 from scu_dining_plans.txt, distances 0.34-0.47) | Accurate |
| 4 | What concerns exist about the SimplyOasis allergen station at Benson? | Frequently lists dairy; unclear gluten labeling; unreliable for celiac | Frequently lists dairy; lacks clear gluten information; unreliable for celiac disease | Relevant (food_insecurity + scu_food_allergy_spokin, distances 0.47-0.53) | Accurate |
| 5 | What do student reviews say about Prof. Stephen Carroll's grading style? | Harsh/personal feedback; unconventional writing system; office hours critical; high attrition | Only mentioned office hours matter — missed harsh feedback, attrition, unconventional system | Partially relevant (top 3 chunks from other professor files; Carroll doc ranked 4th) | Partially accurate |

---

## Failure Case Analysis

**Question that failed:**
"What do student reviews say about Professor Stephen Carroll's grading style?"

**What the system returned:**
The response cited only one detail from the Carroll document: "Your grades on your writing all really depend if you go to his office hours." It missed the more distinctive aspects of student feedback — that Carroll uses an unconventional writing system he created himself, that feedback on essays is described as personal attacks rather than professional critique, and that the class starts with 30 students and ends with fewer than 10.

**Root cause (tied to a specific pipeline stage):**
This is a **retrieval failure**. The query phrase "grading style" is generic enough that it semantically matched review content from other professor files first — chunks from rmp_tony_nguyen.txt (distance: 0.38), rmp_david_keaton.txt (0.38), and rmp_lawrence_nelson.txt (0.39) all ranked above the most relevant Carroll chunks. The Carroll document only appeared at position 4 in the retrieved set. Because the system prompt instructs the LLM to use only the retrieved context, and the most informative Carroll chunks were not in the top results, the LLM generated a thin answer from a single Carroll chunk.

The root cause is that "grading style" is a common phrase across all professor review documents. Without the professor's name as a strong retrieval signal, the embedding similarity became diluted across the entire professor review corpus.

**What you would change to fix it:**
Two fixes would address this. First, **metadata filtering**: restricting retrieval to chunks from a specific source file when the query names a professor would guarantee Carroll chunks rank highest. Second, **query rewriting**: reformulating the query to include the distinctive language ("Stephen Carroll's unconventional writing system") would shift the semantic signal away from generic grading-related text.

---

## Spec Reflection

**One way the spec helped you during implementation:**
Writing the chunking strategy in planning.md before writing any code forced a concrete decision: 400 characters with 80-character overlap, justified by the structure of short review text. This meant that when the ingestion code was implemented, the chunk size was not a guess — it was a reasoned choice that could be verified against the actual output. Printing 5 sample chunks during development confirmed that 400-character chunks captured complete review sentences without merging unrelated opinions.

**One way your implementation diverged from the spec, and why:**
The spec called for using LangChain's CharacterTextSplitter for chunking. During implementation, chunking was instead written as a plain Python function (~10 lines) without importing LangChain at all. LangChain is a heavy dependency that would have added significant install time for functionality that a simple sliding-window loop handles identically. The chunk size, overlap logic, and metadata attachment behavior are identical to what CharacterTextSplitter would have produced.

---

## AI Usage

**Instance 1 — Ingestion and chunking pipeline**

- *What I gave the AI:* The Domain, Documents, Chunking Strategy, and Architecture sections of planning.md, along with the requirement that each chunk retain its source filename as metadata.
- *What it produced:* ingest.py with a clean() function that strips headers, a chunk_text() function implementing the sliding-window split, and a load_chunks() function that returns a list of dicts with text, source, and chunk_index keys.
- *What I changed or overrode:* The initial version used LangChain's CharacterTextSplitter. This was replaced with a plain Python sliding-window implementation to eliminate the dependency. The sample output section was also changed from printing the first 5 chunks (all from the same document) to printing chunks spaced evenly across the corpus.

**Instance 2 — Embedding, retrieval, and generation**

- *What I gave the AI:* The Retrieval Approach section and Architecture diagram from planning.md, plus the chunk data structure produced by ingest.py, plus the grounding requirement (answers only from retrieved context, source filenames cited in every response).
- *What it produced:* embed.py with build_index() and retrieve() functions using ChromaDB and all-MiniLM-L6-v2, and query.py with an ask() function that builds a grounded prompt and returns answer, sources, and chunks.
- *What I changed or overrode:* ChromaDB's default distance metric is L2 (Euclidean), which produced distances in the 0.7-1.1 range. The collection was recreated with cosine distance to get scores in the [0, 1] range, which aligned with the spec's guideline of "below 0.5 for strong matches." This was caught by running the retrieval test and inspecting the distance scores before moving to generation.
