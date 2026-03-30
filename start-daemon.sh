#!/bin/bash
# Arranca o daemon osno-remind numa janela tmux dedicada
# Uso: ./start-daemon.sh

SESSION="osno"
WINDOW="remind-daemon"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verifica se a janela já existe
if tmux list-windows -t "$SESSION" | grep -q "$WINDOW"; then
    echo "Daemon já está a correr em $SESSION:$WINDOW"
    exit 0
fi

tmux new-window -t "$SESSION" -n "$WINDOW" "python3 $SCRIPT_DIR/remind.py daemon"
echo "Daemon arrancado em $SESSION:$WINDOW"
