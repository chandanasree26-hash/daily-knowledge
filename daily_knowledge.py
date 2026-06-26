#!/usr/bin/env python3
"""
Daily Knowledge Reminder
Shows a popup every morning with something new to learn.
Opens the topic in Chrome when clicked.
"""

import json
import os
import sys
import random
import hashlib
import webbrowser
import subprocess
import platform
import tkinter as tk
from tkinter import font as tkfont
from tkinter import simpledialog, messagebox
from datetime import date
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
def resource_path(filename):
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / filename
    return Path(__file__).parent.resolve() / filename


TOPICS_FILE = resource_path("topics.json")
STATE_FILE = Path.home() / ".daily_knowledge_state.json"

# ── Category colours (background, foreground) ─────────────────────────────────
CATEGORY_COLOURS = {
    "Politics":        ("#E8EAF6", "#3949AB"),
    "Economics":       ("#FFF3E0", "#E65100"),
    "History":         ("#FCE4EC", "#AD1457"),
    "Countries":       ("#E0F2F1", "#00695C"),
    "Science & Nature":("#E8F5E9", "#2E7D32"),
    "Technology":      ("#EDE7F6", "#4527A0"),
    "Engineering":     ("#E3F2FD", "#1565C0"),
    "Society":         ("#FFF8E1", "#F57F17"),
    "Philosophy":      ("#F3E5F5", "#6A1B9A"),
}
DEFAULT_COLOUR = ("#F5F5F5", "#333333")

# ── State helpers ─────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"shown": {}, "last_date": ""}

def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def load_topics() -> list:
    data = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    return data["topics"]

def pick_topic(topics: list, state: dict) -> dict:
    """
    Pick a topic for today. Rules:
      1. Each calendar day always returns the same topic (deterministic seed).
      2. Try not to repeat recently shown topics (last 30).
    """
    today = str(date.today())

    # Already picked for today? Return same one.
    if state.get("last_date") == today and state.get("today_index") is not None:
        idx = state["today_index"]
        if 0 <= idx < len(topics):
            return topics[idx]

    # Build pool excluding recently shown
    shown_indices = set(state.get("shown", {}).values())
    pool = [i for i in range(len(topics)) if i not in shown_indices]

    # If we've exhausted everything, reset
    if not pool:
        state["shown"] = {}
        pool = list(range(len(topics)))

    # Deterministic pick from pool based on today's date
    seed_val = int(hashlib.md5(today.encode()).hexdigest(), 16)
    chosen_idx = pool[seed_val % len(pool)]

    # Save
    state["shown"][today] = chosen_idx
    state["last_date"] = today
    state["today_index"] = chosen_idx
    save_state(state)

    return topics[chosen_idx]
 
# ── Browser opener ────────────────────────────────────────────────────────────

def open_in_chrome(url: str) -> None:
    system = platform.system()
    try:
        if system == "Windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            ]
            for p in chrome_paths:
                if os.path.exists(p):
                    subprocess.Popen([p, url])
                    return
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", "Google Chrome", url])
            return
        elif system == "Linux":
            for cmd in ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]:
                try:
                    subprocess.Popen([cmd, url])
                    return
                except FileNotFoundError:
                    continue
    except Exception:
        pass
    # Fallback: system default browser
    webbrowser.open(url)

# ── GUI ───────────────────────────────────────────────────────────────────────

class KnowledgePopup:
    # Dimensions & colours
    WIDTH  = 480
    BG     = "#FFFFFF"
    ACCENT = "#1A73E8"

    def __init__(self, topic: dict):
        self.topic = topic
        self.root  = tk.Tk()
        self._build()

    def _build(self):
        root = self.root
        APP_VERSION = "v1.0"
        root.title(f"Daily Knowledge {APP_VERSION}")
        root.configure(bg=self.BG)
        root.resizable(False, False)

        # Remove default window chrome on supported platforms
        root.overrideredirect(False)

        # Fonts
        title_font  = tkfont.Font(family="Segoe UI" if platform.system()=="Windows" else "Helvetica",
                                   size=15, weight="bold")
        body_font   = tkfont.Font(family="Segoe UI" if platform.system()=="Windows" else "Helvetica",
                                   size=11)
        small_font  = tkfont.Font(family="Segoe UI" if platform.system()=="Windows" else "Helvetica",
                                   size=10)
        btn_font    = tkfont.Font(family="Segoe UI" if platform.system()=="Windows" else "Helvetica",
                                   size=11, weight="bold")

        # ── Header bar ───────────────────────────────────────────────────────
        header = tk.Frame(root, bg="#DE53DE", height=6)
        header.pack(fill="x")

        # ── Top section ───────────────────────────────────────────────────────
        top = tk.Frame(root, bg=self.BG, padx=24, pady=18)
        top.pack(fill="x")

        # Greeting
        tk.Label(top, text="☀️  Good morning! Time to learn something new!",
                 bg=self.BG, fg="#3067DE", font=small_font,
                 anchor="w").pack(fill="x")

        # Category badge
        cat = self.topic.get("category", "General")
        bg_c, fg_c = CATEGORY_COLOURS.get(cat, DEFAULT_COLOUR)
        badge_frame = tk.Frame(top, bg=self.BG)
        badge_frame.pack(anchor="w", pady=(10, 0))
        tk.Label(badge_frame, text=f"  {cat}  ",
                 bg=bg_c, fg=fg_c, font=small_font,
                 padx=4, pady=3,
                 relief="flat").pack(side="left")

        # Topic title
        tk.Label(top, text=self.topic["title"],
                 bg=self.BG, fg="#202124", font=title_font,
                 wraplength=self.WIDTH - 52, justify="left",
                 anchor="w").pack(fill="x", pady=(8, 0))

        # Divider
        tk.Frame(root, bg="#E8EAED", height=1).pack(fill="x", padx=24)

        # ── Body ──────────────────────────────────────────────────────────────
        body = tk.Frame(root, bg=self.BG, padx=24, pady=16)
        body.pack(fill="x")

        tk.Label(body, text=self.topic["description"],
                 bg=self.BG, fg="#444444", font=body_font,
                 wraplength=self.WIDTH - 52, justify="left",
                 anchor="w").pack(fill="x")

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(root, bg=self.BG, padx=24, pady=20)
        btn_frame.pack(fill="x")

        # "Open in Chrome" button
        open_btn = tk.Button(
            btn_frame,
            text="🌐  Open in Chrome",
            font=btn_font,
            bg="#C970CC", fg="#FFFFFF",
            activebackground="#C342C8", activeforeground="#FFFFFF",
            relief="flat", padx=14, pady=10, cursor="hand2",
            command=self._open_and_close
        )
        open_btn.pack(side="left", padx=(0, 10))

        # "Maybe later" button
        skip_btn = tk.Button(
            btn_frame,
            text="Remind me tomorrow",
            font=small_font,
            bg="#6EBDE1", fg="#444444",
            activebackground="#6EBDE1", activeforeground="#333333",
            relief="flat", padx=10, pady=10, cursor="hand2",
            command=root.destroy
        )
        skip_btn.pack(side="left")

        # Close [X] in corner
        tk.Button(
            root, text="✕", bg=self.BG, fg="#999999",
            relief="flat", font=small_font, cursor="hand2",
            command=root.destroy
        ).place(x=self.WIDTH - 36, y=10)

        # ── Centre on screen ──────────────────────────────────────────────────
        root.update_idletasks()
        w, h = root.winfo_reqwidth(), root.winfo_reqheight()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 3        # slightly above centre feels natural
        root.geometry(f"{w}x{h}+{x}+{y}")

        # Bring to front
        root.lift()
        root.attributes("-topmost", True)
        root.after(500, lambda: root.attributes("-topmost", False))

    def _open_and_close(self):
        open_in_chrome(self.topic["url"])
        self.root.destroy()

    def run(self):
        self.root.mainloop()

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    topics = load_topics()
    state  = load_state()
    topic  = pick_topic(topics, state)
    KnowledgePopup(topic).run()

if __name__ == "__main__":
    main()
