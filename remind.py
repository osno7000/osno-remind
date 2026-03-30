#!/usr/bin/env python3
"""
osno-remind — agendador de mensagens para o Osno
Usa: remind.py add "in 10 minutes" "verificar noticias"
     remind.py add "13:43" "explorar grupos de telegram"
     remind.py add "in 1 hour" "ragebait no twitter"
     remind.py list
     remind.py daemon  (corre em background, verifica a cada 30s)
"""

import json
import sys
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import re
import time

QUEUE_FILE = Path.home() / "mind" / "reminders.json"
TMUX_TARGET = "osno:0.0"

def load_queue():
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE) as f:
        return json.load(f)

def save_queue(queue):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2, default=str)

def parse_time(when: str) -> datetime:
    now = datetime.now()
    when = when.strip().lower()

    # "in X minutes/hours/seconds"
    m = re.match(r"in (\d+)\s*(minute|min|hour|second|sec)s?", when)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        if unit in ("minute", "min"):
            return now + timedelta(minutes=n)
        elif unit in ("hour",):
            return now + timedelta(hours=n)
        elif unit in ("second", "sec"):
            return now + timedelta(seconds=n)

    # "HH:MM" — hoje ou amanhã se já passou
    m = re.match(r"^(\d{1,2}):(\d{2})$", when)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        t = now.replace(hour=h, minute=mi, second=0, microsecond=0)
        if t <= now:
            t += timedelta(days=1)
        return t

    # "HH:MM:SS"
    m = re.match(r"^(\d{1,2}):(\d{2}):(\d{2})$", when)
    if m:
        h, mi, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
        t = now.replace(hour=h, minute=mi, second=s, microsecond=0)
        if t <= now:
            t += timedelta(days=1)
        return t

    raise ValueError(f"Não percebi o tempo: '{when}'. Usa 'in 10 minutes', 'in 1 hour', ou 'HH:MM'")

def add_reminder(when: str, message: str):
    queue = load_queue()
    t = parse_time(when)
    entry = {
        "id": int(datetime.now().timestamp() * 1000),
        "time": t.isoformat(),
        "message": message,
        "sent": False
    }
    queue.append(entry)
    save_queue(queue)
    print(f"✓ Agendado para {t.strftime('%H:%M:%S')} — {message}")

def list_reminders():
    queue = load_queue()
    pending = [e for e in queue if not e["sent"]]
    if not pending:
        print("Sem lembretes pendentes.")
        return
    now = datetime.now()
    for e in sorted(pending, key=lambda x: x["time"]):
        t = datetime.fromisoformat(e["time"])
        diff = t - now
        mins = int(diff.total_seconds() / 60)
        print(f"[{e['id']}] {t.strftime('%H:%M:%S')} (daqui a {mins}min) — {e['message']}")

def send_to_tmux(message: str):
    # Envia a mensagem como input no pane do tmux
    cmd = ["tmux", "send-keys", "-t", TMUX_TARGET, message, "Enter"]
    subprocess.run(cmd)

def run_daemon():
    print(f"daemon arrancado — a verificar {QUEUE_FILE} a cada 30s", flush=True)
    while True:
        try:
            queue = load_queue()
            now = datetime.now()
            changed = False
            for entry in queue:
                if entry["sent"]:
                    continue
                t = datetime.fromisoformat(entry["time"])
                if t <= now:
                    msg = f"[reminder] {entry['message']}"
                    send_to_tmux(msg)
                    entry["sent"] = True
                    changed = True
                    print(f"Enviado: {msg}", flush=True)
            if changed:
                save_queue(queue)
        except Exception as e:
            print(f"Erro: {e}", flush=True)
        time.sleep(30)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add":
        if len(sys.argv) < 4:
            print("Uso: remind.py add <quando> <mensagem>")
            sys.exit(1)
        add_reminder(sys.argv[2], sys.argv[3])

    elif cmd == "list":
        list_reminders()

    elif cmd == "daemon":
        run_daemon()

    else:
        print(f"Comando desconhecido: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
