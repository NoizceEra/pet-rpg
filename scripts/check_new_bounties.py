import os
import re

history_file = 'logs/bounties_history.log'
current_file = 'logs/current_bounties.tmp'

def parse_bounties(content):
    # Strip null bytes and other weirdness if present (the previous read showed some)
    content = content.replace('\x00', '')
    
    tasks = []
    # IDs are like 'task-e3c398d27a36'
    # Rewards are like 'Reward: 100'
    matches = re.findall(r'ID: (task-[a-f0-9]+).*?Reward: (\d+)', content, re.DOTALL)
    for task_id, reward in matches:
        tasks.append({'id': task_id, 'reward': int(reward)})
    return tasks

def main():
    if not os.path.exists(current_file):
        print("No current bounties file found.")
        return

    with open(current_file, 'r', encoding='utf-8', errors='ignore') as f:
        current_content = f.read()
    
    current_tasks = parse_bounties(current_content)
    
    seen_ids = set()
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history_content = f.read()
            seen_ids = set(re.findall(r'ID: (task-[a-f0-9]+)', history_content))

    new_high_reward = []
    for task in current_tasks:
        if task['id'] not in seen_ids:
            if task['reward'] > 200:
                new_high_reward.append(task)
            # Add to history
            with open(history_file, 'a', encoding='utf-8') as f:
                f.write(f"ID: {task['id']} | Reward: {task['reward']}\n")

    if new_high_reward:
        print("NEW_BOUNTIES_FOUND")
        for task in new_high_reward:
            print(f"Bounty Found: {task['id']} - Reward: {task['reward']}")
    else:
        print("NO_NEW_HIGH_REWARD_BOUNTIES")

if __name__ == "__main__":
    main()
