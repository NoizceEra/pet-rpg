from pathlib import Path
p = Path(r'C:\Users\vclin_jjufoql\.openclaw\workspace\skills\openclaw-token-optimizer\scripts\token_tracker.py')
r = p.read_text(encoding='utf-8')
old = 'STATE_FILE = Path.home() / ".openclaw/workspace/memory/token-tracker-state.json"'
new = "STATE_FILE = Path(r'C:\\Users\\vclin_jjufoql\\.openclaw\\workspace\\memory\\token-tracker-state.json')"
p.write_text(r.replace(old, new), encoding='utf-8')
