import json
import os
from datetime import datetime

AUTH_FILE = r"C:\Users\vclin_jjufoql\.openclaw\agents\main\agent\auth-profiles.json"
LOG_FILE = r"C:\Users\vclin_jjufoql\.openclaw\workspace\api_usage_report.md"

def load_auth():
    with open(AUTH_FILE, 'r') as f:
        return json.load(f)

def run_governor():
    data = load_auth()
    stats = data.get("usageStats", {})
    
    report = [
        "# 🦞 API Governor: Token Consumption Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "| Provider | Profile | Errors | Last Used | Status |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    
    for profile_id, s in stats.items():
        provider = profile_id.split(":")[0]
        errs = s.get("errorCount", 0)
        last_used_ts = s.get("lastUsed", 0)
        last_used = datetime.fromtimestamp(last_used_ts/1000).strftime('%Y-%m-%d %H:%M') if last_used_ts else "Never"
        
        status = "✅ Healthy"
        if errs > 5:
            status = "⚠️ Rate Limited (Throttling recommended)"
        if "cooldownUntil" in s:
            status = "🚫 Cooling Down"
            
        report.append(f"| {provider} | {profile_id} | {errs} | {last_used} | {status} |")
        
    report.append("\n## 🧠 Consolidation Strategy:")
    report.append("1. **Primary Logic:** Groq (Llama 3.3 70B) is current primary. Fast and reliable.")
    report.append("2. **Throttling:** If Gemini 429s persist, agents should switch to Groq entirely.")
    report.append("3. **Recall Optimization:** Agents should summarize findings in `MEMORY.MD` to reduce context window consumption for next turns.")
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    
    print(f"Governor report updated at {LOG_FILE}")

if __name__ == "__main__":
    run_governor()
