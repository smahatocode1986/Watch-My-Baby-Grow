from __future__ import annotations

import html
import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ai_service import ask, demo_food_analysis, demo_insights, demo_plan, demo_story, friendly_error, is_live, narrate, profile_context
from storage import add_event, load_data, recent_events, save_data
from styles import CSS

load_dotenv()
ROOT = Path(__file__).parent
AUDIO_DIR = ROOT / "data" / "story_audio"
st.set_page_config(page_title="LittleBloom · Grow with wonder", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)


def esc(value: object) -> str:
    return html.escape(str(value))


def story_id(record: dict) -> str:
    if record.get("id"):
        return str(record["id"])
    source = f"{record.get('date', '')}|{record.get('theme', '')}|{record.get('story', '')}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]


def story_title(record: dict) -> str:
    match = re.search(r"^###?\s+(.+)$", record.get("story", ""), flags=re.MULTILINE)
    return match.group(1).strip() if match else record.get("theme", "Saved story")


def narration_text(story: str) -> str:
    text = re.sub(r"[`*_#>]", "", story)
    return re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text).strip()


def sidebar(profile: dict) -> None:
    with st.sidebar:
        st.markdown("<div class='brand-kicker'>LittleBloom</div>", unsafe_allow_html=True)
        st.title("Grow with wonder.")
        st.caption("A thoughtful co-pilot for your child's everyday learning and wellbeing.")
        st.divider()
        initials = "".join(p[0] for p in profile.get("name", "Child").split()[:2]).upper()
        st.markdown(f"### {initials} &nbsp; {esc(profile.get('name'))}", unsafe_allow_html=True)
        language_summary = profile.get("language", "English")
        if profile.get("second_language"):
            language_summary += f" + learning {profile['second_language']}"
        st.caption(f"Age {profile.get('age')} · {language_summary} · {profile.get('location')}")
        if st.button("Edit child profile", use_container_width=True):
            st.session_state.edit_profile = not st.session_state.get("edit_profile", False)
        st.divider()
        st.markdown("<div class='privacy'>🔒 <b>Family-first privacy</b><br>Your profile and history stay in this project’s local data folder. Uploaded media is analyzed only when you ask.</div>", unsafe_allow_html=True)
        st.write("")
        status = "<span class='status-live'>● API key configured</span>" if is_live() else "<span class='status-demo'>● Curated demo mode</span>"
        st.markdown(status, unsafe_allow_html=True)
        st.caption("Add `OPENAI_API_KEY` to `.env` for live, profile-aware generation.")


def profile_editor(profile: dict) -> dict:
    with st.container(border=True):
        st.subheader("Child profile")
        st.caption("Use only details you’re comfortable storing locally. Avoid sensitive medical information.")
        c1, c2, c3 = st.columns([1.2, .6, 1.2])
        name = c1.text_input("Name", profile.get("name", ""))
        age = c2.number_input("Age", 2, 17, int(profile.get("age", 7)))
        languages = ["English", "Spanish", "French", "Hindi", "Mandarin", "Arabic", "Other"]
        current_language = profile.get("language", "English")
        language = c3.selectbox("Preferred language", languages, index=languages.index(current_language) if current_language in languages else 0)
        st.markdown("#### Language learning")
        l1, l2 = st.columns(2)
        second_language_options = ["Not set", "Spanish", "French", "Hindi", "Mandarin", "Arabic", "Bengali", "Gujarati", "Tamil", "Telugu", "Other"]
        saved_second_language = profile.get("second_language") or "Not set"
        second_language = l1.selectbox(
            "Second language",
            second_language_options,
            index=second_language_options.index(saved_second_language) if saved_second_language in second_language_options else 0,
            help="Used for playful vocabulary, songs, and bilingual stories.",
        )
        language_levels = ["Just starting", "Understands some words", "Uses short phrases", "Conversational"]
        saved_level = profile.get("second_language_level", "Just starting")
        second_language_level = l2.selectbox(
            "Current exposure",
            language_levels,
            index=language_levels.index(saved_level) if saved_level in language_levels else 0,
            disabled=second_language == "Not set",
        )
        language_learning_notes = st.text_area(
            "Words, songs, or language goals",
            profile.get("language_learning_notes", ""),
            placeholder="For example: knows greetings and colors; family uses a special bedtime song…",
            disabled=second_language == "Not set",
        )
        location = st.text_input("Place", profile.get("location", ""), help="Used only for locally relevant activity ideas.")
        interest_options = ["Animals", "Art", "Building", "Cooking", "Dance", "Dinosaurs", "Drawing", "Flowers", "Music", "Nature", "Puzzles", "Reading", "Space", "Sports", "Water play"]
        interests = st.multiselect("Interests", interest_options, default=[item for item in profile.get("interests", []) if item in interest_options])
        c1, c2 = st.columns(2)
        likes = c1.text_area("Likes", profile.get("likes", ""))
        dislikes = c2.text_area("Dislikes / sensitivities", profile.get("dislikes", ""))
        favorites = st.text_area("Favorite characters, animals, colors, foods & places", profile.get("favorites", ""))
        learning_style = st.text_area("Learning preferences", profile.get("learning_style", ""))
        notes = st.text_area("Routine & behavior notes", profile.get("notes", ""))
        if st.button("Save profile"):
            profile = {**profile, "name": name, "age": age, "language": language, "second_language": "" if second_language == "Not set" else second_language, "second_language_level": second_language_level, "language_learning_notes": language_learning_notes if second_language != "Not set" else "", "location": location, "interests": interests, "likes": likes, "dislikes": dislikes, "favorites": favorites, "learning_style": learning_style, "notes": notes}
            data = load_data(); data["profile"] = profile; save_data(data)
            st.session_state.edit_profile = False
            st.success("Profile saved.")
            st.rerun()
    return profile


def plan_cards(plan: list[dict]) -> None:
    cols = st.columns(len(plan))
    for col, item in zip(cols, plan):
        with col:
            st.markdown(f"<div class='agenda-card {esc(item.get('tone',''))}'><div class='agenda-time'>{esc(item.get('time'))} · {esc(item.get('period'))}</div><h3>{esc(item.get('title'))}</h3><p>{esc(item.get('detail'))}</p><span class='pill'>{esc(item.get('tag'))}</span></div>", unsafe_allow_html=True)


def dashboard(profile: dict) -> None:
    hero = (ROOT / "assets" / "littlebloom-hero.png").as_posix()
    import base64
    b64 = base64.b64encode(Path(hero).read_bytes()).decode()
    st.markdown(f"<div class='hero' style=\"background-image:url('data:image/png;base64,{b64}')\"><div class='hero-copy'><div class='eyebrow'>Saturday · A gentle day</div><h1>Good morning,<br>{esc(profile['name'])}'s family.</h1><p>Small moments of curiosity, movement, and connection add up. Here’s a rhythm shaped around what {esc(profile['name'])} loves.</p></div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-head'><h2>Today at a glance</h2><span>A balanced rhythm, not a checklist</span></div>", unsafe_allow_html=True)
    events = load_data().get("events", [])
    cols = st.columns(4)
    metrics = [("Learning rhythm", "3 moments", "Reading · Making · Reflecting"), ("Move & play", "40 min", "Two joyful movement breaks"), ("Color on plate", "4 groups", "One gentle addition suggested"), ("Connection", "1 ritual", "Three little wins tonight")]
    for col, (label, value, sub) in zip(cols, metrics):
        col.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-sub'>{sub}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-head'><h2>Today’s little adventures</h2><span>Tap Learning to remake the day</span></div>", unsafe_allow_html=True)
    plan = st.session_state.get("plan", demo_plan(profile))
    plan_cards(plan)
    st.markdown("<div class='section-head'><h2>Patterns worth noticing</h2><span>Supportive signals from recent check-ins</span></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for col, insight in zip(cols, demo_insights()):
        col.markdown(f"<div class='insight-card'><div class='insight-icon'>{insight['icon']}</div><h3>{insight['title']}</h3><p>{insight['text']}</p></div>", unsafe_allow_html=True)
    if not events:
        st.caption("This dashboard becomes more personalized as you save meals, activities, and reflections.")


def learning(profile: dict) -> None:
    st.title("A day made for curiosity")
    st.write("Shape an age-appropriate plan around energy, interests, and what happened yesterday.")
    c1, c2, c3 = st.columns(3)
    energy = c1.select_slider("Energy today", ["Quiet", "Steady", "Bouncy"], value="Steady")
    time = c2.selectbox("Time available", ["About 1 hour", "A few hours", "A full day"])
    focus_options = ["Balanced mix", "Reading & language", "Math thinking", "Creative confidence", "Outdoor discovery"]
    if profile.get("second_language"):
        focus_options.insert(2, f"{profile['second_language']} practice")
    focus = c3.selectbox("Gentle focus", focus_options)
    update = st.text_area("What should the plan know?", placeholder="Yesterday she loved measuring ingredients, but found writing frustrating…")
    if st.button("Make today’s plan", type="primary"):
        with st.spinner("Gathering just-right ideas…"):
            if is_live():
                prompt = f"Profile: {profile_context(profile)}\nEnergy: {energy}; time: {time}; focus: {focus}; parent update: {update}. Return ONLY a JSON array of exactly 5 objects with keys time, period, title, detail, tag, tone. tone must be one of coral, teal, yellow, lavender, blue. Keep activities practical, low-cost and developmentally appropriate."
                try:
                    result = ask("You are a warm, evidence-informed children's learning planner. Never diagnose. Treat the plan as flexible suggestions, not performance goals.", prompt)
                    result = result.strip().removeprefix("```json").removesuffix("```").strip()
                    st.session_state.plan = json.loads(result)
                except Exception as exc:
                    st.warning(friendly_error(exc), icon=":material/info:")
                    st.session_state.plan = demo_plan(profile)
            else:
                st.session_state.plan = demo_plan(profile)
            add_event("learning", {"energy": energy, "focus": focus, "parent_update": update})
    st.subheader("Suggested rhythm")
    plan_cards(st.session_state.get("plan", demo_plan(profile)))
    if routine := profile.get("routine"):
        with st.expander(f"{profile.get('name', 'Child')}’s saved daily routine"):
            routine_frame = pd.DataFrame(routine).rename(columns={"time": "Time", "activity": "Activity", "reason": "Why it fits"})
            st.dataframe(routine_frame, hide_index=True, width="stretch")
            st.caption("These times are flexible placeholders—adjust them to match daycare and family life.")
    with st.expander("Why this plan works"):
        st.write("It alternates focus with movement, mixes receptive and creative tasks, and closes with low-pressure reflection. Adjust or skip anything that does not fit your child today.")


def nutrition(profile: dict) -> None:
    st.title("Food patterns, without food pressure")
    st.write("Capture what was offered and eaten. We’ll highlight variety and gentle next steps—never grades, guilt, or calorie counting.")
    mode = st.radio("Add a food moment", ["Write it", "Meal photo", "Food log", "Short video"], horizontal=True)
    uploaded = None; description = ""
    if mode == "Write it":
        description = st.text_area("What did they have?", placeholder="Breakfast: oatmeal with banana, cinnamon, and a glass of water…")
    elif mode == "Meal photo":
        uploaded = st.file_uploader("Upload a clear meal photo", type=["png", "jpg", "jpeg"])
        if uploaded: st.image(uploaded, width=420)
        description = st.text_input("Anything the photo cannot show?", placeholder="She ate most of the fruit and tried one bite of egg.")
    elif mode == "Food log":
        uploaded = st.file_uploader("Upload Excel or CSV", type=["xlsx", "xls", "csv"])
        if uploaded:
            try:
                df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
                st.dataframe(df.head(30), use_container_width=True)
                description = df.head(50).to_csv(index=False)
            except Exception as exc: st.error(f"Could not read that file: {exc}")
    else:
        uploaded = st.file_uploader("Upload a short meal clip", type=["mp4", "mov", "avi"])
        if uploaded: st.video(uploaded)
        description = st.text_area("Briefly describe what happens in the clip", placeholder="Lunch plate before and after eating…")
        st.caption("Video understanding is represented by your description in this version; the file is not stored.")
    if st.button("Review this food moment", type="primary", disabled=not (description or uploaded)):
        with st.spinner("Looking for balance and variety…"):
            analysis = demo_food_analysis(description)
            if is_live() and mode != "Short video":
                try:
                    raw = ask("You are a pediatric nutrition education assistant. Give general, weight-neutral guidance. Do not diagnose, count calories, moralize foods, or replace a clinician. Return strict JSON with score (0-100 variety score), summary, groups (object), wins (array), gentle_next, note.", f"Child profile: {profile_context(profile)}\nMeal notes/data: {description}", uploaded.getvalue() if uploaded and mode == "Meal photo" else None, uploaded.type if uploaded else "image/jpeg")
                    analysis = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
                except Exception as exc:
                    st.warning(friendly_error(exc), icon=":material/info:")
            st.session_state.food_analysis = analysis
            add_event("food", {"input_mode": mode, "description": description[:1000], "analysis": analysis})
    if analysis := st.session_state.get("food_analysis"):
        c1, c2 = st.columns([.35, 1])
        c1.metric("Variety signal", f"{analysis['score']}/100", help="A simple variety indicator—not a grade or health score.")
        c2.info(analysis["summary"])
        cols = st.columns(len(analysis["groups"]))
        for col, (group, value) in zip(cols, analysis["groups"].items()): col.metric(group, f"{value}/3")
        st.subheader("What’s already working")
        for win in analysis["wins"]: st.write(f"✓ {win}")
        st.success(f"A gentle next step: {analysis['gentle_next']}")
        st.caption(analysis["note"] + " Consult a qualified pediatric professional for allergies, growth, feeding difficulties, or medical concerns.")


def stories(profile: dict) -> None:
    st.title("A story that feels like theirs")
    st.write("Turn favorite things and today’s little moments into a cozy, age-aware story.")
    c1, c2, c3 = st.columns(3)
    kind = c1.selectbox("Story moment", ["Bedtime", "Quiet time", "Read together"])
    mood = c2.selectbox("Feeling", ["Cozy", "Silly", "Adventurous", "Reassuring"])
    length = c3.selectbox("Length", ["Tiny · 2 min", "Just right · 5 min", "Longer · 8 min"])
    story_language_options = [profile.get("language", "English")]
    if profile.get("second_language"):
        story_language_options.extend([profile["second_language"], f"Bilingual: {profile['language']} + {profile['second_language']}"])
    story_language = st.selectbox("Story language", story_language_options)
    theme = st.text_input("A spark for tonight", "A secret garden in the stars")
    lesson = st.selectbox("Optional thread", ["Kindness", "Trying again", "Curiosity", "Sharing", "Big feelings", "No lesson—just fun"])
    if st.button("Tell me a story", type="primary"):
        with st.spinner("Sprinkling in a little wonder…"):
            if is_live():
                try:
                    language_guidance = f"Write in {story_language}. For bilingual output, use short second-language phrases, repeat their meaning naturally in context, and match the child's saved exposure level."
                    story = ask("You write original, warm, age-appropriate children's stories. Never imitate living authors or use copyrighted characters; transform named favorites into original archetypes. Avoid peril, stereotypes, moralizing, and marketing. End with one inviting discussion question.", f"Profile: {profile_context(profile)}\nCreate a {length}, {mood}, {kind} story about {theme}. Thread: {lesson}. {language_guidance} Use markdown with a title.")
                except Exception as exc:
                    st.warning(friendly_error(exc), icon=":material/info:")
                    story = demo_story(profile, mood, theme)
            else:
                story = demo_story(profile, mood, theme)
                if story_language != profile.get("language", "English"):
                    st.info("Live AI is needed for second-language or bilingual stories. This curated story is shown in the primary language.", icon=":material/translate:")
                    story_language = profile.get("language", "English")
            record = {"id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "date": date.today().isoformat(), "theme": theme, "mood": mood, "kind": kind, "language": story_language, "story": story}
            st.session_state.story = story
            st.session_state.story_record = record
            data = load_data(); data.setdefault("stories", []).append(record); save_data(data)
    if story := st.session_state.get("story"):
        st.markdown("<div class='story-paper'>", unsafe_allow_html=True)
        st.markdown(story)
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button("Save story", story, file_name=f"littlebloom-story-{date.today()}.md", mime="text/markdown")

    saved_stories = list(reversed(load_data().get("stories", [])))
    st.divider()
    st.subheader("Story library")
    st.caption("Generated stories are recorded locally and remain here after the app restarts.")
    if not saved_stories:
        st.info("Your first generated story will appear here.", icon=":material/auto_stories:")
        return

    labels = {
        story_id(record): f"{record.get('date', 'Unknown date')} · {story_title(record)} · {record.get('language', profile.get('language', 'English'))}"
        for record in saved_stories
    }
    selected_key = st.selectbox(
        "Choose a recorded story",
        list(labels),
        format_func=lambda key: labels[key],
        key="selected_story_id",
    )
    selected = next(record for record in saved_stories if story_id(record) == selected_key)
    with st.container(border=True):
        st.markdown(selected.get("story", ""))
        actions = st.container(horizontal=True)
        actions.download_button(
            "Download text",
            selected.get("story", ""),
            file_name=f"{selected_key}-story.md",
            mime="text/markdown",
            icon=":material/download:",
        )
        make_audio = actions.button(
            "Create audio",
            key=f"narrate_{selected_key}",
            icon=":material/headphones:",
        )

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    audio_path = AUDIO_DIR / f"{selected_key}.mp3"
    if make_audio and not audio_path.exists():
        with st.spinner("Recording a gentle narration…"):
            try:
                audio_path.write_bytes(narrate(narration_text(selected.get("story", ""))))
            except Exception as exc:
                st.warning(friendly_error(exc), icon=":material/info:")
    if audio_path.exists():
        st.caption("AI-generated voice narration")
        st.audio(audio_path, format="audio/mpeg")
        st.download_button(
            "Download audio",
            audio_path.read_bytes(),
            file_name=f"{selected_key}-story.mp3",
            mime="audio/mpeg",
            icon=":material/audio_file:",
        )


def insights(profile: dict) -> None:
    st.title("A gentle view of the whole child")
    st.write("Look across learning, food, routines, and connection—without labels or diagnoses.")
    events = load_data().get("events", [])
    c1, c2, c3 = st.columns(3)
    c1.metric("Check-ins saved", len(events))
    c2.metric("Learning moments", len([e for e in events if e.get("kind") == "learning"]))
    c3.metric("Food moments", len([e for e in events if e.get("kind") == "food"]))
    st.subheader("This week’s supportive signals")
    for item in demo_insights():
        st.markdown(f"<div class='soft-card' style='margin-bottom:10px'><b>{item['icon']} &nbsp;{item['title']}</b><br><span style='color:#6f7a75'>{item['text']}</span></div>", unsafe_allow_html=True)
    st.subheader("Add a parent reflection")
    c1, c2 = st.columns(2)
    bright = c1.text_area("What brought joy or focus?", placeholder="She stayed with the painting activity for a long time…")
    hard = c2.text_area("What felt difficult?", placeholder="The transition to homework was bumpy…")
    if st.button("Save reflection"):
        add_event("reflection", {"bright_spot": bright, "challenge": hard})
        st.success("Reflection saved. Future plans can use this context.")
    with st.expander("Recent family history"):
        for event in recent_events(limit=8):
            st.write(f"**{event['created_at'][:10]} · {event['kind'].title()}**")
            st.caption(str({k: v for k, v in event.items() if k not in {'created_at', 'kind', 'analysis'}})[:500])
        if not events: st.caption("No entries yet. Your first saved plan, meal, or reflection will appear here.")


data = load_data()
profile = data["profile"]
sidebar(profile)
if st.session_state.get("edit_profile"):
    profile_editor(profile)
    st.stop()

tabs = st.tabs(["Today", "Learning", "Food & nutrition", "Story studio", "Growth insights"])
with tabs[0]: dashboard(profile)
with tabs[1]: learning(profile)
with tabs[2]: nutrition(profile)
with tabs[3]: stories(profile)
with tabs[4]: insights(profile)

st.divider()
st.caption("LittleBloom offers general educational and wellness ideas. It is not medical, nutritional, behavioral, or educational diagnosis. Parent judgment comes first.")
