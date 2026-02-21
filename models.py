# Player data, persistence, and utility functions

import asyncio
import json
import os
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, List

from .config_default import DEFAULT_CONFIG

DATA_DIR = "data/wilderness"
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")


def _now() -> int:
    return int(time.time())


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def parse_chance(v: Any) -> float:
    """Parse probability from '1/50', '0.02', '2%', etc."""
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
    ground_items: List[List] = None  # [[item, qty, unix_timestamp], ...]
    npc_kills: Dict[str, int] = None  # {"NPC Name": kill_count, ...}
    presets: Dict[str, Dict[str, Any]] = None  # {"name": {"equipment": {...}, "inventory": {...}}}
    slayer_xp: int = 0
    slayer_points: int = 0
    slayer_tasks_done: int = 0
    slayer_task: Optional[Dict[str, Any]] = None  # {"npc": name, "npc_type": type, "total": N, "remaining": N}
    slayer_unlocks: List[str] = None
    slayer_blocked: List[str] = None
    alch_auto: List[str] = None
    pet_counts: Dict[str, int] = None
    consume_auto: List[str] = None
    ammo_qty: int = 0

    def __post_init__(self):
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
        if self.ground_items is None:
            self.ground_items = []
        if self.npc_kills is None:
            self.npc_kills = {}
        if self.presets is None:
            self.presets = {}
        if self.slayer_unlocks is None:
            self.slayer_unlocks = []
        if self.slayer_blocked is None:
            self.slayer_blocked = []
        if self.alch_auto is None:
            self.alch_auto = []
        if self.pet_counts is None:
            self.pet_counts = {}
        if self.consume_auto is None:
            self.consume_auto = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PlayerState":
        if not isinstance(d, dict):
            return PlayerState(user_id=0)

        allowed = set(PlayerState.__dataclass_fields__.keys())
        cleaned = {k: v for k, v in d.items() if k in allowed}

        if "user_id" not in cleaned:
            cleaned["user_id"] = int(d.get("user_id", 0) or 0)

        return PlayerState(**cleaned)


@dataclass
class DuelState:

    a_id: int
    b_id: int
    channel_id: int
    started_at: int
    turn_id: int
    log: List[str]
    a_acted: bool = False
    b_acted: bool = False


class JsonStore:

    def __init__(self):
        self._lock = asyncio.Lock()
        os.makedirs(DATA_DIR, exist_ok=True)

    async def _read_json(self, path: str, default: Any) -> Any:
        def _read():
            if not os.path.exists(path):
                return default
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        return await asyncio.to_thread(_read)

    async def _write_json(self, path: str, data: Any) -> None:
        def _write():
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, path)

        await asyncio.to_thread(_write)

    async def load_config(self) -> Dict[str, Any]:
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
        async with self._lock:
            return await self._read_json(PLAYERS_FILE, {})

    async def save_players(self, players: Dict[str, Any]) -> None:
        async with self._lock:
            await self._write_json(PLAYERS_FILE, players)
