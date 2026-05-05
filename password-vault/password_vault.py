#!/usr/bin/env python3
# offline password vault — desktop GUI (tkinter)

import tkinter as tk
from tkinter import ttk, messagebox
import json, os, secrets, string, math, datetime
from pathlib import Path

# optional deps
try:
    from argon2.low_level import hash_secret_raw, Type
    ARGON2_OK = True
except ImportError:
    ARGON2_OK = False

try:
    import pyperclip
    CLIP_OK = True
except ImportError:
    CLIP_OK = False

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

def _write_secret(path: Path, data: bytes) -> None:
    path.write_bytes(data)
    os.chmod(path, 0o600)

# tunables
CLIPBOARD_CLEAR_MS = 30_000
AUTO_LOCK_MS       = 300_000
HISTORY_LIMIT      = 3
WEAK_BITS          = 50
OLD_DAYS           = 365

# crypto
def derive_key(password: str, salt: bytes) -> bytearray:
    if ARGON2_OK:
        return bytearray(hash_secret_raw(
            secret=password.encode(), salt=salt,
            time_cost=3, memory_cost=65536, parallelism=4,
            hash_len=32, type=Type.ID))
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480_000)
    return bytearray(kdf.derive(password.encode()))

def encrypt(data: list, key: bytes) -> bytes:
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, json.dumps(data).encode(), None)
    return nonce + ct

def decrypt(blob: bytes, key: bytes) -> list:
    nonce, ct = blob[:12], blob[12:]
    return json.loads(AESGCM(key).decrypt(nonce, ct, None))

# helpers
def gen_password(length=20) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(secrets.choice(chars) for _ in range(length))

def password_entropy(pw: str) -> float:
    if not pw: return 0.0
    pool = 0
    if any(c.islower() for c in pw): pool += 26
    if any(c.isupper() for c in pw): pool += 26
    if any(c.isdigit() for c in pw): pool += 10
    if any(c in string.punctuation for c in pw): pool += 32
    return len(pw) * math.log2(max(pool, 2))

def strength_label(bits: float):
    if bits < 28: return "Very weak",   "#ef4444"
    if bits < 36: return "Weak",        "#f97316"
    if bits < 50: return "Fair",        "#facc15"
    if bits < 70: return "Strong",      "#4ade80"
    return              "Very strong",  "#22d3ee"

def now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat()

def days_ago(iso: str) -> int:
    try:
        return (datetime.datetime.now(datetime.UTC) - datetime.datetime.fromisoformat(iso)).days
    except Exception:
        return 0

def health_report(entries: list) -> dict:
    pw_map: dict[str, list[int]] = {}
    for i, e in enumerate(entries):
        pw_map.setdefault(e.get("password",""), []).append(i)
    reused = {i for pw, idxs in pw_map.items() if len(idxs) > 1 for i in idxs}
    weak   = {i for i, e in enumerate(entries) if password_entropy(e.get("password","")) < WEAK_BITS}
    old    = {i for i, e in enumerate(entries) if days_ago(e.get("updated", now_iso())) > OLD_DAYS}
    return {"reused": reused, "weak": weak, "old": old}

# palette
BG      = "#1a1a2e"
PANEL   = "#16213e"
CARD    = "#0f3460"
ACCENT  = "#e94560"
ACCENT2 = "#533483"
TEXT    = "#eaeaea"
MUTED   = "#8892a4"
INBG    = "#0d2137"
SUCCESS = "#4ade80"
WARNING = "#facc15"
DANGER  = "#ef4444"

F       = ("Segoe UI", 11)
FB      = ("Segoe UI", 11, "bold")
FL      = ("Segoe UI", 14, "bold")
FT      = ("Segoe UI", 20, "bold")
FS      = ("Segoe UI", 9)
FM      = ("Consolas", 11)

# widget factories
def lbl(p, text, font=F, fg=TEXT, bg=BG, **kw):
    return tk.Label(p, text=text, font=font, fg=fg, bg=bg, **kw)

def ent(p, show="", width=30):
    return tk.Entry(p, show=show, width=width, font=F,
                    bg=INBG, fg=TEXT, insertbackground=TEXT,
                    relief="flat", bd=8, highlightthickness=1,
                    highlightbackground=CARD, highlightcolor=ACCENT)

def btn(p, text, cmd, bg=ACCENT, fg="#fff", width=None, padx=14, pady=6):
    kw = dict(text=text, command=cmd, bg=bg, fg=fg, font=FB,
              relief="flat", bd=0, cursor="hand2",
              activebackground=ACCENT2, activeforeground=fg, padx=padx, pady=pady)
    if width: kw["width"] = width
    return tk.Button(p, **kw)

def scrolled(parent):
    outer  = tk.Frame(parent, bg=BG)
    canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
    sb     = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner  = tk.Frame(canvas, bg=BG)
    wid    = canvas.create_window((0,0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
    def _scroll(e, d, c=canvas):
        if c.winfo_exists(): c.yview_scroll(d(e), "units")
    for seq, delta in (("<MouseWheel>", lambda e: -1*(e.delta//120)),
                       ("<Button-4>",   lambda _: -1),
                       ("<Button-5>",   lambda _:  1)):
        canvas.bind_all(seq, lambda e, d=delta: _scroll(e, d))
    return outer, inner

# lock screen
class LockScreen(tk.Frame):
    def __init__(self, master, on_unlock):
        super().__init__(master, bg=BG)
        self.on_unlock  = on_unlock
        self._is_new    = not VAULT_FILE.exists()
        self._hint_vis  = False
        self.hint_ent   = None
        self._hint_lbl  = None
        self._hint_btn  = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        card = tk.Frame(self, bg=PANEL, padx=44, pady=44)
        card.grid(row=0, column=0)
        lbl(card, "🔐", font=("Segoe UI",52), bg=PANEL).pack(pady=(0,6))
        lbl(card, "Password Vault", font=FT, bg=PANEL).pack()
        lbl(card, "Encrypted · Offline · Yours", font=FS, fg=MUTED, bg=PANEL).pack(pady=(4,6))
        if not ARGON2_OK:
            lbl(card, "⚠  argon2-cffi missing — using PBKDF2 fallback",
                font=FS, fg=WARNING, bg=PANEL).pack(pady=(0,8))
        lbl(card, "Master password", fg=MUTED, bg=PANEL).pack(anchor="w", pady=(10,0))
        self.pw = ent(card, show="●", width=34)
        self.pw.pack(pady=(4,4), ipady=6)
        self.pw.bind("<Return>", lambda _: self._unlock())
        self.pw.focus_set()
        self.err = lbl(card, "", fg=DANGER, bg=PANEL, font=FS)
        self.err.pack(pady=(0,12))
        btn(card, "Unlock Vault", self._unlock, width=30, pady=10).pack()
        if self._is_new:
            lbl(card, "Hint (optional)", fg=MUTED, bg=PANEL, font=FS).pack(anchor="w", pady=(16,2))
            self.hint_ent = ent(card, width=34)
            self.hint_ent.pack(ipady=4)
            lbl(card, "Shown on lock screen — never store the password itself.",
                font=FS, fg=MUTED, bg=PANEL).pack(pady=(2,0))
            lbl(card, "Any password creates a new vault.",
                font=FS, fg=MUTED, bg=PANEL).pack(pady=(10,0))
        else:
            self._build_hint_widget(card)

    def _build_hint_widget(self, card):
        if not HINT_FILE.exists():
            return
        hint_text = HINT_FILE.read_text().strip()
        if not hint_text:
            return
        self._hint_lbl = lbl(card, hint_text, fg=WARNING, bg=PANEL, font=FS, wraplength=280)
        self._hint_btn = btn(card, "💡 Show hint", self._toggle_hint,
                             bg=CARD, fg=MUTED, padx=10, pady=4)
        self._hint_btn.pack(pady=(14,0))

    def _toggle_hint(self):
        self._hint_vis = not self._hint_vis
        if self._hint_vis:
            self._hint_lbl.pack(pady=(4,0))
            self._hint_btn.config(text="🙈 Hide hint")
        else:
            self._hint_lbl.pack_forget()
            self._hint_btn.config(text="💡 Show hint")

    def _unlock(self):
        pw = self.pw.get()
        if not pw:
            self.err.config(text="Enter a master password.")
            return
        self.err.config(text="Deriving key…")
        self.update()
        salt = SALT_FILE.read_bytes() if SALT_FILE.exists() else os.urandom(32)
        if not SALT_FILE.exists():
            _write_secret(SALT_FILE, salt)
        key = derive_key(pw, salt)
        if VAULT_FILE.exists():
            try:
                entries = decrypt(VAULT_FILE.read_bytes(), key)
            except Exception:
                self.err.config(text="Wrong master password.")
                self.pw.delete(0, "end")
                return
        else:
            entries = []
            _write_secret(VAULT_FILE, encrypt(entries, key))
            hint = self.hint_ent.get().strip() if self.hint_ent else ""
            if hint:
                _write_secret(HINT_FILE, hint.encode())
        self.pw.delete(0, "end")
        self.err.config(text="")
        self.on_unlock(key, entries)

# entry dialog
class EntryDialog(tk.Toplevel):
    def __init__(self, master, on_save, entry=None):
        super().__init__(master)
        self.on_save = on_save
        self.entry   = entry or {}
        self.title("Edit Entry" if entry else "Add Entry")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self.after(80, self._center)

    def _center(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width()  - self.winfo_width())  // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        p = dict(padx=24, pady=5)
        e = self.entry
        lbl(self, "Edit Entry" if e else "Add Entry", font=FL, bg=BG).pack(pady=(20,8))
        self.vars = {}
        for txt, key in [("Site / Name *","name"),("Username / Email","username"),
                          ("URL","url"),("Notes","notes")]:
            lbl(self, txt, fg=MUTED, bg=BG).pack(anchor="w", **p)
            w = ent(self, width=38)
            w.insert(0, e.get(key,""))
            w.pack(ipady=5, **p)
            self.vars[key] = w

        lbl(self, "Password *", fg=MUTED, bg=BG).pack(anchor="w", **p)
        pw_row = tk.Frame(self, bg=BG)
        pw_row.pack(**p)
        self.pw_ent = ent(pw_row, show="●", width=28)
        self.pw_ent.insert(0, e.get("password",""))
        self.pw_ent.pack(side="left", ipady=5)
        self.pw_ent.bind("<KeyRelease>", lambda _: self._update_meter())
        self._vis = False

        def toggle():
            self._vis = not self._vis
            self.pw_ent.config(show="" if self._vis else "●")
            eye.config(text="🙈" if self._vis else "👁")
        eye = tk.Button(pw_row, text="👁", command=toggle, bg=CARD, fg=TEXT,
                        relief="flat", bd=0, font=("Segoe UI",12), cursor="hand2", padx=6)
        eye.pack(side="left", padx=(4,0))

        def gen():
            self.pw_ent.delete(0,"end")
            self.pw_ent.insert(0, gen_password())
            self.pw_ent.config(show="")
            self._vis = True; eye.config(text="🙈")
            self._update_meter()
        btn(pw_row, "Generate", gen, bg=CARD, fg=ACCENT, padx=8, pady=4).pack(side="left", padx=(6,0))

        # strength meter
        mr = tk.Frame(self, bg=BG)
        mr.pack(fill="x", padx=24, pady=(2,4))
        self.bar = tk.Canvas(mr, height=6, bg=CARD, highlightthickness=0)
        self.bar.pack(fill="x")
        self.slbl = lbl(mr, "", font=FS, fg=MUTED, bg=BG)
        self.slbl.pack(anchor="w")
        self._update_meter()

        # history preview
        hist = e.get("history", [])
        if hist:
            lbl(self, "Password history", fg=MUTED, bg=BG).pack(anchor="w", **p)
            for h in hist:
                hr = tk.Frame(self, bg=PANEL, padx=10, pady=4)
                hr.pack(fill="x", padx=24, pady=2)
                lbl(hr, "●"*min(len(h["password"]),12), font=FM, fg=MUTED, bg=PANEL).pack(side="left")
                lbl(hr, f"{days_ago(h.get('updated',''))}d ago", font=FS, fg=MUTED, bg=PANEL).pack(side="right")

        br = tk.Frame(self, bg=BG)
        br.pack(pady=20)
        btn(br, "Save",   self._save,     width=14).pack(side="left", padx=6)
        btn(br, "Cancel", self.destroy, bg=CARD, fg=TEXT, width=14).pack(side="left", padx=6)

    def _update_meter(self):
        bits  = password_entropy(self.pw_ent.get())
        sl, sc = strength_label(bits)
        self.slbl.config(text=f"{sl}  ({bits:.0f} bits)", fg=sc)
        self.bar.update_idletasks()
        w = self.bar.winfo_width() or 300
        filled = min(w, int(w * bits / 100))
        self.bar.delete("all")
        self.bar.create_rectangle(0, 0, filled, 6, fill=sc, outline="")

    def _save(self):
        name = self.vars["name"].get().strip()
        pw   = self.pw_ent.get()
        if not name:
            messagebox.showwarning("Missing", "Site / Name is required.", parent=self); return
        if not pw:
            messagebox.showwarning("Missing", "Password is required.", parent=self); return
        old_pw   = self.entry.get("password","")
        old_hist = list(self.entry.get("history",[]))
        if old_pw and old_pw != pw:
            old_hist.insert(0, {"password": old_pw, "updated": self.entry.get("updated", now_iso())})
            old_hist = old_hist[:HISTORY_LIMIT]
        self.on_save({
            "name":     name,
            "username": self.vars["username"].get().strip(),
            "url":      self.vars["url"].get().strip(),
            "notes":    self.vars["notes"].get().strip(),
            "password": pw,
            "updated":  now_iso(),
            "history":  old_hist,
        })
        self.destroy()

# health dashboard
class HealthDashboard(tk.Toplevel):
    def __init__(self, master, entries, on_goto):
        super().__init__(master)
        self.entries = entries
        self.on_goto = on_goto
        self.title("Password Health")
        self.configure(bg=BG)
        self.geometry("580x540")
        self.grab_set()
        self._build()
        self.after(80, self._center)

    def _center(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width()  - self.winfo_width())  // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        report = health_report(self.entries)
        total  = len(self.entries)
        n_issues = len(report["reused"] | report["weak"] | report["old"])
        score  = max(0, 100 - int(n_issues / max(total,1) * 100))

        hdr = tk.Frame(self, bg=PANEL, padx=20, pady=16)
        hdr.pack(fill="x")
        lbl(hdr, "🛡  Password Health", font=FL, bg=PANEL).pack(side="left")
        sc = SUCCESS if score >= 80 else (WARNING if score >= 50 else DANGER)
        lbl(hdr, f"{score} / 100", font=FL, fg=sc, bg=PANEL).pack(side="right")

        stats = tk.Frame(self, bg=BG, pady=12, padx=16)
        stats.pack(fill="x")
        for i, (title, count, col) in enumerate([
            ("Total",   total,                    TEXT),
            ("Reused",  len(report["reused"]),    DANGER),
            ("Weak",    len(report["weak"]),       WARNING),
            ("Outdated",len(report["old"]),        "#f97316"),
        ]):
            c = tk.Frame(stats, bg=CARD, padx=12, pady=10)
            c.grid(row=0, column=i, padx=4, sticky="ew")
            stats.columnconfigure(i, weight=1)
            lbl(c, title,     font=FS, fg=MUTED, bg=CARD).pack()
            lbl(c, str(count),font=FL, fg=col,   bg=CARD).pack()

        outer, inner = scrolled(self)
        outer.pack(fill="both", expand=True, padx=16, pady=(8,16))

        sections = [
            ("🔁  Reused passwords",  report["reused"], DANGER,    f"Same password on multiple sites."),
            ("💀  Weak passwords",    report["weak"],   WARNING,   f"Entropy below {WEAK_BITS} bits."),
            ("⏰  Outdated passwords", report["old"],   "#f97316", f"Not changed in over {OLD_DAYS} days."),
        ]
        any_issue = False
        for stitle, idx_set, col, desc in sections:
            if not idx_set: continue
            any_issue = True
            lbl(inner, stitle, font=FB, fg=col, bg=BG).pack(anchor="w", pady=(12,2))
            lbl(inner, desc,   font=FS, fg=MUTED, bg=BG).pack(anchor="w", pady=(0,6))
            for i in sorted(idx_set):
                e   = self.entries[i]
                row = tk.Frame(inner, bg=CARD, padx=12, pady=8)
                row.pack(fill="x", pady=2)
                lbl(row, e.get("name","?"),    font=FB, bg=CARD).pack(side="left")
                lbl(row, e.get("username",""), font=FS, fg=MUTED, bg=CARD).pack(side="left", padx=8)
                def fix(idx=i):
                    self.destroy()
                    self.on_goto(idx)
                btn(row, "Fix →", fix, bg=ACCENT2, fg=TEXT, padx=8, pady=2).pack(side="right")

        if not any_issue:
            lbl(inner, "✅  All passwords look healthy!", font=FB, fg=SUCCESS, bg=BG).pack(pady=40)

# vault screen
class VaultScreen(tk.Frame):
    def __init__(self, master, key, entries, on_lock):
        super().__init__(master, bg=BG)
        self.key       = key
        self.entries   = entries
        self.on_lock   = on_lock
        self._clip_job = None
        self._lock_job = None
        self._build()
        self._refresh()
        self._reset_lock_timer()

    def _build(self):
        top = tk.Frame(self, bg=PANEL, padx=16, pady=10)
        top.pack(fill="x")
        lbl(top, "🔐  Vault", font=FL, bg=PANEL).pack(side="left")
        btn(top, "Lock",      self._lock,     bg=CARD,    fg=ACCENT, padx=10, pady=4).pack(side="right", padx=4)
        btn(top, "+ Add",     self._add,                  padx=10,   pady=4).pack(side="right", padx=4)
        btn(top, "🛡 Health", self._health,  bg=ACCENT2, fg=TEXT,   padx=10, pady=4).pack(side="right", padx=4)
        btn(top, "💡 Hint",   self._set_hint, bg=CARD,   fg=MUTED,  padx=10, pady=4).pack(side="right", padx=4)

        sr = tk.Frame(self, bg=BG, pady=10, padx=16)
        sr.pack(fill="x")
        lbl(sr, "🔍 ", fg=MUTED, bg=BG).pack(side="left")
        self.sv = tk.StringVar()
        self.sv.trace_add("write", lambda *_: (self._refresh(), self._reset_lock_timer()))
        se = tk.Entry(sr, textvariable=self.sv, font=F,
                      bg=INBG, fg=TEXT, insertbackground=TEXT, relief="flat",
                      bd=6, highlightthickness=1, highlightbackground=CARD, highlightcolor=ACCENT)
        se.pack(fill="x", ipady=5)

        self.list_outer, self.list_inner = scrolled(self)
        self.list_outer.pack(fill="both", expand=True, padx=16, pady=(0,4))

        self.status = lbl(self, "", font=FS, fg=SUCCESS, bg=BG)
        self.status.pack(pady=(0,6))

        self.bind_all("<Button-1>", lambda _: self._reset_lock_timer())
        self.bind_all("<Key>",      lambda _: self._reset_lock_timer())

    def _refresh(self):
        q = self.sv.get().lower()
        for w in self.list_inner.winfo_children():
            w.destroy()
        filtered = [e for e in self.entries if
                    q in e.get("name","").lower() or
                    q in e.get("username","").lower() or
                    q in e.get("url","").lower()]
        report = health_report(self.entries)
        if not filtered:
            msg = "No entries yet — click + Add." if not self.entries else f'No results for "{q}".'
            lbl(self.list_inner, msg, fg=MUTED, bg=BG).pack(pady=40)
            return
        for entry in filtered:
            self._entry_card(self.list_inner, entry, self.entries.index(entry), report)

    def _entry_card(self, parent, entry, idx, report):
        issues = []
        if idx in report["reused"]: issues.append(("reused", DANGER))
        if idx in report["weak"]:   issues.append(("weak",   WARNING))
        if idx in report["old"]:    issues.append(("old",    "#f97316"))

        card = tk.Frame(parent, bg=CARD, padx=14, pady=10)
        card.pack(fill="x", pady=3)

        left = tk.Frame(card, bg=CARD)
        left.pack(side="left", fill="x", expand=True)

        nr = tk.Frame(left, bg=CARD)
        nr.pack(anchor="w")
        lbl(nr, entry.get("name","Unnamed"), font=FB, bg=CARD).pack(side="left")
        for it, ic in issues:
            lbl(nr, f"  [{it}]", font=FS, fg=ic, bg=CARD).pack(side="left")

        user = entry.get("username","") or entry.get("url","")
        lbl(left, user, font=FS, fg=MUTED, bg=CARD).pack(anchor="w")
        age = days_ago(entry.get("updated", now_iso()))
        lbl(left, f"Updated {age}d ago", font=FS, fg=MUTED, bg=CARD).pack(anchor="w")

        actions = tk.Frame(card, bg=CARD)
        actions.pack(side="right")

        btn(actions, "Copy",  lambda i=idx: self._copy_pw(i),  bg=ACCENT2, fg=TEXT, padx=8, pady=3).pack(side="left", padx=2)
        btn(actions, "Show",  lambda i=idx: self._show_pw(i),  bg=PANEL,   fg=TEXT, padx=8, pady=3).pack(side="left", padx=2)
        btn(actions, "Edit",  lambda i=idx: EntryDialog(self, lambda d,_i=i: self._save_edit(_i,d), self.entries[i]),
                                                                bg=PANEL,   fg=TEXT, padx=8, pady=3).pack(side="left", padx=2)
        btn(actions, "Del",   lambda i=idx: self._delete(i),   bg=BG,      fg=ACCENT, padx=8, pady=3).pack(side="left", padx=2)

    def _show_pw(self, idx):
        e   = self.entries[idx]
        win = tk.Toplevel(self)
        win.title("Password")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()

        lbl(win, e.get("name",""), font=FB, bg=BG).pack(pady=(20,4), padx=28)
        lbl(win, "Current password", fg=MUTED, bg=BG, font=FS).pack(anchor="w", padx=28)

        pr = tk.Frame(win, bg=BG)
        pr.pack(padx=28, pady=(4,0))
        pe = tk.Entry(pr, font=FM, bg=INBG, fg=SUCCESS, relief="flat",
                      bd=8, width=28, justify="center")
        pe.insert(0, e["password"])
        pe.config(state="readonly")
        pe.pack(side="left", ipady=6)
        sl, sc = strength_label(password_entropy(e["password"]))
        lbl(pr, f" {sl}", fg=sc, bg=BG, font=FS).pack(side="left", padx=6)

        hist = e.get("history", [])
        if hist:
            lbl(win, "Previous passwords", fg=MUTED, bg=BG, font=FS).pack(anchor="w", padx=28, pady=(12,4))
            for h in hist:
                hr = tk.Frame(win, bg=PANEL, padx=12, pady=6)
                hr.pack(fill="x", padx=28, pady=2)
                lbl(hr, "●"*min(len(h["password"]),14), font=FM, fg=MUTED, bg=PANEL).pack(side="left")
                lbl(hr, f"{days_ago(h.get('updated',''))}d ago", font=FS, fg=MUTED, bg=PANEL).pack(side="right")
                def restore(pw=h["password"], i=idx):
                    if messagebox.askyesno("Restore", "Restore this password?", parent=win):
                        win.destroy()
                        updated = {**self.entries[i], "password": pw}
                        self._save_edit(i, updated)
                btn(hr, "Restore", restore, bg=CARD, fg=ACCENT, padx=6, pady=2).pack(side="right", padx=6)

        btn(win, "Copy & Close",
            lambda: [self._copy_pw(idx), win.destroy()]).pack(pady=16)

    def _add(self):
        EntryDialog(self, self._save_new)

    def _save_new(self, data):
        data.setdefault("updated", now_iso())
        data.setdefault("history", [])
        self.entries.insert(0, data)
        self._persist()
        self._refresh()
        self._flash(f'"{data["name"]}" added.')

    def _save_edit(self, idx, data):
        self.entries[idx] = data
        self._persist()
        self._refresh()
        self._flash(f'"{data["name"]}" updated.')

    def _delete(self, idx):
        if messagebox.askyesno("Delete", f'Delete "{self.entries[idx]["name"]}"?'):
            self.entries.pop(idx)
            self._persist()
            self._refresh()
            self._flash("Entry deleted.")

    def _health(self):
        def goto(idx):
            EntryDialog(self, lambda d: self._save_edit(idx, d), self.entries[idx])
        HealthDashboard(self, self.entries, goto)

    def _persist(self):
        _write_secret(VAULT_FILE, encrypt(self.entries, self.key))

    def _copy_pw(self, idx):
        if CLIP_OK:
            pyperclip.copy(self.entries[idx]["password"])
            self._flash(f"Copied! Clears in {CLIPBOARD_CLEAR_MS//1000}s.")
            if self._clip_job: self.after_cancel(self._clip_job)
            self._clip_job = self.after(CLIPBOARD_CLEAR_MS, self._clear_clip)
        else:
            messagebox.showinfo("Password", self.entries[idx]["password"])

    def _clear_clip(self):
        if CLIP_OK: pyperclip.copy("")
        self._flash("Clipboard cleared.")
        self._clip_job = None

    def _reset_lock_timer(self):
        if self._lock_job: self.after_cancel(self._lock_job)
        self._lock_job = self.after(AUTO_LOCK_MS, self._auto_lock)

    def _auto_lock(self):
        self._flash("Auto-locking due to inactivity…")
        self.after(800, self._lock)

    def _lock(self):
        if self._clip_job:
            self.after_cancel(self._clip_job)
            if CLIP_OK: pyperclip.copy("")
        if self._lock_job: self.after_cancel(self._lock_job)
        self.entries.clear()
        if self.key is not None:
            self.key[:] = b'\x00' * len(self.key)
        self.key = None
        self.on_lock()

    def _set_hint(self):
        win = tk.Toplevel(self)
        win.title("Password Hint")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        current = HINT_FILE.read_text().strip() if HINT_FILE.exists() else ""
        lbl(win, "Password Hint", font=FL, bg=BG).pack(pady=(20,4), padx=28)
        lbl(win, "Shown on the lock screen. Never store the password itself.",
            font=FS, fg=MUTED, bg=BG).pack(padx=28)
        e = ent(win, width=38)
        e.insert(0, current)
        e.pack(pady=(10,0), padx=28, ipady=5)
        def save():
            text = e.get().strip()
            if text:
                _write_secret(HINT_FILE, text.encode())
            elif HINT_FILE.exists():
                HINT_FILE.unlink()
            win.destroy()
            self._flash("Hint saved." if text else "Hint cleared.")
        br = tk.Frame(win, bg=BG)
        br.pack(pady=20)
        btn(br, "Save",   save,        width=12).pack(side="left", padx=6)
        btn(br, "Cancel", win.destroy, bg=CARD, fg=TEXT, width=12).pack(side="left", padx=6)
        win.after(80, lambda: (win.update_idletasks(),
            win.geometry(f"+{self.winfo_rootx()+(self.winfo_width()-win.winfo_width())//2}"
                         f"+{self.winfo_rooty()+(self.winfo_height()-win.winfo_height())//2}")))

    def _flash(self, msg, ms=4000):
        self.status.config(text=msg)
        self.after(ms, lambda: self.status.config(text=""))

# app shell
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Vault v2")
        self.geometry("820x600")
        self.minsize(660, 480)
        self.configure(bg=BG)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar",
                        background=CARD, troughcolor=BG,
                        bordercolor=BG, arrowcolor=MUTED)
        self._show_lock()

    def _show_lock(self):
        for w in self.winfo_children(): w.destroy()
        LockScreen(self, self._on_unlock).pack(fill="both", expand=True)

    def _on_unlock(self, key, entries):
        for w in self.winfo_children(): w.destroy()
        VaultScreen(self, key, entries, self._show_lock).pack(fill="both", expand=True)

if __name__ == "__main__":
    missing = []
    if not ARGON2_OK: missing.append(("argon2-cffi",    "python-argon2-cffi"))
    if not CLIP_OK:   missing.append(("pyperclip",      "python-pyperclip"))
    if missing:
        libs = " ".join(p for _, p in missing)
        print(f"Missing packages: {', '.join(n for n,_ in missing)}")
        print(f"Fix:  sudo pacman -S {libs} xclip\n")
    App().mainloop()
