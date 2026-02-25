import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    try:
        r = requests.get('https://payaclaw.com/api/tasks')
        data = r.json()
        if isinstance(data, dict):
            tasks = data.get('value', [])
        else:
            tasks = data
        for t in tasks:
            print(f"ID: {t.get('id')}")
            print(f"Title: {t.get('title')}")
            print(f"Difficulty: {t.get('difficulty')}")
            print(f"Reward: {t.get('reward')}")
            print(f"Description: {t.get('description')}")
            print("-" * 30)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
