# Daily Knowledge — Learn Something New Every Day

A Python desktop app that pops up every time you log into your laptop
and shows you one topic to learn about — then opens the article in Chrome.

No internet required to show the popup. Chrome opens the Wikipedia/article link.

---

## What's Inside

```
daily-knowledge/
├── daily_knowledge.py     ← main app (run this)
├── topics.json            ← 90+ topics across 10 categories
├── state.json             ← auto-created; tracks shown topics
├── setup_windows.bat      ← one-click Windows startup installer
├── setup_mac_linux.sh     ← one-click macOS/Linux startup installer
└── README.md              ← you're reading this
```

---

## Step 1 — Requirements

You only need **Python 3** (no extra packages — uses only built-in libraries).

- Download Python: https://python.org/downloads
- During install on Windows, **check "Add Python to PATH"**

---

## Step 2 — Test It First

Open a terminal in this folder and run:

```bash
python daily_knowledge.py        # Windows
python3 daily_knowledge.py       # macOS / Linux
```

A popup should appear. Click **"Open in Chrome"** to read the article.

---

## Step 3 — Auto-Start on Login

### Windows
Double-click `setup_windows.bat`

That's it. The app will now silently appear every time you log in.

To uninstall: double-click `setup_windows_remove.bat` (created by setup).

---

### macOS
Open Terminal in this folder and run:

```bash
chmod +x setup_mac_linux.sh
./setup_mac_linux.sh
```

This installs a LaunchAgent that runs the app on every login.

To uninstall:
```bash
launchctl unload ~/Library/LaunchAgents/com.dailyknowledge.plist
rm ~/Library/LaunchAgents/com.dailyknowledge.plist
```

---

### Linux (GNOME, KDE, XFCE)
Open Terminal in this folder and run:

```bash
chmod +x setup_mac_linux.sh
./setup_mac_linux.sh
```

This creates a `.desktop` autostart file in `~/.config/autostart/`.

To uninstall:
```bash
rm ~/.config/autostart/daily-knowledge.desktop
```

---

## How Topics Are Chosen

- One topic per day — same one if you open the popup multiple times
- Topics don't repeat until all 90+ have been shown once
- Covers: Politics, History, Science, Countries, Economics,
  Technology, Philosophy, Society, Engineering

---

## Adding Your Own Topics

Open `topics.json` and add entries in this format:

```json
{
  "title": "Your Topic Title",
  "category": "Science & Nature",
  "description": "A 1-2 sentence description that fits in the popup.",
  "url": "https://en.wikipedia.org/wiki/Your_Topic"
}
```

Valid categories: Politics, Economics, History, Countries,
Science & Nature, Technology, Engineering, Society, Philosophy

---

## Troubleshooting

**Popup doesn't appear on Windows startup?**
- Make sure Python is in your PATH
- Try running `setup_windows.bat` as Administrator

**Chrome doesn't open, opens another browser instead?**
- The app looks for Chrome in the default install locations
- If Chrome is installed elsewhere, edit the `chrome_paths` list in `daily_knowledge.py`

**Want to reset and see all topics fresh?**
- Delete `state.json` — it will be recreated automatically
