# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

**Santa Clara University (SCU) Student Survival Guide** — covering professor reviews, campus dining, housing, and campus life from the student perspective.

This knowledge is valuable because SCU's official channels (course catalogs, housing guides, university website) tell you what exists but not what it's actually like. The real knowledge lives in Rate My Professors reviews, student newspaper articles, dorm ranking sites, and food allergy community guides — scattered across a dozen sources that incoming and current students have to hunt down individually. A student asking "Which professor is best for the ENG1A requirement?" or "How do dining points actually work?" needs to cross-reference six different websites to get a complete answer. This system makes that informal, student-generated knowledge searchable in one place.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors — Stephen Carroll | Student reviews of SCU English professor (ENG1A) | https://www.ratemyprofessors.com/professor/406086 |
| 2 | Rate My Professors — David Keaton | Student reviews of SCU English professor (ENGL1A, ENGL171) | https://www.ratemyprofessors.com/professor/2045818 |
| 3 | Rate My Professors — Sumana Sur | Student reviews of SCU OMIS professor (OMIS15) | https://www.ratemyprofessors.com/professor/125677 |
| 4 | Rate My Professors — Ye Cai | Student reviews of SCU Finance professor (FNCE121) | https://www.ratemyprofessors.com/professor/1589515 |
| 5 | Rate My Professors — Sina Heydari | Student reviews of SCU Mechanical Engineering professor (MECH140/141) | https://www.ratemyprofessors.com/professor/2978478 |
| 6 | Rate My Professors — Tony Nguyen | Student reviews of SCU Finance professor (FNCE124) | https://www.ratemyprofessors.com/professor/726495 |
| 7 | Rate My Professors — Kirk Glaser | Student reviews of SCU Creative Writing professor (ENGL71/72/91) | https://www.ratemyprofessors.com/professor/664664 |
| 8 | Rate My Professors — Lawrence Nelson | Student reviews of SCU Philosophy/Ethics professor (PHIL30) | https://www.ratemyprofessors.com/professor/13997 |
| 9 | The Santa Clara — Top 10 Professors | Student newspaper list of SCU's best professors with student quotes | https://www.thesantaclara.org/blog/top-10-santa-clara-professors |
| 10 | The Santa Clara — Food Insecurity Article | Investigative piece on dining costs, Bronco Pantry, and food access at SCU | https://www.thesantaclara.org/blog/food-insecurity-remains-a-continual-challenge-at-santa-clara-university |
| 11 | SCU Official Dining Services | Official list of dining locations, food trucks, allergen stations, off-campus Flex partners | https://www.scu.edu/auxiliary-services/dining-services/ |
| 12 | SCU Official Dining Plans | Full breakdown of 2025-26 dining plan options, point values, carryover rules | https://www.scu.edu/auxiliary-services/dining-services/dining-plans/ |
| 13 | RateMyDorm — SCU Freshman Dorms | Student rankings and reviews of Campisi, Finn, Graham, and Sobrato halls | https://www.ratemydorm.com/freshman-dorms-ranked/santa-clara-university |
| 14 | Princeton Review — SCU Profile | Student quotes on academics, campus life, social scene, housing rates | https://www.princetonreview.com/college/santa-clara-university-1023579 |
| 15 | Appily — SCU Student Reviews | 10 student reviews covering academics, quarter system, professor quality, resources | https://www.appily.com/colleges/santa-clara-university/reviews |
| 16 | Spokin Campus Guide — SCU | Food allergy guide: safe dining stations, off-campus allergy-friendly options with Flex | https://www.spokin.com/food-allergy-friendly-campus-guide-santa-clara-university |
| 17 | CollegeVine — SCU Campus Life FAQ | Student orgs, housing progression, Greek life, Silicon Valley opportunities, notable traditions | https://www.collegevine.com/faq/127434/campus-life-at-santa-clara-university-what-s-it-like |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 80 characters

**Reasoning:**
The corpus is mostly short, opinion-based review text (1–5 sentences per review) mixed with structured factual content (dining plans, dorm descriptions). A 400-character chunk captures 2–4 sentences — enough to hold a complete student opinion or a complete factual claim (e.g., "Professor X's exams are curved and focus on lecture slides") without merging unrelated reviews together. Longer chunks would blend multiple opinions about different aspects of a professor into one embedding, making it harder to match specific queries (e.g., "What do students say about Prof X's grading?" would pull chunks that also mention unrelated topics).

An 80-character overlap (~20% of chunk size) prevents key information from being lost at chunk boundaries. For example, a review that mentions a professor's exam policy in the last sentence of one chunk and elaborates in the first sentence of the next would be retrievable by either chunk.

For purely factual sections (dining plans, dorm ratings), this size is appropriate because each paragraph covers one distinct claim. Paragraph-based splitting was considered but rejected because document formatting is inconsistent — some sources use line breaks, some use run-on prose — making fixed-size chunking with overlap more reliable across the corpus.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 5

**Reasoning for top-k:** 5 chunks provides enough context for the LLM to synthesize an answer across multiple reviews or sources without flooding the prompt with loosely related content. For professor queries, this typically retrieves 3–4 reviews plus a contextual chunk (e.g., a newspaper mention). Too few (k=2) risks missing relevant chunks when similar language is spread across multiple documents; too many (k=8+) introduces noise that can dilute the generated answer.

**Production tradeoff reflection:**
`all-MiniLM-L6-v2` is the right choice for this project — it runs locally with no API cost or rate limits and produces strong semantic similarity results for short English text. For a production deployment serving real SCU students, I would consider:

- **OpenAI text-embedding-3-small**: Higher accuracy on nuanced queries, cost-effective at scale (~$0.02 per 1M tokens), but introduces API dependency and latency
- **text-embedding-3-large**: Best accuracy, but 5x the cost of small — worth it only for high-value queries or low-volume use
- **multilingual-e5-large** (multilingual support): If serving international SCU students who query in Chinese, Spanish, or Vietnamese, a multilingual model would be essential — `all-MiniLM-L6-v2` only handles English well
- **Context length**: `all-MiniLM-L6-v2` handles up to 256 tokens, which is sufficient for 400-character chunks (~80–100 tokens). For larger document types (PDFs, long guides), a model with 512+ token context would be needed
- **Local vs. API**: Local inference (sentence-transformers) offers zero latency cost and data privacy, important if documents contain sensitive student data

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Professor Ye Cai's exams in FNCE121? | Exams are challenging but fair; cheat sheet allowed; most info is covered in class; homework is on Connect and mirrors class problems |
| 2 | Which freshman dorm at SCU is best for students who want a quiet study environment? | Campisi Hall — rated 3.9/5, near library and gym, described as ideal for quiet study; Finn Hall also mentioned as quiet and newest |
| 3 | How do SCU dining points work and what happens to unused points at the end of the quarter? | 1 point = $1, no meal swipes; up to 100 unused resident dining points carry over to next quarter; Dining Plus points carry over year-to-year; first-years can only choose Basic or Preferred plan |
| 4 | What are the concerns students have raised about the SimplyOasis allergen station at Benson? | Designed to avoid top-9 allergens plus gluten but frequently lists dairy and has unclear gluten labeling; not reliable for celiac disease management; students should verify with staff |
| 5 | What do student reviews say about Professor Stephen Carroll's grading style? | Known for unconventional, difficult writing system; grades heavily depend on office hours attendance; personal and harsh written feedback on essays; class has high attrition rate |

---

## Anticipated Challenges

1. **Review text fragmentation across chunk boundaries**: Many professor reviews are 2–4 sentences long. If a review spans a chunk boundary (e.g., the course number and professor name are in one chunk, the grading opinion is in the next), a query about grading may retrieve the second chunk without the professor context. The 80-character overlap partially mitigates this, but it remains a risk for the shortest reviews. This could produce retrieved chunks that are accurate but confusing to the LLM without the surrounding metadata.

2. **Topic drift in multi-topic documents**: Documents like `scu_campus_life_princetonreview.txt` and `scu_campus_life_collegevine.txt` cover academics, social life, housing, dining, and Greek life all in one file. A query about Greek life might retrieve a chunk that also mentions unrelated content (e.g., sustainability ratings), causing the LLM to include irrelevant details. Keeping chunk size at 400 characters (rather than larger) limits how much off-topic content fits into a single chunk, but dense factual paragraphs covering multiple topics in one sentence are hard to split cleanly.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PIPELINE                                 │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────────────┐
  │  Document        │  17 .txt files in documents/
  │  Ingestion       │  Tool: Python open() / pathlib
  │                  │  Clean: strip headers, normalize whitespace
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │  Chunking        │  chunk_size=400 chars, overlap=80 chars
  │                  │  Tool: LangChain CharacterTextSplitter
  │                  │  Metadata: source filename attached to each chunk
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │  Embedding +     │  Model: all-MiniLM-L6-v2 (sentence-transformers)
  │  Vector Store    │  Store: ChromaDB (local, persistent)
  │                  │  Collection: "scu_guide"
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │  Retrieval       │  Query → embed → cosine similarity search
  │                  │  Top-k: 5 chunks returned with source metadata
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │  Generation      │  LLM: Groq llama-3.3-70b-versatile
  │                  │  Prompt: grounded context-only instruction
  │                  │  Output: answer + cited source filenames
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │  Query Interface │  Tool: Gradio (app.py)
  │                  │  Inputs: text question
  │                  │  Outputs: answer text + source list
  └──────────────────┘
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
Tool: Claude (claude-sonnet-4-6)
Input: This planning.md (Documents section + Chunking Strategy section + Architecture diagram), plus the project requirement that each chunk must retain its source filename as metadata.
Expected output: `ingest.py` — a script that (1) loads all .txt files from documents/, (2) strips SOURCE/URL header lines, (3) splits with CharacterTextSplitter at chunk_size=400, overlap=80, (4) attaches source filename metadata to each chunk, (5) prints 5 sample chunks with their source metadata.
Verification: Run the script and manually inspect 5 printed chunks — each should be readable, self-contained, and have a correct source filename attached.

**Milestone 4 — Embedding and retrieval:**
Tool: Claude (claude-sonnet-4-6)
Input: This planning.md (Retrieval Approach section + Architecture diagram) + the chunk data structure produced by ingest.py (list of dicts with `text` and `source` keys).
Expected output: `embed.py` — a script that (1) loads chunks from ingest.py, (2) embeds with SentenceTransformer("all-MiniLM-L6-v2"), (3) stores in a persistent ChromaDB collection "scu_guide" with source metadata, (4) exposes a `retrieve(query, k=5)` function that returns top-k chunks with distance scores and source names.
Verification: Call retrieve() with 3 of the 5 evaluation plan questions and confirm returned chunks are visibly relevant; check distance scores are below 0.5 for top results.

**Milestone 5 — Generation and interface:**
Tool: Claude (claude-sonnet-4-6)
Input: This planning.md (Retrieval Approach + Architecture) + the retrieve() function signature from embed.py + the grounding requirement (answers must come only from retrieved context, with source filenames cited in every response).
Expected output: (1) `query.py` — an `ask(question)` function that calls retrieve(), builds a grounded prompt with the retrieved chunks as context, calls Groq llama-3.3-70b-versatile, and returns `{"answer": str, "sources": list[str]}`; (2) `app.py` — a Gradio interface with a question textbox, Ask button, answer output, and sources output.
Verification: Enter 3 test queries in the Gradio UI; confirm each response cites source filenames; ask an out-of-scope question and confirm the system declines rather than hallucinating.
