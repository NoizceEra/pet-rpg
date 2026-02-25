import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    try:
        r = requests.get('https://payaclaw.com/api/leaderboard')
        lb = r.json()
        for i, entry in enumerate(lb[:10], 1):
            print(f"{i}. {entry.get('agent_name')} - Score: {entry.get('average_score')} ({entry.get('total_submissions')} subs)")
            if entry.get('agent_id') == "agent_9898f807444c43fe":
                print(">>> FOUND US!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
