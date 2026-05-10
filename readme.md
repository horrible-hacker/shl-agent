# SHL Assessment Conversational Agent

## Problem
Hiring managers can't always articulate what they need. Traditional keyword search assumes the user knows the right vocabulary. This agent moves from vague intent to a grounded shortlist of SHL assessments through dialogue.

## Live API
- **Health:** `GET https://ravishing-caring-production.up.railway.app/health`
- **Chat:** `POST https://ravishing-caring-production.up.railway.app/chat`

## Tech Stack
| Component | Choice | Reason |
|---|---|---|
| LLM | Groq — `meta-llama/llama-4-scout-17b-16e-instruct` | Fast inference, OpenAI-compatible, strong instruction following |
| API | FastAPI + Uvicorn | Lightweight, async, auto validation |
| Catalog | JSON file (in-memory) | ~400 items, fits in RAM |
| Retrieval | Semantic search via Sentence Transformers | Handles vocabulary mismatch, no vector DB needed |
| Embeddings | `all-MiniLM-L6-v2` (local) | Free, fast, runs on CPU, no API key needed |
| Deployment | Railway | Free tier, auto-deploy on push |
| Agent Logic | Raw Python + Groq SDK | No LangChain — simpler, faster, easier to debug |

## Architecture

```text
POST /chat
  → concatenate all user messages
  → embed query with all-MiniLM-L6-v2
  → cosine similarity search over pre-embedded catalog (top 15)
  → inject matches into system prompt
  → Groq LLM (`meta-llama/llama-4-scout-17b-16e-instruct`) generates structured JSON reply
  → validate all URLs against catalog set
  → return response
```

## Agent Behaviors
- **Clarify** — asks 1 question if message has zero context. Max 1 clarifying turn.
- **Recommend** — once role OR level OR skill OR industry known, recommends 3–10 assessments immediately.
- **Refine** — updates shortlist when user changes constraints without restarting.
- **Compare** — answers comparison questions using only injected catalog data.
- **In-scope only** — refuses legal advice, general HR questions, salary questions, prompt injection.

## Retrieval Setup
At startup, all ~400 catalog items are embedded once using `all-MiniLM-L6-v2` and stored in memory. For each request, the full conversation history (all user turns concatenated) is embedded and compared via cosine similarity to find the top 15 most relevant assessments. These are injected as structured text into the system prompt.

This approach handles vocabulary mismatch — e.g. "plant operators" finds safety assessments even without exact keyword overlap.

All returned URLs are validated against the catalog set — hallucinated links are stripped before response is returned.

## Evaluation Approach
- Tested against all 10 public conversation traces
- Measured Recall@10 per trace and mean across all traces
- Verified schema compliance on every response (`reply`, `recommendations`, `end_of_conversation`)
- Confirmed all returned URLs exist in catalog
- Behavior probes: refusal of off-topic queries, schema fields, refinement, URL validity

## Performance
- Warm request latency typically stays between ~1–2.5 seconds
- Retrieval latency remains sub-100ms due to in-memory embeddings
- Main latency contributor is Groq inference time
- Cold starts mainly come from Railway container wake-up and embedding model initialization

## What Worked
- Semantic search with sentence transformers handled vocabulary mismatch better than pure keyword matching
- Per-request catalog injection kept prompts focused and relevant
- Explicit turn limits in prompt forced earlier recommendations improving Recall@10
- URL validation post-processing eliminated hallucinated links
- Concatenating all user turns for search improved catalog match quality

## What Didn't Work
- Initial system prompt was too conservative — agent kept asking clarifying questions even after sufficient context was provided, hurting recall on early turns. Fixed by explicitly instructing the model to recommend as soon as any role, level, skill, or industry is mentioned.
- Pure keyword search missed relevant assessments when user phrasing differed from catalog vocabulary (e.g. "plant operators" not matching "safety"). Fixed by switching to semantic embeddings.
- Smaller free models (HuggingFace 8B) produced lower quality recommendations and struggled to follow JSON output format consistently. Groq's `meta-llama/llama-4-scout-17b-16e-instruct` provided significantly better instruction following, response quality, and JSON consistency while maintaining low latency.

## AI Tools Used
Claude (Anthropic) was used for scaffolding the project structure, iterating on the system prompt, debugging deployment issues, and writing the eval script. All code was reviewed and manually tested. Core design decisions — retrieval strategy, prompt rules, URL validation — were made by the author.

## Project Structure

```text
shl-agent/
├── main.py          # FastAPI app
├── catalog.py       # semantic search over catalog
├── agent.py         # Groq LLM + prompt logic
├── eval.py          # evaluation script
├── data/
│   └── catalog.json
├── models/
│   └── all-MiniLM-L6-v2/  # local embedding model
└── requirements.txt
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn groq python-dotenv sentence-transformers scikit-learn numpy
export GROQ_API_KEY=your_key_here
uvicorn main:app --reload --port 8000
```