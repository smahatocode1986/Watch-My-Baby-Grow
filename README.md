# LittleBloom

LittleBloom is an AI-ready Streamlit assistant that helps parents create personalized learning rhythms, review food variety, generate original stories, and notice supportive lifestyle patterns for a child.

## What’s included

- A warm, responsive parent dashboard
- Editable child profile with preferences, routines, and learning style
- Optional second-language profile with exposure level, family vocabulary notes, playful practice plans, and bilingual story choices
- Daily plan generation with energy, time, focus, and parent context
- Meal capture through text, photo, Excel/CSV, or short video
- Weight-neutral nutrition guidance with explicit safety boundaries
- Personalized, original story generation
- Persistent story library with reusable AI voice narration and MP3 downloads
- Local JSON history for learning, meals, reflections, and stories
- Optional OpenAI Responses API integration and a complete offline demo mode

## Run locally

On Windows, the easiest option is:

```powershell
.\run.ps1
```

The script detects the common Windows Store Python alias problem, creates `.venv`, installs dependencies, and launches Streamlit. If script execution is disabled, run `Set-ExecutionPolicy -Scope Process Bypass` once in that terminal.

Or set up the environment manually:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

The app works immediately in curated demo mode. For live multimodal AI and story narration, set `OPENAI_API_KEY` in `.env`; optionally change `OPENAI_MODEL` or `OPENAI_TTS_MODEL`. Narration uses API credits, is clearly labeled as AI-generated, and is cached under `data/story_audio/` after the first generation.

## Supabase persistence

LittleBloom uses local JSON by default and switches to Supabase automatically when `SUPABASE_URL` and `SUPABASE_SECRET_KEY` are configured.

1. Create a Supabase project.
2. Run `supabase/schema.sql` in the Supabase SQL Editor.
3. Copy `.env.example` to `.env` and add the project URL and server-side secret key.
4. Restart Streamlit. The first successful connection seeds Supabase with the existing local JSON history.

For Streamlit Community Cloud, add the same values in the app's Secrets settings. Never commit `.env`, `.streamlit/secrets.toml`, or a Supabase secret key. This lightweight schema stores one private application-state document and is intended for a single family. Add Supabase Auth and per-family rows before supporting multiple accounts.

## Architecture

```text
Streamlit UI (app.py)
  ├── profile + local interaction state
  ├── AI service (live Responses API / offline fallback)
  ├── ingestion (text, image, video preview, Excel/CSV)
  └── local JSON store (data/littlebloom.json)
```

For production, replace `storage.py` with encrypted Postgres/object storage, add authenticated parent accounts, consent and retention controls, background media processing, audit logging, and a clinician-reviewed safety/evaluation layer. Uploaded media is not persisted by this prototype.

## Privacy and safety

Profile and history data remain in the local project folder. Do not enter sensitive medical data. Nutrition and lifestyle outputs are general suggestions—not diagnosis or treatment. Any allergy, growth, feeding, developmental, or mental-health concern should go to an appropriately qualified professional.

## Generated asset

`assets/littlebloom-hero.png` was created specifically for this project with the built-in OpenAI image generation tool. Prompt: a warm editorial illustration of a curious child reading, surrounded by subtle learning, nutrition, creativity, and wellbeing motifs; cream/coral/teal palette; landscape composition with left-side negative space; no text, logos, or watermark.
