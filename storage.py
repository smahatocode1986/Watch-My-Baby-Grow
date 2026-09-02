"""Small, transparent JSON persistence layer for LittleBloom."""

from __future__ import annotations

import json
import os
import warnings
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
STORE = DATA_DIR / "littlebloom.json"
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "app_state")
SUPABASE_STATE_ID = os.getenv("SUPABASE_STATE_ID", "littlebloom")

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


def is_supabase_configured() -> bool:
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return bool(os.getenv("SUPABASE_URL") and key)


@lru_cache(maxsize=1)
def _supabase_client():
    from supabase import create_client

    url = os.environ["SUPABASE_URL"]
    key = os.getenv("SUPABASE_SECRET_KEY") or os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)


def _load_local() -> dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STORE.exists():
        STORE.write_text(json.dumps(_seed(), indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _seed()


def _save_local(data: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_data() -> dict[str, Any]:
    if not is_supabase_configured():
        return _load_local()

    try:
        response = (
            _supabase_client()
            .table(SUPABASE_TABLE)
            .select("payload")
            .eq("id", SUPABASE_STATE_ID)
            .limit(1)
            .execute()
        )
    except httpx.TransportError as exc:
        warnings.warn(
            f"Supabase is unreachable ({exc}). Using local JSON storage for this run.",
            RuntimeWarning,
            stacklevel=2,
        )
        return _load_local()
    if response.data:
        payload = response.data[0].get("payload")
        if isinstance(payload, dict):
            return payload

    # First connection: preserve and migrate any existing local history.
    initial_data = _load_local()
    save_data(initial_data)
    return initial_data


def save_data(data: dict[str, Any]) -> None:
    if not is_supabase_configured():
        _save_local(data)
        return

    try:
        (
            _supabase_client()
            .table(SUPABASE_TABLE)
            .upsert(
                {
                    "id": SUPABASE_STATE_ID,
                    "payload": data,
                    "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                },
                on_conflict="id",
            )
            .execute()
        )
    except httpx.TransportError as exc:
        warnings.warn(
            f"Supabase is unreachable ({exc}). Saving to local JSON storage instead.",
            RuntimeWarning,
            stacklevel=2,
        )
        _save_local(data)


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
