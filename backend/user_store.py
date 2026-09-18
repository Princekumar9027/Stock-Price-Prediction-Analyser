"""
user_store.py
--------------
Handles user self-registration (sign up) and login verification.

Users are stored in users.json in the project root. Passwords are
NEVER stored in plain text - each password is hashed with PBKDF2-HMAC-SHA256
using a unique random salt per user.

This replaces the old "one random login per run" approach: now anyone
can create their own account, and it persists across restarts.
"""

import json
import os
import hashlib
import secrets

USERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "users.json",
)

MIN_USERNAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 6
PBKDF2_ITERATIONS = 200_000


def _load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_users(users: dict) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _hash_password(password: str, salt_hex: str = None) -> tuple[str, str]:
    if salt_hex is None:
        salt_hex = secrets.token_hex(16)

    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        PBKDF2_ITERATIONS,
    ).hex()

    return salt_hex, pw_hash


def register_user(username: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """
    Creates a new account. Returns (success, message).
    """
    username = (username or "").strip()
    password = password or ""

    if not username or not password:
        return False, "❌ Please fill in both username and password."

    if len(username) < MIN_USERNAME_LENGTH:
        return False, f"❌ Username must be at least {MIN_USERNAME_LENGTH} characters."

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"❌ Password must be at least {MIN_PASSWORD_LENGTH} characters."

    if password != confirm_password:
        return False, "❌ Passwords do not match."

    users = _load_users()

    if username.lower() in users:
        return False, "❌ That username is already taken. Please choose another."

    salt_hex, pw_hash = _hash_password(password)
    users[username.lower()] = {
        "display_name": username,
        "salt": salt_hex,
        "hash": pw_hash,
    }
    _save_users(users)

    return True, "✅ Account created! You can now log in from the Login tab."


def verify_user(username: str, password: str) -> tuple[bool, str]:
    """
    Checks login credentials. Returns (success, message_or_display_name).
    """
    username = (username or "").strip()
    password = password or ""

    if not username or not password:
        return False, "❌ Please enter both username and password."

    users = _load_users()
    record = users.get(username.lower())

    if record is None:
        return False, "❌ No account found with that username. Please sign up first."

    _, pw_hash = _hash_password(password, record["salt"])

    if pw_hash != record["hash"]:
        return False, "❌ Incorrect password."

    return True, record["display_name"]
