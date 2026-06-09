# SCU Unofficial Guide

A conversational AI assistant that answers questions about Santa Clara University using real student-generated content — professor reviews, dining info, housing ratings, and campus life guides. Ask a question and get a grounded answer with sources cited.

---

## What It Does

SCU's official website tells you what exists. This project answers what it's actually like. It pulls together student reviews from Rate My Professors, SCU's student newspaper, dorm ranking sites, and food allergy guides into a searchable, conversational interface.

**Try asking things like:**
- "Which professor is best for the ENG1A requirement?"
- "How do dining points work and what happens to unused ones?"
- "Which freshman dorm is quietest for studying?"
- "Is the SimplyOasis allergen station reliable for celiac students?"

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Groq API key
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=your_key_here

# 3. Build the vector index
python embed.py

# 4. Launch the app
python app.py
# Open http://localhost:7860
```

---

## How It Works

The pipeline has three stages:

1. **Ingest** (`ingest.py`) — Loads 17 `.txt` documents, strips metadata headers, and splits the text into overlapping chunks.
2. **Embed** (`embed.py`) — Converts each chunk into a vector using `all-MiniLM-L6-v2` and stores everything in a local ChromaDB database.
3. **Query** (`query.py`) — When you ask a question, the system finds the most relevant chunks, passes them to Groq's LLaMA model, and returns a grounded answer with sources.

The model is instructed to answer **only from the retrieved documents** — if the documents don't cover something, it says so.

---

## Document Sources

17 documents collected from student-facing platforms:

| # | Source | Category |
|---|--------|----------|
| 1–8 | Rate My Professors — Carroll, Keaton, Sur, Ye Cai, Heydari, Nguyen, Glaser, Nelson | Professor reviews |
| 9 | The Santa Clara — Top 10 Professors article | Professor reviews |
| 10 | The Santa Clara — Food Insecurity article | Dining |
| 11–12 | SCU Official Dining Services & Dining Plans 2025–26 | Dining |
| 13 | RateMyDorm — SCU Freshman Dorms Ranked | Housing |
| 14–15 | Princeton Review & Appily — SCU student reviews | Campus life |
| 16 | Spokin Campus Guide — SCU Food Allergy info | Dining |
| 17 | CollegeVine — SCU Campus Life FAQ | Campus life |

---

## Chunking Strategy

- **Chunk size:** 400 characters
- **Overlap:** 80 characters

Most of the content is short, opinion-based review text — a few sentences at a time. 400 characters captures one complete thought or review without mixing opinions from different students. The 80-character overlap makes sure nothing important gets cut off at a boundary.

**Example chunks:**

> `rmp_ye_cai.txt` — *"Cai is an amazing professor. She goes at a perfect pace for you to understand the material. Homework is on Connect and is very similar to problems done in class. No group projects! Midterms/Final are definitely more challenging but it's doable. She allows cheat sheet for them too."*

> `scu_dorms_ratemydorm.txt` — *"#1 CAMPISI HALL (Rating: 3.9/5) — Ideal for students who prefer quiet study environments. Positioned near the library and gym."*

> `scu_dining_plans.txt` — *"HOW DINING POINTS WORK: 1 dining point = $1. There are no 'meal swipes' — all purchases deduct points from your balance."*

**Total:** 119 chunks across 17 documents.

---

## Embedding Model

**Model:** `all-MiniLM-L6-v2` via `sentence-transformers` (runs locally, no API key needed)

This model works well for short English text, has no API cost, and handles up to ~400 characters per chunk — which matches the chunk size exactly. For a production system serving international students, a multilingual model would be a better fit since SCU's student body is ~20% international.

---

## Retrieval Results

| Query | Top source | Distance | Result |
|-------|-----------|----------|--------|
| "Professor Ye Cai's exams" | `rmp_ye_cai.txt` | 0.36 | Accurate |
| "Best dorm for quiet studying" | `scu_dorms_ratemydorm.txt` | 0.23 | Accurate |
| "Unused dining points" | `scu_dining_plans.txt` | 0.34 | Accurate |

Distances below 0.5 indicate strong semantic matches. The dorm query at 0.23 was the strongest retrieval result across all tests.

---

## Example Responses

**Question:** What do students say about Professor Ye Cai's exams in FNCE121?

> According to rmp_ye_cai.txt, students say exams are "definitely more challenging but doable." A cheat sheet is allowed, and most content comes directly from lectures. Students who attend class regularly tend to do well.
>
> *Retrieved from: rmp_ye_cai.txt*

---

**Question:** Which freshman dorm is best for quiet studying?

> According to scu_dorms_ratemydorm.txt, Campisi Hall is rated best for quiet study environments. It's near the library and gym. The main downsides are the bathrooms and a limited social scene.
>
> *Retrieved from: scu_dorms_ratemydorm.txt*

---

**Question:** Is there anything about parking on campus?

> I don't have enough information in my documents to answer that. The documents cover dorms, dining, and campus life but don't mention parking.

---

## Stretch Features

### Filter by Topic

Each chunk is tagged with a category at index time (`professor_reviews`, `dining`, `housing`, `campus_life`). The UI includes a dropdown to restrict search to a specific category before running the similarity query — useful when you want professor-only results without dining or housing content mixing in.

### Conversational Memory

Follow-up questions work naturally. The conversation history is passed to the model with each new query, so references like "what about *her* exams?" resolve correctly from the previous turn. Without history, "her" would have no referent — the model would return generic content.

**Example:**

```
User:       Tell me about Professor Ye Cai.
SCU Guide:  [answers with her rating, teaching style, homework format]

User:       What about her exams specifically?
SCU Guide:  [resolves "her" → Ye Cai, returns exam-specific details]
```

---

## Evaluation

| # | Question | Expected | Actual | Accuracy |
|---|----------|----------|--------|----------|
| 1 | Prof. Ye Cai's exams | Challenging, cheat sheet allowed, mirrors class | Challenging, cheat sheet allowed, attend class | ✅ Accurate |
| 2 | Best dorm for quiet study | Campisi Hall | Campisi Hall | ✅ Accurate |
| 3 | Dining points & carryover | 1pt=$1, 100pt carryover, Dining Plus carryover | Correct on all three | ✅ Accurate |
| 4 | SimplyOasis allergen concerns | Dairy issues, unclear gluten labeling, unreliable for celiac | All three concerns covered | ✅ Accurate |
| 5 | Prof. Stephen Carroll's grading | Harsh feedback, unconventional writing system, high dropout | Only mentioned office hours matter | ⚠️ Partial |

### Why Question 5 Failed

The query "grading style" is a generic phrase that appears across all professor review files. Chunks from other professors (Nguyen, Keaton, Nelson) ranked higher than the Carroll-specific chunks because the phrase matched them just as well. The most informative Carroll chunks didn't make it into the top 5 results.

**Fix:** Add metadata filtering by professor name so Carroll-specific chunks always rank first when his name is in the query.

---

## Reflection

**How planning helped:** Writing out the chunking strategy before coding forced a concrete decision — 400 chars with 80-char overlap — that I could verify by actually printing sample chunks. It wasn't a guess.

**Where I diverged from the spec:** The spec suggested using LangChain's `CharacterTextSplitter`. I replaced it with a ~10-line plain Python function that does the same thing. LangChain adds significant install weight for one operation that's easy to write directly.

---

## AI Usage

**Ingestion pipeline**
- *Input:* Domain description, document structure, chunking requirements
- *Output:* `ingest.py` with `clean()`, `chunk_text()`, and `load_chunks()` functions
- *Changed:* Replaced LangChain splitter with plain Python; changed sample output to show chunks spread evenly across the corpus instead of all from the same file

**Embedding, retrieval, and generation**
- *Input:* Architecture diagram from planning.md, chunk data structure, grounding requirements
- *Output:* `embed.py` with ChromaDB + sentence-transformers, `query.py` with grounded prompt
- *Changed:* ChromaDB defaulted to L2 distance (scores 0.7–1.1). Switched to cosine similarity to get scores in the [0, 1] range as expected by the spec.
