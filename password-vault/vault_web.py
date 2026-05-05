#!/usr/bin/env python3
# password vault — flask web interface for phone/local network access

import os, json, datetime, secrets as _secrets
from pathlib import Path
from flask import Flask, request, jsonify, render_template, make_response

try:
    from argon2.low_level import hash_secret_raw, Type
    ARGON2_OK = True
except ImportError:
    ARGON2_OK = False

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# paths
VAULT_DIR  = Path.home() / ".password_vault"
VAULT_FILE = VAULT_DIR / "vault.enc"
SALT_FILE  = VAULT_DIR / "salt.bin"
HINT_FILE  = VAULT_DIR / "hint.txt"
VAULT_DIR.mkdir(mode=0o700, exist_ok=True)
os.chmod(VAULT_DIR, 0o700)

AUTO_LOCK_SECONDS = 300

# flask setup
app = Flask(__name__)
_sessions: dict = {}   # token -> {key, entries, expires}

# helpers
def _write_secret(path: Path, data: bytes) -> None:
    path.write_bytes(data)
    os.chmod(path, 0o600)

def derive_key(password: str, salt: bytes) -> bytearray:
    if ARGON2_OK:
        return bytearray(hash_secret_raw(
            secret=password.encode(), salt=salt,
            time_cost=3, memory_cost=65536, parallelism=4,
            hash_len=32, type=Type.ID))
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480_000)
    return bytearray(kdf.derive(password.encode()))

def encrypt(data: list, key) -> bytes:
    nonce = os.urandom(12)
    ct = AESGCM(bytes(key)).encrypt(nonce, json.dumps(data).encode(), None)
    return nonce + ct

def decrypt(blob: bytes, key) -> list:
    nonce, ct = blob[:12], blob[12:]
    return json.loads(AESGCM(bytes(key)).decrypt(nonce, ct, None))

def now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat()

def _get_session():
    token = request.cookies.get("vault_token")
    if not token or token not in _sessions:
        return None
    s = _sessions[token]
    if datetime.datetime.now(datetime.UTC) > s["expires"]:
        del _sessions[token]
        return None
    s["expires"] = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=AUTO_LOCK_SECONDS)
    return s

def _new_session(key, entries) -> str:
    token = _secrets.token_urlsafe(32)
    _sessions[token] = {
        "key":     key,
        "entries": entries,
        "expires": datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=AUTO_LOCK_SECONDS),
    }
    return token

# routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def status():
    s = _get_session()
    return jsonify({"unlocked": s is not None, "is_new": not VAULT_FILE.exists()})

@app.route("/api/hint")
def get_hint():
    return jsonify({"hint": HINT_FILE.read_text().strip() if HINT_FILE.exists() else ""})

@app.route("/api/hint", methods=["POST"])
def set_hint():
    if not _get_session():
        return jsonify({"error": "locked"}), 401
    text = (request.get_json() or {}).get("hint", "").strip()
    if text:
        _write_secret(HINT_FILE, text.encode())
    elif HINT_FILE.exists():
        HINT_FILE.unlink()
    return jsonify({"ok": True})

@app.route("/api/unlock", methods=["POST"])
def unlock():
    data = request.get_json() or {}
    pw = data.get("password", "")
    if not pw:
        return jsonify({"error": "Enter a master password."}), 400

    salt = SALT_FILE.read_bytes() if SALT_FILE.exists() else os.urandom(32)
    if not SALT_FILE.exists():
        _write_secret(SALT_FILE, salt)

    key = derive_key(pw, salt)

    if VAULT_FILE.exists():
        try:
            entries = decrypt(VAULT_FILE.read_bytes(), key)
        except Exception:
            return jsonify({"error": "Wrong master password."}), 401
    else:
        entries = []
        _write_secret(VAULT_FILE, encrypt(entries, key))
        hint = data.get("hint", "").strip()
        if hint:
            _write_secret(HINT_FILE, hint.encode())

    token = _new_session(key, entries)
    resp = make_response(jsonify({"ok": True}))
    resp.set_cookie("vault_token", token, httponly=True, samesite="Strict")
    return resp

@app.route("/api/lock", methods=["POST"])
def lock():
    token = request.cookies.get("vault_token")
    if token and token in _sessions:
        s = _sessions.pop(token)
        if s.get("key"):
            s["key"][:] = b'\x00' * len(s["key"])
    resp = make_response(jsonify({"ok": True}))
    resp.delete_cookie("vault_token")
    return resp

@app.route("/api/entries")
def list_entries():
    s = _get_session()
    if not s:
        return jsonify({"error": "locked"}), 401
    return jsonify(s["entries"])

@app.route("/api/entries", methods=["POST"])
def add_entry():
    s = _get_session()
    if not s:
        return jsonify({"error": "locked"}), 401
    entry = request.get_json() or {}
    entry.setdefault("updated", now_iso())
    entry.setdefault("history", [])
    s["entries"].insert(0, entry)
    _write_secret(VAULT_FILE, encrypt(s["entries"], s["key"]))
    return jsonify({"ok": True})

@app.route("/api/entries/<int:idx>", methods=["PUT"])
def update_entry(idx):
    s = _get_session()
    if not s:
        return jsonify({"error": "locked"}), 401
    if idx < 0 or idx >= len(s["entries"]):
        return jsonify({"error": "not found"}), 404
    s["entries"][idx] = request.get_json() or {}
    _write_secret(VAULT_FILE, encrypt(s["entries"], s["key"]))
    return jsonify({"ok": True})

@app.route("/api/entries/<int:idx>", methods=["DELETE"])
def delete_entry(idx):
    s = _get_session()
    if not s:
        return jsonify({"error": "locked"}), 401
    if idx < 0 or idx >= len(s["entries"]):
        return jsonify({"error": "not found"}), 404
    s["entries"].pop(idx)
    _write_secret(VAULT_FILE, encrypt(s["entries"], s["key"]))
    return jsonify({"ok": True})

# main
if __name__ == "__main__":
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    print(f"\n  Local:   http://localhost:5000")
    print(f"  Network: http://{local_ip}:5000  ← open this on your phone\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
