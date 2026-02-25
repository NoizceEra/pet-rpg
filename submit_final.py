import requests
import json

api_key = "payaclaw_sk_2136973fc7e34683aa420829dff7af90"
agent_id = "agent_9898f807444c43fe"
agent_name = "Pinchie"
url = "https://payaclaw.com/api/submissions"

def submit(task_id, content):
    payload = {
        "task_id": task_id,
        "agent_id": agent_id,
        "agent_name": agent_name,
        "content": content
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    r = requests.post(url, json=payload, headers=headers)
    print(f"Task {task_id}: {r.status_code}")
    print(r.text)

# 1. Awesome OpenClaw Guide (100 links)
with open("C:/Users/vclin_jjufoql/.openclaw/workspace/bounties/awesome_guide_100.md", "r", encoding="utf-8") as f:
    guide_content = f.read()
submit("task-906b6760d5d0", guide_content)

# 2. Money Making Methods (10 methods)
with open("C:/Users/vclin_jjufoql/.openclaw/workspace/bounties/money_methods_zh.md", "r", encoding="utf-8") as f:
    money_content = f.read()
submit("task-e3c398d27a36", money_content)
