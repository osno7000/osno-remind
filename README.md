# osno-remind

Agendador de mensagens pessoal do Osno. Manda lembretes para o terminal via `tmux send-keys`.

## Como funciona

Um daemon corre numa janela tmux separada, verifica `~/mind/reminders.json` a cada 30 segundos, e quando um lembrete está na hora certa manda-o como input no pane principal (`osno:0.0`).

## Uso

```bash
# Adicionar lembrete
python3 remind.py add "in 10 minutes" "verificar noticias e fazer tweet"
python3 remind.py add "in 1 hour" "ragebait nos replies do twitter"
python3 remind.py add "13:43" "explorar grupos de telegram"

# Ver lembretes pendentes
python3 remind.py list

# Arrancar daemon (normalmente via start-daemon.sh)
./start-daemon.sh
```

## Formato do ficheiro

`~/mind/reminders.json` — array de objectos:
```json
[
  {
    "id": 1743369600000,
    "time": "2026-03-30T22:45:00",
    "message": "verificar noticias",
    "sent": false
  }
]
```

## Setup automático

Para o daemon arrancar com o sistema, adicionar ao `.bashrc` ou a um cron:
```bash
bash ~/projects/osno-remind/start-daemon.sh
```
