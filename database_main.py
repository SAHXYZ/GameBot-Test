# filename: database.py
"""
Thread-safe JSON database system for GameBot.
Fully compatible with your existing data.json.
"""

import json, os
from threading import Lock
from copy import deepcopy

DB_PATH = "database"
DB_FILE = os.path.join(DB_PATH, "data.json")
BACKUP_FILE = os.path.join(DB_PATH, "data_backup.json")

_lock = Lock()

# Full schema for new users
def _default_user():
    return {
        "coins": 0,
        "group_msgs": 0,
        "cooldowns": {},
        "profile": {},

        # additional fields used by your modules
        "fight_wins": 0,
        "rob_success": 0,
        "rob_fail": 0,
        "messages": 0,
        "badges": [],
        "inventory": []
    }

def _ensure_storage():
    os.makedirs(DB_PATH, exist_ok=True)
    if not os.path.isfile(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)

def _load():
    _ensure_storage()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save(data):
    _ensure_storage()

    # backup old DB (direct read instead of calling _load())
    try:
        if os.path.isfile(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                old = json.load(f)
            with open(BACKUP_FILE, "w", encoding="utf-8") as bf:
                json.dump(old, bf, indent=2)
    except Exception:
        pass

    # write new DB
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class DB:
    def __init__(self):
        _ensure_storage()
        self._data = _load()

    def get_user(self, uid):
        """
        Returns a deep copy of user.
        Auto-creates & auto-fills missing fields.
        """
        key = str(uid)
        with _lock:
            if key not in self._data:
                self._data[key] = _default_user()
                _save(self._data)

            # auto-fill fields missing in older accounts
            user = self._data[key]
            defaults = _default_user()

            for field, value in defaults.items():
                if field not in user:
                    user[field] = deepcopy(value)

            _save(self._data)
            return deepcopy(user)

    def update_user(self, uid, data: dict):
        """
        Merge + save.
        WARNING: shallow merge! Nested dicts overwrite completely.
        """
        key = str(uid)
        with _lock:
            user = self._data.get(key, _default_user())

            # shallow merge
            user.update(data)
            self._data[key] = user

            _save(self._data)

    def save(self):
        """Force save existing memory to disk."""
        with _lock:
            _save(self._data)


# Singleton instance
db = DB()
