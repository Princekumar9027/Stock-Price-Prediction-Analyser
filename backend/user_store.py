
import os
import hashlib
import secrets
import hmac
from functools import lru_cache

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

load_dotenv()

MIN_USERNAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 6
PBKDF2_ITERATIONS = 200_000


@lru_cache(maxsize=1)
def _get_collection():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not configured.")

    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    collection = client["stock_app"]["users"]
    collection.create_index("username_key", unique=True)
    return collection


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
    username = (username or "").strip()
    password = password or ""
    confirm_password = confirm_password or ""

    if not username or not password:
        return False, "Please fill in both username and password."
    if len(username) < MIN_USERNAME_LENGTH:
        return False, f"Username must be at least {MIN_USERNAME_LENGTH} characters."
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if password != confirm_password:
        return False, "Passwords do not match."

    try:
        collection = _get_collection()
        username_key = username.casefold()

        if collection.find_one({"username_key": username_key}, {"_id": 1}):
            return False, "That username is already taken. Please choose another."

        salt_hex, pw_hash = _hash_password(password)
        collection.insert_one({
            "username_key": username_key,
            "display_name": username,
            "salt": salt_hex,
            "hash": pw_hash,
        })
        return True, "Account created! You can now log in from the Login tab."

    except DuplicateKeyError:
        return False, "That username is already taken. Please choose another."
    except (PyMongoError, RuntimeError):
        return False, "Database error. Please try again later."


def verify_user(username: str, password: str) -> tuple[bool, str]:
    username = (username or "").strip()
    password = password or ""

    if not username or not password:
        return False, "Please enter both username and password."

    try:
        record = _get_collection().find_one({
            "username_key": username.casefold()
        })
        if record is None:
            return False, "No account found with that username. Please sign up first."

        _, pw_hash = _hash_password(password, record["salt"])
        if not hmac.compare_digest(pw_hash, record["hash"]):
            return False, "Incorrect password."

        return True, record["display_name"]

    except (PyMongoError, RuntimeError):
        return False, "Unable to connect to the database. Please try again later."