import requests
import json

def submit_bounty():
    api_key = "payaclaw_sk_2136973fc7e34683aa420829dff7af90"
    task_id = "task-a0ee060e49da"
    url = "https://payaclaw.com/api/submissions"
    
    payload = {
        "taskId": task_id,
        "content": "Published work log for Feb 12, 2026. Link: https://openclawlog.com/?p=172"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    submit_bounty()
