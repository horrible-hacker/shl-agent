# SHL Assessment Conversational Agent

## Problem
Hiring managers can't always articulate what they need. Traditional keyword search assumes the user knows the right vocabulary. This agent moves from vague intent to a grounded shortlist of SHL assessments through dialogue.

## Live API
- **Health:** `GET https://ravishing-caring-production.up.railway.app/health`
- **Chat:** `POST https://ravishing-caring-production.up.railway.app/chat`

## Tech Stack
| Component | Choice | Reason |
|---|---|---|
| LLM | Groq — llama-3.3-70b-versatile | Free, fast (<3s), OpenAI-compatible |
| API | FastAPI + Uvicorn | Lightweight, async, auto validation |
| Catalog | JSON file (in-memory) | ~400 items, fits in RAM |
| Retrieval | Keyword scoring | No vector DB needed at this scale |
| Deployment | Railway | Free tier, auto-deploy on push |
| Agent Logic | Raw Python + Groq SDK | No LangChain — simpler, faster |

## Architecture
```
POST /chat
  → concatenate all user messages → keyword search catalog (top 15)
  → inject matches into system prompt
  → Groq LLM generates JSON reply
  → validate URLs against catalog
  → return structured response
```

## Agent Behaviors
- **Clarify** — asks 1 question if role/level/skills all unknown. Max 2 clarifying turns.
- **Recommend** — once role OR level OR skills known, recommends 3–10 assessments immediately.
- **Refine** — updates shortlist when user changes constraints without restarting.
- **Compare** — answers comparison questions using only injected catalog data.
- **In-scope only** — refuses legal advice, general HR questions, prompt injection.

## Retrieval
Each catalog item is scored by counting query words found in: name + description + keys + job levels. Top 15 injected into prompt as plain text. All returned URLs validated against catalog — hallucinated links stripped.

## Project Structure
```
shl-agent/
├── main.py        # FastAPI app
├── catalog.py     # load & search catalog
├── agent.py       # Groq LLM + prompt logic
├── data/
│   └── catalog.json
└── requirements.txt
```

## What Worked
- Per-request catalog injection kept prompts focused and relevant
- Explicit turn limits in prompt forced earlier recommendations improving Recall@10
- URL validation post-processing eliminated hallucinated links
- Concatenating all user turns for search improved catalog match quality

## What Didn't Work
- Initial system prompt was too conservative — agent kept asking clarifying questions even after sufficient context was provided, hurting recall on early turns. Fixed by explicitly instructing the model to recommend as soon as role OR level OR skills are known.
- Keyword search occasionally missed relevant assessments when user phrasing differed from catalog vocabulary; partially mitigated by using full conversation history for search instead of just the last message.

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn groq python-dotenv
export GROQ_API_KEY=your_key_here
uvicorn main:app --reload --port 8000
```