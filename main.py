import os
import time
from groq import Groq
from pruner import ContextPruner
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
pruner = ContextPruner()

def triage_emergency(user_input):
    start_total = time.time()

    # 1. PRUNE CONTEXT
    history, protocols, prune_time = pruner.prune(user_input)
    
    # If no protocol is found by the pruner, we tell the LLM that explicitly
    context_str = "\n".join(history + protocols) if (history or protocols) else "NO RELEVANT PROTOCOLS FOUND."

    # 2. LLM INFERENCE (New Cleaner Structure)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system", 
                "content": "You are a professional emergency triage assistant. Use ONLY the provided context. If no protocol matches the injury, say 'Protocol not found - follow general first aid'. BE EXTREMELY BRIEF."
            },
            {
                "role": "user", 
                "content": f"CONTEXT: {context_str}\n\nPATIENT QUERY: {user_input}\n\nFormat: PRIORITY | ACTION | REASON"
            }
        ],
        model="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=40, # Extremely low token limit = High Speed
    )
    
    result = chat_completion.choices[0].message.content
    total_latency = (time.time() - start_total) * 1000
    
    return result, total_latency

# --- TERMINAL LOOP (Same as before) ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print("      SENTINEL-FAST TRIAGE ASSISTANT READY")
    print("="*50)
    while True:
        user_query = input("\n[MEDIC INPUT] > ")
        if user_query.lower() in ["exit", "quit", "q"]: break
        try:
            response, latency = triage_emergency(user_query)
            print(f"\nTRIAGE DECISION ({latency:.2f}ms):\n{response}\n" + "-"*50)
            if latency > 500: print("⚠️ LATENCY ALERT")
        except Exception as e: print(f"Error: {e}")