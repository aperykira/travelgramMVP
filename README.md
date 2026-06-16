# Travelgram Starter

This is a lightweight working MVP for Travelgram, an AI Travel Assistant that turns Instagram-inspired or manually uploaded travel inspiration into:

1. A Travel Taste Profile
2. Destination recommendations
3. A personalized itinerary
4. Conversational itinerary refinements

The app is designed for a capstone/demo and intentionally avoids overbuilding: no direct Instagram saved-post syncing, no booking integration, no live pricing, and no full RAG. It uses a curated static knowledge pack instead.

## What is included

- `app.py` — Streamlit app
- `src/demo_engine.py` — deterministic demo mode that works without an API key
- `src/llm_client.py` — optional OpenAI API adapter
- `src/prompt_templates.py` — prompt-building logic
- `data/master_prompt.md` — master prompt with hallucination guardrails
- `data/static_knowledge_pack.json` — curated static destination knowledge pack
- `eval/llm_judge_prompt.md` — LLM-as-judge prompt
- `eval/run_eval.py` — evaluation runner scaffold
- `.env.example` — environment variable example
- `requirements.txt`

## Quick start

```bash
cd ai_travel_mvp_starter
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate  # Windows

pip install -r requirements.txt
streamlit run app.py
```

The app runs in **Demo Mode** without any API key.

## Optional: Use an LLM API

1. Copy `.env.example` to `.env`
2. Add your API key:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

3. Restart the app and select **OpenAI API** in the sidebar.

You can change the model name to any model available in your account.

## Suggested demo script

Paste this into the inspiration box:

```text
Kyoto street food, matcha cafés, quiet temples, boutique ryokans, scenic walking streets.
I like cozy cafés, local food markets, calm cultural experiences, and slow-paced days.
```

Then:
1. Create Travel Taste Profile
2. Recommend destinations
3. Select Kyoto
4. Generate a 4-day itinerary
5. Refine with: "Make this cheaper and more relaxed."

## MVP guardrails

The app’s prompt instructs the assistant not to invent:
- exact prices
- current hours
- live availability
- booking status
- exact menus
- fake hidden gems
- real-time events
- flight or hotel availability

Dynamic details should be placed under **What to verify**.

## Recommended next steps

- Add your Golden Test Set as a CSV
- Automate judge scoring using `eval/llm_judge_prompt.md`
- Add a small database for saved sessions
- Add user authentication only after the demo is stable
- Add full RAG only when scaling to many destinations or company-approved content
