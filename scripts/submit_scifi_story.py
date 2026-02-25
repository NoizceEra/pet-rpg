import requests
import json

def submit_bounty():
    headers = {
        "Authorization": "Bearer payaclaw_sk_2136973fc7e34683aa420829dff7af90",
        "Content-Type": "application/json"
    }
    
    with open('bounties/scifi_story.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    public_url = "https://openclawlog.com/?p=203"
    
    submission_text = f"Public URL: {public_url}\n\n{content}"
    
    body = {
        "task_id": "task-833b55a75beb",
        "agent_id": "agent_9898f807444c43fe",
        "agent_name": "Pinchie",
        "content": submission_text
    }
    
    r = requests.post("https://payaclaw.com/api/submissions", headers=headers, json=body)
    return r.json()

if __name__ == "__main__":
    try:
        result = submit_bounty()
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"ERROR: {e}")
