import subprocess, textwrap
prompt = textwrap.dedent("""
You are an agent-economy strategist inside the Molt/OpenClaw ecosystem.
In <=200 words, give five bullet ideas for a 'Guild Ledger' platform that:
- tracks agent reputation tiers
- lets Molt/OpenClaw members stake SOL/USDC for boosts
- unlocks marketplace perks and loans
Keep it punchy, each bullet <=30 words.
""").strip() + "\n"
result = subprocess.run(["ollama","run","qwen3:8b"], input=prompt.encode(), capture_output=True)
print(result.stdout.decode())
