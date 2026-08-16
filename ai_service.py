"""AI generation with an offline-first fallback and optional OpenAI integration."""

from __future__ import annotations

import base64
import json
import os
from typing import Any


def is_live() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def friendly_error(error: Exception) -> str:
    """Turn provider/network exceptions into safe, actionable UI copy."""
    detail = str(error).lower()
    if "credit_balance_exhausted" in detail or "insufficient_quota" in detail or "no credits remaining" in detail:
        return "Live AI is paused because this API project has no credits remaining. Curated demo content is shown instead."
    if "invalid_api_key" in detail or "incorrect api key" in detail or "authentication" in detail:
        return "The configured API key could not be authenticated. Curated demo content is shown instead."
    if "rate_limit" in detail or "rate limit" in detail or "too many requests" in detail:
        return "Live AI is temporarily busy. Please wait a moment and try again; curated demo content is shown for now."
    if "connection" in detail or "timeout" in detail:
        return "The AI service could not be reached. Check the connection and try again; curated demo content is shown for now."
    return "Live AI is temporarily unavailable, so curated demo content is shown instead."


def _client():
    from openai import OpenAI

    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def ask(system: str, prompt: str, image: bytes | None = None, mime: str = "image/jpeg") -> str:
    if not is_live():
        raise RuntimeError("AI key not configured")
    content: list[dict[str, Any]] = [{"type": "input_text", "text": prompt}]
    if image:
        encoded = base64.b64encode(image).decode("ascii")
        content.append({"type": "input_image", "image_url": f"data:{mime};base64,{encoded}"})
    response = _client().responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=system,
        input=[{"role": "user", "content": content}],
    )
    return response.output_text


def narrate(text: str, voice: str = "coral") -> bytes:
    """Generate an MP3 narration for a saved story."""
    if not is_live():
        raise RuntimeError("AI key not configured")
    response = _client().audio.speech.create(
        model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
        voice=voice,
        input=text[:12000],
        instructions="Read as a warm, gentle children's storyteller. Use a calm pace, expressive but soothing delivery, and a soft pause between paragraphs.",
        response_format="mp3",
    )
    return response.content


def profile_context(profile: dict[str, Any]) -> str:
    return json.dumps(profile, ensure_ascii=False)


def demo_plan(profile: dict[str, Any]) -> list[dict[str, str]]:
    name = profile.get("name", "your child")
    routine = profile.get("routine") or []
    if routine:
        selected = [routine[index] for index in (0, 3, 5, 6, 12) if index < len(routine)]
        tones = ["coral", "teal", "yellow", "lavender", "blue"]
        periods = ["Morning spark", "Daycare connection", "Free play", "Move & explore", "Wind down"]
        plan = [
            {
                "time": item["time"].replace(" AM", "").replace(" PM", ""),
                "period": periods[index],
                "title": item["activity"],
                "detail": item["reason"],
                "tag": "Flexible · Family rhythm",
                "tone": tones[index],
            }
            for index, item in enumerate(selected)
        ]
        if second_language := profile.get("second_language"):
            level = profile.get("second_language_level", "Just starting").lower()
            notes = profile.get("language_learning_notes") or "use three familiar family-approved words"
            plan[2] = {
                "time": "3:00",
                "period": "Language through play",
                "title": f"A little {second_language}",
                "detail": f"During drawing or pretend play, {notes}. Keep it playful and match a child who is {level}.",
                "tag": "5–10 min · Listen + repeat",
                "tone": "yellow",
            }
        return plan
    interest = (profile.get("interests") or ["nature"])[0]
    plan = [
        {"time": "8:00", "period": "Morning spark", "title": "Wonder question", "detail": f"Ask {name}: “If you could visit any {interest.lower()} world, what would you notice first?”", "tag": "10 min · Conversation", "tone": "coral"},
        {"time": "10:30", "period": "Learning focus", "title": f"{interest} fact detective", "detail": "Read a short page together, circle three new words, then draw the most surprising fact.", "tag": "25 min · Reading + art", "tone": "teal"},
        {"time": "3:45", "period": "Move & reset", "title": "Color trail challenge", "detail": "Take a walk and spot five colors. Add a hop, stretch, or silly walk at each one.", "tag": "20 min · Movement", "tone": "yellow"},
        {"time": "6:30", "period": "Create together", "title": "Build a tiny habitat", "detail": "Use paper or recyclables to make a home for a favorite animal. Explain each design choice.", "tag": "30 min · STEM play", "tone": "lavender"},
        {"time": "7:45", "period": "Wind down", "title": "Three little wins", "detail": "Share one thing learned, one kind moment, and one thing to try tomorrow.", "tag": "8 min · Reflection", "tone": "blue"},
    ]
    if second_language := profile.get("second_language"):
        plan[2] = {
            "time": "3:45",
            "period": "Language through play",
            "title": f"A little {second_language}",
            "detail": "Practice three familiar words through movement, pictures, or a favorite song. Let understanding come before speaking.",
            "tag": "10 min · Listen + play",
            "tone": "yellow",
        }
    return plan


def demo_story(profile: dict[str, Any], mood: str, theme: str) -> str:
    name = profile.get("name", "Maya")
    favorite = profile.get("favorites", "red pandas and the beach")
    return f"""### {name} and the Lantern of Little Brave Things

At the edge of a moonlit garden, {name} found a lantern no bigger than a strawberry. It did not glow when held up high. It glowed only when someone did a small brave thing.

“Small is perfect,” whispered Pip, a red panda with a teal scarf. Together they followed a trail toward {theme.lower()}. The path wobbled across a silver stream, and {name}'s knees felt wobbly too. So {name} took one slow breath, then one careful step. *Blink!* The lantern warmed to gold.

Beyond the stream, they met a cloud who had forgotten how to rain. {name} listened without interrupting. *Blink!* The lantern shone brighter. Pip offered a slice of mango, and soon the cloud was laughing soft, happy raindrops over the flowers.

When they reached home, the lantern had become a tiny sunrise. “You filled it,” said Pip.

“With big brave things?” asked {name}.

“No,” Pip smiled. “With listening, trying, and being kind—the little things that quietly change the world.”

That night, with thoughts of {favorite}, {name} tucked the lantern beside the bed. Its glow faded to a cozy ember, just right for a {mood.lower()} dream.

**A question to share:** What small brave thing did you do today?"""


def demo_food_analysis(description: str) -> dict[str, Any]:
    return {
        "score": 78,
        "summary": "A colorful, energy-friendly meal with a solid base. Adding one protein or calcium-rich choice could help it last longer.",
        "groups": {"Fruit & veg": 3, "Protein": 1, "Whole grains": 2, "Hydration": 2},
        "wins": ["Visible color variety", "Likely child-friendly portions", "A useful source of quick energy"],
        "gentle_next": "Try adding yogurt, hummus, egg, beans, tofu, or cheese—whichever already feels familiar.",
        "note": "This is general wellness guidance, not a medical assessment.",
    }


def demo_insights() -> list[dict[str, str]]:
    return [
        {"icon": "↗", "title": "Visual learning is clicking", "text": "Drawing after reading may be helping new ideas stick. Keep this pairing in the weekly rhythm."},
        {"icon": "☀", "title": "Protect the after-school reset", "text": "A snack and 15 minutes of free movement before focused tasks can make transitions gentler."},
        {"icon": "♥", "title": "Build on small wins", "text": "End the day with one specific success. It supports confidence without adding performance pressure."},
    ]
