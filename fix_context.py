from pathlib import Path
p = Path(r'C:\Users\vclin_jjufoql\.openclaw\workspace\skills\openclaw-token-optimizer\scripts\context_optimizer.py')
r = p.read_text(encoding='utf-8')
old = 'STATE_FILE = Path.home() / ".openclaw/workspace/memory/context-usage.json"'
new = "STATE_FILE = Path(r'C:\\Users\\vclin_jjufoql\\.openclaw\\workspace\\memory\\context-usage.json')"
p.write_text(r.replace(old, new), encoding='utf-8')
