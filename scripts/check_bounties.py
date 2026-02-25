import requests
import json
import os

LAST_BOUNTIES_FILE = 'payaclaw/bounties_last.json'

def main():
    try:
        r = requests.get('https://payaclaw.com/api/tasks')
        data = r.json()
        tasks = data.get('value', []) if isinstance(data, dict) else data
        
        if os.path.exists(LAST_BOUNTIES_FILE):
            with open(LAST_BOUNTIES_FILE, 'r') as f:
                last_ids = json.load(f)
        else:
            last_ids = []
            
        new_high_reward = []
        current_ids = []
        
        for t in tasks:
            tid = t.get('id')
            current_ids.append(tid)
            reward = t.get('reward', 0)
            try:
                reward = int(reward)
            except:
                reward = 0
            
            if tid not in last_ids:
                if reward > 200:
                    new_high_reward.append(t)
        
        # Save current state
        with open(LAST_BOUNTIES_FILE, 'w') as f:
            json.dump(current_ids, f, indent=2)
            
        if new_high_reward:
            print("NEW_BOUNTIES_FOUND")
            for t in new_high_reward:
                print(f"ID: {t.get('id')} | Title: {t.get('title')} | Reward: {t.get('reward')}")
        else:
            print("NO_NEW_HIGH_REWARD_BOUNTIES")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
