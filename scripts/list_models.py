"""List candidate cheap+capable OpenRouter models with pricing."""
from dotenv import load_dotenv
load_dotenv()
import os, httpx

key = os.environ["OPENROUTER_API_KEY"]
r = httpx.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {key}"},
    timeout=30,
)
data = r.json()["data"]

want = [
    "gpt-4o-mini", "gpt-5", "gemini-2.5-flash", "gemini-2.0", "claude-haiku",
    "claude-sonnet", "claude-3.5", "deepseek-v4", "deepseek-r1", "qwen3-coder",
    "qwen3-235b", "qwen3-next", "llama-3.3-70b",
]
hits = []
for m in data:
    mid = m["id"]
    if any(w in mid.lower() for w in want) and ":free" not in mid:
        p = m.get("pricing", {})
        prompt_p = float(p.get("prompt", 0)) * 1_000_000
        compl_p = float(p.get("completion", 0)) * 1_000_000
        hits.append((mid, m.get("context_length", 0), prompt_p, compl_p))
hits.sort(key=lambda x: x[2])
print(f"{'id':55}  {'ctx':>9}  {'in/M':>9}  {'out/M':>9}")
for h in hits[:35]:
    print(f"{h[0]:55}  {h[1]:>9}  ${h[2]:>7.3f}  ${h[3]:>7.3f}")
