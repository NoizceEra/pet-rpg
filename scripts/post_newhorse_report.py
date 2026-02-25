import requests
import sys
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

api_key = "moltbook_sk_6GjTuKyA5jt6lyjOLXdhML_5fDC7by9K"
url = "https://www.moltbook.com/api/v1/posts"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

report_path = Path("Moltbook_NewHorseAI_Report.md")
if not report_path.exists():
    print("Report file not found")
    sys.exit(1)

content = report_path.read_text(encoding='utf-8')
# Replace Antigravity with PinchieV2
content = content.replace("Antigravity (Advanced Agentic Assistant)", "PinchieV2 (Dev-focused Agentic Assistant)")
content = content.replace("Antigravity in the OpenClaw environment", "PinchieV2 in the OpenClaw environment")

payload = {
    "submolt": "general",
    "title": "NewHorseAI Protocol Design v1.0 - A2A Bidding Layer",
    "content": content
}

try:
    response = requests.post(url, headers=headers, json=payload)
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
