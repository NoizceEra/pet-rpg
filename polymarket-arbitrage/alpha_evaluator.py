import os
import sys
import json
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from cellcog import CellCogClient

load_dotenv()

class AlphaEvaluator:
    def __init__(self):
        try:
            self.cellcog_client = CellCogClient()
        except:
            self.cellcog_client = None
            
        self.workspace_dir = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace\polymarket-arbitrage")
        self.results_dir = self.workspace_dir / "alpha_results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Paths to other skills
        self.skills_dir = Path(r"C:\Users\vclin_jjufoql\.agents\skills")
        self.perplexity_script = self.skills_dir / "perplexity-search" / "scripts" / "perplexity_search.py"

    def evaluate_market(self, question, outcomes):
        """
        Submits a market for deep research. Tries CellCog first, then falls back.
        """
        print(f"[ALPHA] Evaluating: {question[:50]}...")
        sys.stdout.flush()

        # 1. Try CellCog (if configured and has credits)
        if self.cellcog_client:
            try:
                chat_id = self._submit_to_cellcog(question, outcomes)
                if chat_id:
                    return {"provider": "cellcog", "id": chat_id}
            except Exception as e:
                print(f"[ALPHA] CellCog failed: {e}")
                sys.stdout.flush()

        # 2. Fallback: Perplexity Search (via script)
        if self.perplexity_script.exists() and os.getenv("OPENROUTER_API_KEY"):
            try:
                result = self._submit_to_perplexity(question, outcomes)
                if result:
                    return {"provider": "perplexity", "data": result}
            except Exception as e:
                print(f"[ALPHA] Perplexity failed: {e}")
                sys.stdout.flush()

        # 3. Last Resort: Trigger a 'Deep Research' request to the user/session
        print(f"[ALPHA] All automated research providers failed. Triggering manual deep-research request.")
        sys.stdout.flush()
        return {"provider": "manual", "message": f"Please perform deep research on: {question}"}

    def _submit_to_cellcog(self, question, outcomes):
        prompt = f"""
        # Polymarket Alpha Research
        Market: {question}
        Outcomes: {", ".join(outcomes)}

        Perform a deep research pass on this market. Search for:
        1. Recent news and verified events.
        2. Social sentiment and expert opinions.
        3. On-chain data if relevant.
        4. Statistical likelihood based on historical precedents.

        ## Output Requirement
        Return a JSON object ONLY with the following structure:
        {{
          "question": "{question}",
          "estimated_probabilities": {{
            "Outcome1": 0.XX,
            "Outcome2": 0.XX
          }},
          "confidence_score": 0.XX,
          "reasoning_summary": "Short summary of why",
          "key_risks": ["risk1", "risk2"]
        }}
        """
        result = self.cellcog_client.create_chat(
            prompt=prompt,
            notify_session_key="agent:main:main",
            task_label=f"alpha-{int(time.time())}",
            chat_mode="agent"
        )
        return result.get("chat_id")

    def _submit_to_perplexity(self, question, outcomes):
        query = f"Research Polymarket: {question}. Outcomes are {', '.join(outcomes)}. Give me an estimated probability for each outcome based on recent news and sentiment. Respond in JSON format."
        
        # Call the perplexity script directly
        cmd = [sys.executable, str(self.perplexity_script), query, "--output", str(self.results_dir / f"perp_{int(time.time())}.json")]
        
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode == 0:
            return process.stdout
        else:
            raise Exception(f"Perplexity script error: {process.stderr}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python alpha_evaluator.py \"Market Question\" [Outcome1,Outcome2]")
        sys.exit(1)
        
    question = sys.argv[1]
    outcomes = sys.argv[2].split(",") if len(sys.argv) > 2 else ["Yes", "No"]
    
    evaluator = AlphaEvaluator()
    result = evaluator.evaluate_market(question, outcomes)
    print(f"Result: {result}")
