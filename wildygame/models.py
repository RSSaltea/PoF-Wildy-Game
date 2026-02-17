"""
Data models and persistence for the Wilderness game.

This module contains:
- Core data structures (PlayerState, DuelState)
- JSON persistence (JsonStore)
- Utility functions (_now, clamp, parse_chance)
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, List

from .config_default import DEFAULT_CONFIG

# File paths
DATA_DIR = "data/wilderness"
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")


# Utility functions
def _now() -> int:
    """Get current Unix timestamp."""
    return int(time.time())


def clamp(n: int, lo: int, hi: int) -> int:
    """Clamp value between min and max."""
    return max(lo, min(hi, n))


def parse_chance(v: Any) -> float:
    """
    Parse probability from various formats.

    Accepts:
    - "1/50" (or "3/100")
    - "0.02" (string) or 0.02 (float/int)
    - "2%" (optional convenience)

    Returns: probability in [0,1]
    """
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return max(0.0, min(1.0, float(v)))
    s = str(v).strip().lower()
    if not s:
        return 0.0
    if s.endswith("%"):
        try:
            pct = float(s[:-1].strip())
            return max(0.0, min(1.0, pct / 100.0))
        except Exception:
            return 0.0
    if "/" in s:
        try:
            a, b = s.split("/", 1)
            num = float(a.strip())
            den = float(b.strip())
            if den <= 0:
                return 0.0
            return max(0.0, min(1.0, num / den))
        except Exception:
            return 0.0
    try:
        return max(0.0, min(1.0, float(s)))
    except Exception:
        return 0.0


@dataclass
class PlayerState:
    """Complete player profile with inventory, stats, and progression."""

    user_id: int
    started: bool = False
    coins: int = 0
    bank_coins: int = 0
    inventory: Dict[str, int] = None
    bank: Dict[str, int] = None
    in_wilderness: bool = False
    wildy_level: int = 1
    hp: int = 99
    skulled: bool = False
    risk: Dict[str, int] = None
    equipment: Dict[str, str] = None
    uniques: Dict[str, int] = None
    pets: List[str] = None
    kills: int = 0
    deaths: int = 0
    ventures: int = 0
    escapes: int = 0
    biggest_win: int = 0
    biggest_loss: int = 0
    unique_drops: int = 0
    pet_drops: int = 0
    cd: Dict[str, int] = None
    last_action: int = 0
    active_buffs: Dict[str, Dict[str, int]] = None
    blacklist: List[str] = None
    locked: List[str] = None
    wildy_run_id: int = 0

    def __post_init__(self):
        """Initialize mutable default fields."""
        if self.inventory is None:
            self.inventory = {}
        if self.bank is None:
            self.bank = {}
        if self.risk is None:
            self.risk = {}
        if self.equipment is None:
            self.equipment = {}
        if self.uniques is None:
            self.uniques = {}
        if self.pets is None:
            self.pets = []
        if self.cd is None:
            self.cd = {}
        if not self.last_action:
            self.last_action = _now()
        if self.active_buffs is None:
            self.active_buffs = {}
        if self.blacklist is None:
            self.blacklist = []
        if self.locked is None:
            self.locked = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PlayerState":
        """Create PlayerState from dictionary."""
        if not isinstance(d, dict):
            return PlayerState(user_id=0)

        allowed = set(PlayerState.__dataclass_fields__.keys())
        cleaned = {k: v for k, v in d.items() if k in allowed}

        # Ensure required fields exist
        if "user_id" not in cleaned:
            cleaned["user_id"] = int(d.get("user_id", 0) or 0)

        return PlayerState(**cleaned)


@dataclass
class DuelState:
    """Turn-based PvP duel state."""

    a_id: int
    b_id: int
    channel_id: int
    started_at: int
    turn_id: int
    log: List[str]
    a_acted: bool = False
    b_acted: bool = False


class JsonStore:
    """Async JSON persistence with atomic writes."""

    def __init__(self):
        self._lock = asyncio.Lock()
        os.makedirs(DATA_DIR, exist_ok=True)

    async def _read_json(self, path: str, default: Any) -> Any:
        """Read JSON file asynchronously."""
        def _read():
            if not os.path.exists(path):
                return default
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        return await asyncio.to_thread(_read)

    async def _write_json(self, path: str, data: Any) -> None:
        """Write JSON file atomically."""
        def _write():
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, path)

        await asyncio.to_thread(_write)

    async def load_config(self) -> Dict[str, Any]:
        """Load configuration, merging with defaults."""
        async with self._lock:
            cfg = await self._read_json(CONFIG_FILE, DEFAULT_CONFIG)
            changed = False
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
                    changed = True
            if changed:
                await self._write_json(CONFIG_FILE, cfg)
            return cfg

    async def load_players(self) -> Dict[str, Any]:
        """Load all player data."""
        async with self._lock:
            return await self._read_json(PLAYERS_FILE, {})

    async def save_players(self, players: Dict[str, Any]) -> None:
        """Save all player data."""
        async with self._lock:
            await self._write_json(PLAYERS_FILE, players)
