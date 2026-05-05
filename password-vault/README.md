# Password Vault

A personal offline password manager built from scratch in Python. Two interfaces: a desktop GUI and a web app for phone access on the same network. No cloud, no third-party sync — the encrypted vault file stays on your machine.

---

## Features

- **AES-256-GCM encryption** — authenticated encryption, vault file is unreadable without the master password
- **Argon2id key derivation** — modern, memory-hard KDF; falls back to PBKDF2-SHA256 (480k iterations) if argon2-cffi isn't installed
- **Two interfaces** — desktop GUI (tkinter) and web app (Flask) for mobile access
- **Auto-lock** — locks after 5 minutes of inactivity, clears the key from memory
- **Clipboard auto-clear** — copied passwords cleared from clipboard after 30 seconds
- **Password history** — keeps last 3 versions of each password, restorable
- **Password health dashboard** — flags weak (<50 bits entropy), reused, and outdated (>365 days) passwords
- **Strength meter** — real-time entropy calculation as you type or generate

---

## How It Works

The vault file is stored at `~/.password_vault/vault.enc`. On unlock, the master password is passed through Argon2id with a random 32-byte salt to derive a 256-bit key. The entries list is serialised to JSON, encrypted with AES-GCM, and written to disk. The key never touches disk — it lives in memory only while the vault is unlocked, and is zeroed out on lock.

```
master password + salt ──► Argon2id ──► 256-bit key
entries (JSON)           ──► AES-256-GCM ──► vault.enc
```

---

## Usage

### Desktop app

```bash
# Install dependencies (Arch/Parrot)
sudo pacman -S python-argon2-cffi python-cryptography python-pyperclip xclip
# or
pip install argon2-cffi cryptography pyperclip

python password_vault.py
```

### Web app (phone access)

```bash
pip install flask argon2-cffi cryptography

python vault_web.py
```

The terminal will print your local IP. Open it on any device on the same network:

```
Local:   http://localhost:5000
Network: http://192.168.x.x:5000
```

> The web app is intended for local network use only. Do not expose it to the internet.

---

## File Structure

```
password-vault/
├── password_vault.py   # Desktop GUI (tkinter)
├── vault_web.py        # Web interface (Flask)
└── templates/
    └── index.html      # Single-page web UI
```

The vault data lives outside the repo at `~/.password_vault/`:

```
~/.password_vault/
├── vault.enc   # Encrypted entries (chmod 600)
├── salt.bin    # KDF salt (chmod 600)
└── hint.txt    # Optional lock screen hint (chmod 600)
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `cryptography` | AES-GCM encryption |
| `argon2-cffi` | Argon2id key derivation (recommended) |
| `pyperclip` + `xclip` | Clipboard access (desktop app) |
| `flask` | Web interface only |
