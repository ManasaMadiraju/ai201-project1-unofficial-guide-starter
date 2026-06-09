# Project 1 Planning: The Unofficial Guide

---

## Domain

**Santa Clara University (SCU) Student Survival Guide** — professor reviews, campus dining, housing, and general campus life.

I chose SCU because there's a real gap between what the university's official website says and what students actually experience. If you're trying to figure out which professor to pick for a required course, or whether dining points roll over at the end of the quarter, you end up jumping between Rate My Professors, the student newspaper, random Reddit threads, and the SCU website. It's a lot of digging for pretty basic questions. This project pulls all of that scattered student knowledge into one place where you can just ask.

---

## Documents

| # | Source | Description | URL |
|---|--------|-------------|-----|
| 1 | Rate My Professors — Stephen Carroll | Student reviews of SCU English professor (ENG1A) | https://www.ratemyprofessors.com/professor/406086 |
| 2 | Rate My Professors — David Keaton | Student reviews, ENGL1A and ENGL171 | https://www.ratemyprofessors.com/professor/2045818 |
| 3 | Rate My Professors — Sumana Sur | Student reviews, OMIS15 | https://www.ratemyprofessors.com/professor/125677 |
| 4 | Rate My Professors — Ye Cai | Student reviews, FNCE121 | https://www.ratemyprofessors.com/professor/1589515 |
| 5 | Rate My Professors — Sina Heydari | Student reviews, MECH140/141 | https://www.ratemyprofessors.com/professor/2978478 |
| 6 | Rate My Professors — Tony Nguyen | Student reviews, FNCE124 | https://www.ratemyprofessors.com/professor/726495 |
| 7 | Rate My Professors — Kirk Glaser | Student reviews, creative writing courses | https://www.ratemyprofessors.com/professor/664664 |
| 8 | Rate My Professors — Lawrence Nelson | Student reviews, PHIL30 | https://www.ratemyprofessors.com/professor/13997 |
| 9 | The Santa Clara — Top 10 Professors | Student newspaper's best professors list with student quotes | https://www.thesantaclara.org/blog/top-10-santa-clara-professors |
| 10 | The Santa Clara — Food Insecurity Article | Piece on dining costs, the Bronco Pantry, and food access on campus | https://www.thesantaclara.org/blog/food-insecurity-remains-a-continual-challenge-at-santa-clara-university |
| 11 | SCU Official Dining Services | Dining locations, food trucks, allergen stations, Flex partners | https://www.scu.edu/auxiliary-services/dining-services/ |
| 12 | SCU Official Dining Plans 2025–26 | Dining plan options, point values, carryover rules | https://www.scu.edu/auxiliary-services/dining-services/dining-plans/ |
| 13 | RateMyDorm — SCU Freshman Dorms | Student rankings of Campisi, Finn, Graham, and Sobrato halls | https://www.ratemydorm.com/freshman-dorms-ranked/santa-clara-university |
| 14 | Princeton Review — SCU Profile | Student quotes on academics, campus life, and social scene | https://www.princetonreview.com/college/santa-clara-university-1023579 |
| 15 | Appily — SCU Student Reviews | 10 student reviews on academics, the quarter system, and resources | https://www.appily.com/colleges/santa-clara-university/reviews |
| 16 | Spokin Campus Guide — SCU | Food allergy guide with safe dining stations and off-campus options | https://www.spokin.com/food-allergy-friendly-campus-guide-santa-clara-university |
| 17 | CollegeVine — SCU Campus Life FAQ | Student orgs, housing, Greek life, Silicon Valley connections | https://www.collegevine.com/faq/127434/campus-life-at-santa-clara-university-what-s-it-like |

---

## Chunking Strategy

**Chunk size:** 400 characters
**Overlap:** 80 characters

Most of the content in this corpus is short, opinion-based review text — usually 1 to 5 sentences per review. A 400-character chunk is about 2–4 sentences, which is enough to capture one complete student opinion without accidentally blending two unrelated ones. If chunks were larger, a single chunk might include a comment about a professor's grading *and* their personality, which would make it harder to match a specific query like "what do students say about their exams."

The 80-character overlap is there to avoid losing information at chunk boundaries. Sometimes a review will start a thought at the end of one chunk and finish it at the start of the next — the overlap makes sure either chunk is retrievable for that topic.

I also considered splitting by paragraph, but the documents are too inconsistent for that to work cleanly. Some sources use line breaks, others are dense prose. Fixed-size chunking is less elegant but more reliable across the whole corpus.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers` (runs locally, no API key)
**Top-k:** 5

I picked `all-MiniLM-L6-v2` because it runs entirely on-device with no API cost, and it handles short English text well — which is exactly what this corpus is made of. It also has a 256-token context limit, which lines up nicely with our 400-character chunk size.

Returning 5 chunks gives the LLM enough context to synthesize a real answer (especially for professor queries where useful information might be spread across 3–4 reviews) without dumping too much irrelevant content into the prompt.

**If this were a production system**, I'd think about:
- **OpenAI text-embedding-3-small** — better accuracy on nuanced queries, cheap at scale, but adds API dependency
- **multilingual-e5-large** — SCU's student body is ~20% international; if students are querying in Chinese or Spanish, an English-only model won't work well
- **Local vs. API** — local inference is great for privacy if documents contain sensitive student info; an API model would only make sense if accuracy gains clearly outweigh the tradeoffs

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Professor Ye Cai's exams in FNCE121? | Challenging but fair; cheat sheet allowed; content mirrors class lectures |
| 2 | Which freshman dorm is best for a quiet study environment? | Campisi Hall — rated 3.9/5, near the library, described as ideal for quiet studying |
| 3 | How do SCU dining points work and what happens to unused ones? | 1 point = $1; up to 100 points carry over per quarter; Dining Plus carries year-to-year |
| 4 | What concerns have students raised about the SimplyOasis allergen station? | Frequently lists dairy; unclear gluten labeling; not reliable for celiac disease |
| 5 | What do student reviews say about Professor Stephen Carroll's grading? | Unconventional writing system; grades depend heavily on office hours; feedback can feel harsh; high dropout rate |

---

## Anticipated Challenges

**Chunk boundary splits on short reviews** — Some reviews are only 2–3 sentences. If the professor's name appears in one chunk and the grading opinion appears in the next, a query about grading might return the second chunk without enough context to know which professor it's about. The overlap helps, but it doesn't fully solve this for very short reviews.

**Multi-topic documents** — Files like `scu_campus_life_collegevine.txt` cover academics, housing, dining, and Greek life all in one place. A query about Greek life might pull a chunk that also mentions something unrelated. Keeping chunks small (400 chars) limits how much off-topic content ends up in one chunk, but it's hard to avoid entirely with dense factual paragraphs.

---

## Architecture

```
  documents/ (17 .txt files)
       │
       ▼
  ingest.py
  - Load files with pathlib
  - Strip SOURCE: / URL: headers
  - Split into 400-char chunks with 80-char overlap
  - Attach source filename as metadata
       │
       ▼
  embed.py
  - Embed chunks with all-MiniLM-L6-v2
  - Store in ChromaDB (local, cosine similarity)
  - Collection: "scu_guide"
  - retrieve(query, k=5) → top chunks + distances
       │
       ▼
  query.py
  - Call retrieve() for the user's question
  - Build a grounded prompt with retrieved chunks
  - Call Groq (llama-3.3-70b-versatile)
  - Return answer + source filenames
       │
       ▼
  app.py
  - Gradio web UI at localhost:7860
  - Input: question text + optional category filter
  - Output: answer + sources listed below
  - Supports multi-turn conversation
```

---

## AI Tool Plan

**Milestone 3 — Ingestion:**
Giving Claude the Documents and Chunking Strategy sections above, plus the requirement that each chunk keeps its source filename attached. Expected output: `ingest.py` that loads, cleans, and chunks all documents. Will verify by printing sample chunks and checking they look readable and have the right metadata.

**Milestone 4 — Embedding and retrieval:**
Giving Claude the Retrieval Approach section and the chunk structure from ingest.py. Expected output: `embed.py` with `build_index()` and `retrieve()`. Will verify by running retrieval on the evaluation questions and checking that top results are visibly relevant and have distance scores below 0.5.

**Milestone 5 — Generation and interface:**
Giving Claude the retrieve() function signature and the grounding requirement (answers must come only from the retrieved documents, sources must be cited). Expected output: `query.py` with an `ask()` function and `app.py` with a Gradio UI. Will verify by testing all 5 evaluation questions and checking that out-of-scope questions are declined rather than hallucinated.

---

## Stretch Features

### Stretch 3: Metadata Filtering

Let users filter results to a specific category so a question about professors doesn't pull in dining content.

**Categories:**
- `professor_reviews` — rmp_*.txt, top10_professors_*.txt
- `dining` — scu_dining_*.txt, food_insecurity_*.txt, scu_food_allergy_*.txt
- `housing` — scu_dorms_*.txt
- `campus_life` — scu_campus_life_*.txt, scu_student_reviews_*.txt

**Plan:** Tag each chunk with a category field at index time. Add an optional `category` param to `retrieve()` that passes a `where` filter to ChromaDB. Add a dropdown to the Gradio UI.

### Stretch 4: Conversational Memory

Let users ask follow-up questions without repeating context. "What about her exams?" should work after asking about a specific professor.

**Plan:** Add a `history` parameter to `ask()` — a list of prior turns as `{"role": ..., "content": ...}` dicts. Pass the history to Groq alongside the new query. Update `app.py` to track and pass history between turns.

**Test:** Ask "Tell me about Professor Ye Cai" then "What about her exams?" — the second answer should correctly refer to Ye Cai without being told the name again.
