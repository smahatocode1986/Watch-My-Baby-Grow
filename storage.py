"""Small, transparent JSON persistence layer for LittleBloom."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"
STORE = DATA_DIR / "littlebloom.json"

DEFAULT_PROFILE = {
    "name": "Nyra",
    "age": 3,
    "language": "English",
    "second_language": "",
    "second_language_level": "Just starting",
    "language_learning_notes": "",
    "location": "New York, USA",
    "interests": ["Dance", "Music", "Drawing", "Animals", "Water play", "Flowers"],
    "likes": "Dancing, singing, splashing and water play; drawing smiley, sad, and angry faces; playing with her dog Simba; naming her friends and sisters; lollipops only as a toy/prop, never to eat.",
    "dislikes": "Do not offer lollipops as food; they are for pretend play only.",
    "favorites": "Pink; flowers; banana, rice, beans, chicken, fish, mango, and apple; Bluey, Peppa Pig, Demon Hunters, and her flower-ghost character called the Demogorgon; dinosaurs, jungles, animals, mountains, and lava in stories; her dog Simba; Miss Stephania, her daycare teacher.",
    "learning_style": "Learns through music, movement, water play, pretend play, drawing emotion faces, and short stories.",
    "notes": "Daycare is part of her weekday rhythm. She enjoys time with Miss Stephania, friends, sisters, and Simba. Encourage gentle play with Simba. Routine times are flexible placeholders.",
    "routine": [
        {"time": "7:00 AM", "activity": "Wake up + morning song and dance", "reason": "Starts the day with movement and music she loves."},
        {"time": "7:30 AM", "activity": "Breakfast: banana, rice, or eggs", "reason": "Builds breakfast around familiar foods."},
        {"time": "8:00 AM", "activity": "Get dressed and choose something pink", "reason": "Offers a simple favorite-color choice."},
        {"time": "8:30 AM", "activity": "Daycare drop-off", "reason": "Time with Miss Stephania and friends."},
        {"time": "12:00 PM", "activity": "Lunch: chicken or fish with rice and beans", "reason": "A familiar favorite-food combination."},
        {"time": "3:00 PM", "activity": "Pick-up + free play", "reason": "Pretend lollipop play or drawing emotion faces."},
        {"time": "4:00 PM", "activity": "Water play", "reason": "Bath, pool, or water-table play."},
        {"time": "5:00 PM", "activity": "Snack: mango or apple", "reason": "Offers familiar fruit."},
        {"time": "5:30 PM", "activity": "Gentle Simba time", "reason": "Connection and supervised gentle play with her dog."},
        {"time": "6:00 PM", "activity": "Show time", "reason": "Bluey, Peppa Pig, or Demon Hunters."},
        {"time": "6:30 PM", "activity": "Family dinner", "reason": "A family-style meal with familiar foods."},
        {"time": "7:00 PM", "activity": "Bath with flower-themed toys", "reason": "Combines her love of water and flowers."},
        {"time": "7:30 PM", "activity": "Wind-down drawing", "reason": "Draw smiley, sad, and angry faces."},
        {"time": "8:00 PM", "activity": "Bedtime story", "reason": "Dinosaurs, jungle, animals, mountains, or lava."},
        {"time": "8:30 PM", "activity": "Lights out", "reason": "A consistent bedtime close."},
    ],
}


def _seed() -> dict[str, Any]:
    return {"profile": DEFAULT_PROFILE, "events": [], "stories": [], "plans": []}


def load_data() -> dict[str, Any]:
    DATA_DIR.mkdir(exist_ok=True)
    if not STORE.exists():
        save_data(_seed())
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _seed()


def save_data(data: dict[str, Any]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    STORE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def add_event(kind: str, payload: dict[str, Any]) -> None:
    data = load_data()
    data.setdefault("events", []).append(
        {"kind": kind, "created_at": datetime.now().isoformat(timespec="seconds"), **payload}
    )
    save_data(data)


def recent_events(kind: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    events = load_data().get("events", [])
    if kind:
        events = [event for event in events if event.get("kind") == kind]
    return list(reversed(events[-limit:]))
