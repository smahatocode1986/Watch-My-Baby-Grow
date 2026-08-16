from __future__ import annotations

import html
import hashlib
import json
import re
from datetime import date, datetime, timedelta
from io import StringIO
from pathlib import Path

import altair as alt
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


def _dashboard_legacy(profile: dict) -> None:
    hero = (ROOT / "assets" / "littlebloom-hero.png").as_posix()
    import base64
    b64 = base64.b64encode(Path(hero).read_bytes()).decode()
    today = datetime.now()
    today_label = f"{today:%A} · {today:%B} {today.day}, {today:%Y}"
    st.markdown(f"<div class='hero' style=\"background-image:url('data:image/png;base64,{b64}')\"><div class='hero-copy'><div class='eyebrow'>{today_label}</div><h1>Good morning,<br>{esc(profile['name'])}'s family.</h1><p>Small moments of curiosity, movement, and connection add up. Here’s a rhythm shaped around what {esc(profile['name'])} loves.</p></div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-head'><h2>Today at a glance</h2><span>A balanced rhythm, not a checklist</span></div>", unsafe_allow_html=True)
    events = load_data().get("events", [])
    cols = st.columns(4)
    metrics = [("Learning rhythm", "3 moments", "Reading · Making · Reflecting"), ("Move & play", "40 min", "Two joyful movement breaks"), ("Color on plate", "4 groups", "One gentle addition suggested"), ("Connection", "1 ritual", "Three little wins tonight")]
    for col, (label, value, sub) in zip(cols, metrics):
        col.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-sub'>{sub}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-head'><h2>Today’s little adventures</h2><span>Tap Learning to remake the day</span></div>", unsafe_allow_html=True)
    plan = st.session_state.get("plan") or demo_plan(profile)
    plan_cards(plan)
    st.markdown("<div class='section-head'><h2>Patterns worth noticing</h2><span>Supportive signals from recent check-ins</span></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for col, insight in zip(cols, demo_insights()):
        col.markdown(f"<div class='insight-card'><div class='insight-icon'>{insight['icon']}</div><h3>{insight['title']}</h3><p>{insight['text']}</p></div>", unsafe_allow_html=True)
    if not events:
        st.caption("This dashboard becomes more personalized as you save meals, activities, and reflections.")


def adventure_image(item: dict) -> Path:
    text = f"{item.get('title', '')} {item.get('detail', '')} {item.get('period', '')}".lower()
    if any(word in text for word in ("move", "dance", "water", "outside", "explore", "play")):
        return ROOT / "assets" / "adventure-move.png"
    if any(word in text for word in ("story", "read", "wind", "family", "reflect", "bed")):
        return ROOT / "assets" / "adventure-connect.png"
    return ROOT / "assets" / "adventure-create.png"


def dashboard(profile: dict) -> None:
    import base64

    hero = ROOT / "assets" / "littlebloom-hero.png"
    b64 = base64.b64encode(hero.read_bytes()).decode()
    today = datetime.now()
    today_label = f"{today:%A} · {today:%B} {today.day}, {today:%Y}"
    child_name = esc(profile.get("name", "your child"))
    st.markdown(f"<div class='hero' style=\"background-image:url('data:image/png;base64,{b64}')\"><div class='hero-copy'><div class='eyebrow'>{today_label}</div><h1>Good morning,<br>{child_name}'s family.</h1><p>Small moments of curiosity, movement, and connection add up. Here’s a rhythm shaped around what {child_name} loves.</p></div></div>", unsafe_allow_html=True)

    events = load_data().get("events", [])
    plan = st.session_state.get("plan") or demo_plan(profile)
    st.session_state.setdefault("today_adventures_done", [])
    completed = st.session_state.today_adventures_done
    food_today = len([event for event in events if event.get("kind") == "food" and event.get("created_at", "")[:10] == date.today().isoformat()])

    st.markdown("<div class='section-head'><h2>Today’s little adventures</h2><span>Choose one small moment at a time</span></div>", unsafe_allow_html=True)
    plan_by_title = {item["title"]: item for item in plan}
    adventure_titles = list(plan_by_title)
    default_adventure = adventure_titles[0]
    selected_title = st.pills("Choose an adventure", adventure_titles, default=default_adventure, key="selected_adventure")
    if selected_title not in plan_by_title:
        selected_title = default_adventure
    selected = plan_by_title[selected_title]
    image_col, detail_col = st.columns([1.05, 1], vertical_alignment="center")
    with image_col:
        st.image(adventure_image(selected), width="stretch")
    with detail_col.container(border=True):
        st.badge(f"{selected.get('time')} · {selected.get('period')}", color="orange")
        st.subheader(selected["title"])
        st.write(selected["detail"])
        st.caption(selected.get("tag", "Flexible family rhythm"))
        is_done = selected_title in completed
        button_label = "Completed today" if is_done else "Mark as done"
        if st.button(button_label, key=f"done_{selected_title}", icon=":material/check_circle:", type="secondary" if is_done else "primary"):
            if is_done:
                st.session_state.today_adventures_done = [title for title in completed if title != selected_title]
            else:
                st.session_state.today_adventures_done = [*completed, selected_title]
            st.rerun()
    if completed:
        st.progress(len(completed) / len(plan), text=f"{len(completed)} of {len(plan)} adventures explored")

    st.markdown("<div class='section-head'><h2>Today at a glance</h2><span>Tap a focus to explore the day</span></div>", unsafe_allow_html=True)
    metric_row = st.container(horizontal=True)
    metric_row.metric("Learning rhythm", f"{len(completed)}/{len(plan)}", "adventures explored", border=True, chart_data=[0, 1, len(completed)], chart_type="bar")
    metric_row.metric("Move & play", "40 min", "gentle daily idea", border=True, chart_data=[10, 15, 15], chart_type="bar")
    metric_row.metric("Food moments", str(food_today), "logged today", border=True, chart_data=[0, food_today], chart_type="bar")
    metric_row.metric("Connection", "1 ritual", "little wins tonight", border=True, chart_data=[0, 1], chart_type="line")
    focus_details = {
        "Learning": "Short, playful moments build confidence without turning the day into a checklist.",
        "Movement": "Two movement breaks can be dancing, water play, or a walk together.",
        "Food": "Offer familiar foods alongside one gentle opportunity for variety.",
        "Connection": "Close the day by naming one thing that felt joyful or brave.",
    }
    glance_focus = st.segmented_control("Explore today's rhythm", list(focus_details), default="Learning", key="glance_focus")
    st.info(focus_details[glance_focus], icon=":material/lightbulb:")

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


def _nutrition_legacy(profile: dict) -> None:
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


FOOD_GROUPS = {
    "Fruit": ("banana", "mango", "apple", "berry", "berries", "orange", "pear", "peach", "melon", "strawberry"),
    "Vegetables": ("broccoli", "carrot", "peas", "spinach", "avocado", "sweet potato", "tomato", "pepper", "corn"),
    "Grains": ("rice", "oat", "bread", "toast", "pasta", "quinoa", "cereal", "tortilla"),
    "Protein": ("bean", "chicken", "fish", "salmon", "egg", "tofu", "lentil", "turkey", "nut butter"),
    "Dairy / alternative": ("milk", "yogurt", "cheese", "kefir", "soy milk"),
}

FOOD_IDEAS = {
    "Fruit": [("Blueberries", "Soft berries beside a familiar breakfast"), ("Ripe pear", "Thin, soft slices with yogurt")],
    "Vegetables": [("Sweet potato", "Soft roasted cubes next to rice"), ("Broccoli", "Steamed florets with a familiar dip")],
    "Grains": [("Oatmeal", "Warm oats topped with banana"), ("Whole-grain toast", "Toast fingers with avocado")],
    "Protein": [("Lentils", "A spoonful mixed into familiar rice"), ("Egg", "Soft scrambled egg served family-style")],
    "Dairy / alternative": [("Plain yogurt", "Yogurt with mango stirred in"), ("Fortified soy milk", "Offer in the usual cup with a meal")],
}

FOOD_CHART_PALETTE = {
    "Banana": "#F6C453",
    "Rice": "#F4A6C6",
    "Beans": "#B98CD9",
    "Chicken": "#F2836B",
    "Fish": "#5EC8D8",
    "Mango": "#FFA45C",
    "Apple": "#E8607A",
}


def food_groups_in(text: str) -> set[str]:
    lowered = text.lower()
    return {group for group, words in FOOD_GROUPS.items() if any(word in lowered for word in words)}


def food_event_time(event: dict) -> datetime:
    try:
        return datetime.fromisoformat(event.get("created_at", ""))
    except (TypeError, ValueError):
        return datetime.min


def food_chart_rows(events: list[dict]) -> pd.DataFrame:
    """Expand saved meal notes and uploaded CSV logs into chartable food occurrences."""
    rows: list[dict] = []
    meal_names = {"breakfast": "Breakfast", "lunch": "Lunch", "dinner": "Dinner", "snack": "Snack"}
    for event in events:
        description = event.get("description", "")
        event_date = food_event_time(event).date()
        parsed_log = False
        if "Date," in description and "Breakfast" in description:
            try:
                log = pd.read_csv(StringIO(description))
                for _, record in log.iterrows():
                    logged_date = pd.to_datetime(record.get("Date"), errors="coerce")
                    if pd.isna(logged_date):
                        continue
                    for column, meal in meal_names.items():
                        source_column = next((name for name in log.columns if str(name).lower() == column), None)
                        if not source_column or pd.isna(record.get(source_column)):
                            continue
                        foods_text = str(record[source_column]).lower()
                        for food in FOOD_CHART_PALETTE:
                            if food.lower() in foods_text:
                                rows.append({"Date": logged_date.date(), "Meal": meal, "Food": food, "Count": 1})
                parsed_log = True
            except (pd.errors.ParserError, ValueError):
                parsed_log = False
        if parsed_log or event_date == datetime.min.date():
            continue
        meal = event.get("meal_type", "Food moment")
        lowered = description.lower()
        for food in FOOD_CHART_PALETTE:
            if food.lower() in lowered:
                rows.append({"Date": event_date, "Meal": meal, "Food": food, "Count": 1})
    return pd.DataFrame(rows, columns=["Date", "Meal", "Food", "Count"])


def nutrition(profile: dict) -> None:
    child_name = profile.get("name", "your child")
    import base64

    nutrition_image = ROOT / "assets" / "nutrition-banner.png"
    nutrition_b64 = base64.b64encode(nutrition_image.read_bytes()).decode()
    st.markdown(
        f"<div class='nutrition-hero' style=\"background-image:url('data:image/png;base64,{nutrition_b64}')\">"
        f"<div class='nutrition-hero-copy'><div class='eyebrow'>A colorful food story</div>"
        f"<h1>Food &amp; nutrition</h1><p>See {esc(child_name)}'s food story over time and discover gentle ideas for variety—without pressure, grades, or calorie counting.</p>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    all_food_events = [event for event in load_data().get("events", []) if event.get("kind") == "food"]
    cutoff = datetime.now() - timedelta(days=7)
    recent_foods = [event for event in all_food_events if food_event_time(event) >= cutoff]
    group_counts = {group: 0 for group in FOOD_GROUPS}
    for event in recent_foods:
        text = f"{event.get('description', '')} {event.get('foods', '')}"
        detected = food_groups_in(text)
        analysis_groups = event.get("analysis", {}).get("groups", {})
        for group in group_counts:
            if group in detected or analysis_groups.get(group, 0):
                group_counts[group] += 1

    st.subheader("This week's balance snapshot")
    metric_cols = st.columns(3)
    metric_cols[0].metric("Food moments", len(recent_foods), help="Meals and snacks logged in the last 7 days")
    groups_seen = sum(value > 0 for value in group_counts.values())
    metric_cols[1].metric("Food groups seen", f"{groups_seen}/5")
    metric_cols[2].metric("New foods tried", len([e for e in recent_foods if e.get("new_food_tried")]))
    st.caption("Variety across days matters more than making every plate perfect.")
    st.progress(groups_seen / len(group_counts), text="Weekly variety")

    st.subheader("Food timeline")
    st.caption("Choose a period and meal types to explore the foods offered each day.")
    chart_source = food_chart_rows(all_food_events)
    chart_dates = chart_source["Date"].tolist() if not chart_source.empty else []
    earliest_date = min(chart_dates) if chart_dates else date.today() - timedelta(days=6)
    latest_date = max(chart_dates) if chart_dates else date.today()
    default_start = max(earliest_date, latest_date - timedelta(days=6))
    filter_cols = st.columns([1, 1.7], vertical_alignment="bottom")
    selected_dates = filter_cols[0].date_input(
        "Date range",
        value=(default_start, latest_date),
        min_value=earliest_date,
        max_value=max(date.today(), latest_date),
        key="food_date_range",
    )
    meal_options = ["Breakfast", "Lunch", "Dinner", "Snack", "Food moment"]
    meal_filter = filter_cols[1].pills(
        "Meals",
        meal_options,
        default=meal_options,
        selection_mode="multi",
        key="food_meals",
    )
    timeline = sorted(all_food_events, key=food_event_time, reverse=True)
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        range_start, range_end = selected_dates
    else:
        range_start = range_end = selected_dates
    timeline = [
        event for event in timeline
        if food_event_time(event) != datetime.min and range_start <= food_event_time(event).date() <= range_end
    ]
    if meal_filter:
        timeline = [event for event in timeline if event.get("meal_type", "Food moment") in meal_filter]
    else:
        timeline = []
    filtered_chart = chart_source[
        chart_source["Date"].between(range_start, range_end)
        & chart_source["Meal"].isin(meal_filter or [])
    ].copy() if not chart_source.empty else chart_source
    chart_view = st.segmented_control(
        "Chart view",
        ["By day", "Period total"],
        default="By day",
        key="food_chart_view",
    )
    if not filtered_chart.empty:
        food_order = list(FOOD_CHART_PALETTE)
        food_colors = alt.Scale(domain=food_order, range=list(FOOD_CHART_PALETTE.values()))
        with st.container(border=True):
            st.markdown(f"<div class='food-chart-head'><span>{esc(child_name)}'s food story</span><h3>Food variety chart</h3><p>{range_start.strftime('%b %d')} – {range_end.strftime('%b %d, %Y')}</p></div>", unsafe_allow_html=True)
            if chart_view == "By day":
                daily = filtered_chart.groupby(["Date", "Food"], as_index=False)["Count"].sum()
                daily["Date label"] = pd.to_datetime(daily["Date"])
                chart = alt.Chart(daily).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                    x=alt.X("yearmonthdate(Date label):O", title=None, axis=alt.Axis(format="%a\n%b %d", labelAngle=0)),
                    y=alt.Y("sum(Count):Q", title="Times offered", axis=alt.Axis(tickMinStep=1)),
                    color=alt.Color("Food:N", scale=food_colors, sort=food_order, title=None),
                    order=alt.Order("Food:N", sort="ascending"),
                    tooltip=[
                        alt.Tooltip("Date label:T", title="Date", format="%A, %b %d"),
                        alt.Tooltip("Food:N"),
                        alt.Tooltip("sum(Count):Q", title="Times offered"),
                    ],
                ).properties(height=340)
            else:
                totals = filtered_chart.groupby("Food", as_index=False)["Count"].sum()
                chart = alt.Chart(totals).mark_arc(innerRadius=72, outerRadius=138, cornerRadius=5, padAngle=.025).encode(
                    theta=alt.Theta("Count:Q", stack=True),
                    color=alt.Color("Food:N", scale=food_colors, sort=food_order, title=None),
                    tooltip=[alt.Tooltip("Food:N"), alt.Tooltip("Count:Q", title="Times offered")],
                ).properties(height=340)
            st.altair_chart(chart)
            st.caption("Based on saved meal entries. One count means the food appeared in a logged meal; it is not a calorie or portion measure.")
    if False and timeline:
        timeline_rows = []
        for event in timeline:
            moment = food_event_time(event)
            meal = event.get("meal_type", "Food moment")
            description_text = event.get("description") or event.get("foods") or "Meal saved"
            detected_groups = sorted(food_groups_in(description_text))
            timeline_rows.append({
                "When": moment,
                "Meal": meal,
                "Food group": detected_groups[0] if detected_groups else "Other",
                "Foods offered": description_text[:180],
                "Variety": max(1, len(detected_groups)),
            })
        timeline_frame = pd.DataFrame(timeline_rows)
        meal_order = ["Breakfast", "Lunch", "Dinner", "Snack", "Food moment"]
        color_scale = alt.Scale(
            domain=["Fruit", "Vegetables", "Grains", "Protein", "Dairy / alternative", "Other"],
            range=["#e8785f", "#4f8b62", "#dfa940", "#648aa3", "#9580a7", "#9a948a"],
        )
        guide = alt.Chart(timeline_frame).mark_rule(color="#ded8cc", strokeWidth=2).encode(
            y=alt.Y("Meal:N", sort=meal_order, title=None)
        )
        points = alt.Chart(timeline_frame).mark_circle(opacity=.92, stroke="#fffdfa", strokeWidth=2).encode(
            x=alt.X("When:T", title="Date and time", axis=alt.Axis(format="%b %d", labelAngle=0, grid=True)),
            y=alt.Y("Meal:N", sort=meal_order, title=None),
            color=alt.Color("Food group:N", scale=color_scale, title="Main food group"),
            size=alt.Size("Variety:Q", scale=alt.Scale(range=[180, 520]), legend=None),
            tooltip=[
                alt.Tooltip("When:T", title="When", format="%a, %b %d · %I:%M %p"),
                alt.Tooltip("Meal:N", title="Meal"),
                alt.Tooltip("Foods offered:N", title="Foods offered"),
                alt.Tooltip("Food group:N", title="Main group"),
            ],
        )
        chart = (guide + points).properties(height=300).interactive(bind_y=False)
        with st.container(border=True):
            st.altair_chart(chart)
            st.caption(f"Showing {len(timeline)} food moment{'s' if len(timeline) != 1 else ''}. Larger circles include more detected food groups.")
    elif filtered_chart.empty:
        st.info("No food moments match these filters yet. Add one below to start the timeline.", icon=":material/restaurant:")

    st.subheader("Add a food moment")
    mode = st.segmented_control("How would you like to add it?", ["Write it", "Meal photo", "Food log", "Short video"], default="Write it")
    meal_type = st.selectbox("Meal or snack", ["Breakfast", "Lunch", "Dinner", "Snack"])
    uploaded = None
    description = ""
    if mode == "Write it":
        description = st.text_area("What did they have?", placeholder="Breakfast: oatmeal with banana, cinnamon, and water…")
    elif mode == "Meal photo":
        uploaded = st.file_uploader("Upload a clear meal photo", type=["png", "jpg", "jpeg"])
        if uploaded:
            st.image(uploaded, width=420)
        description = st.text_input("Anything the photo cannot show?", placeholder="She ate most of the fruit and tried one bite of egg.")
    elif mode == "Food log":
        uploaded = st.file_uploader("Upload Excel or CSV", type=["xlsx", "xls", "csv"])
        if uploaded:
            try:
                frame = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
                st.dataframe(frame.head(30), width="stretch")
                description = frame.head(50).to_csv(index=False)
            except Exception as exc:
                st.error(f"Could not read that file: {exc}")
    else:
        uploaded = st.file_uploader("Upload a short meal clip", type=["mp4", "mov", "avi"])
        if uploaded:
            st.video(uploaded)
        description = st.text_area("Briefly describe what happens in the clip", placeholder="Lunch plate before and after eating…")
        st.caption("Video understanding is represented by your description in this version; the file is not stored.")

    if st.button("Review this food moment", type="primary", disabled=not (description or uploaded), key="review_food"):
        with st.spinner("Looking for balance and variety…"):
            analysis = demo_food_analysis(description)
            if is_live() and mode != "Short video":
                try:
                    raw = ask("You are a pediatric nutrition education assistant. Give general, weight-neutral guidance. Do not diagnose, count calories, moralize foods, or replace a clinician. Return strict JSON with score (0-100 variety score), summary, groups (object), wins (array), gentle_next, note.", f"Child profile: {profile_context(profile)}\nMeal notes/data: {description}", uploaded.getvalue() if uploaded and mode == "Meal photo" else None, uploaded.type if uploaded else "image/jpeg")
                    analysis = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
                except Exception as exc:
                    st.warning(friendly_error(exc), icon=":material/info:")
            st.session_state.food_analysis = analysis
            add_event("food", {"input_mode": mode, "meal_type": meal_type, "description": description[:1000], "analysis": analysis})
            st.rerun()

    if analysis := st.session_state.get("food_analysis"):
        with st.container(border=True):
            c1, c2 = st.columns([.35, 1])
            c1.metric("Variety signal", f"{analysis['score']}/100", help="A simple variety indicator—not a grade or health score.")
            c2.info(analysis["summary"])
            st.success(f"A gentle next step: {analysis['gentle_next']}")

    st.subheader("Try next")
    missing_groups = [group for group, count in group_counts.items() if count == 0]
    focus_groups = (missing_groups + [group for group in sorted(group_counts, key=group_counts.get) if group not in missing_groups])[:3]
    idea_cols = st.columns(3)
    for index, (col, group) in enumerate(zip(idea_cols, focus_groups)):
        name, serving = FOOD_IDEAS[group][index % len(FOOD_IDEAS[group])]
        with col.container(border=True, height="stretch"):
            st.badge(group, color="green" if group in {"Fruit", "Vegetables"} else "blue")
            st.subheader(name)
            st.write(serving)
            st.caption("Serve beside something familiar; looking, touching, or tasting all count as learning.")
            if st.button("Mark as tried", key=f"try_{group}_{name}", icon=":material/check_circle:"):
                add_event("food", {"input_mode": "suggestion", "meal_type": "Snack", "description": name, "new_food_tried": True})
                st.toast(f"Added {name} to the timeline")
                st.rerun()
    st.caption("General ideas only. Check age-appropriate textures and speak with a pediatric professional about allergies, feeding difficulties, growth, or medical needs.")


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
    theme = st.text_input("Story Title", "What’s the story about?", placeholder="A rainy day adventure, a lost toy, a brave little explorer…")
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
