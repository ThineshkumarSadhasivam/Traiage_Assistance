import os
import time
from groq import Groq
from pruner import ContextPruner
from dotenv import load_dotenv
load_dotenv()
# Initialize
# Note: In a production app, keep your API key in an .env file for security!
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
pruner = ContextPruner()

def triage_emergency(user_input):
    # Start timer for the whole process
    start_total = time.time()

    # 1. Prune Context (Noise Reduction)
    history, protocol, prune_time = pruner.prune(user_input)
    
    # 2. Construct Ultra-Lean Prompt
    # We combine only the relevant history and the matching protocol
    context_str = "\n".join(history + protocol)
    
    # Construct an even leaner prompt
    prompt = f"""
    [INST] You are a Crisis Triage Bot. 
    Use ONLY these facts: {context_str}
    
    If the query is "{user_input}", what is the SINGLE most urgent action?
    
    Format:
    PRIORITY: (Red/Yellow/Green)
    ACTION: (One sentence only)
    REASON: (Based on history)
    [/INST]
    """

    # 3. LLM Inference (Fast Reasoning via Groq)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant", 
        temperature=0, # Keep it deterministic for medical safety
    )
    
    result = chat_completion.choices[0].message.content
    
    # Calculate total time taken
    end_total = time.time()
    total_latency = (end_total - start_total) * 1000
    
    return result, total_latency

# --- OPTION 1: INTERACTIVE TERMINAL LOOP ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print("      SENTINEL-FAST TRIAGE ASSISTANT READY")
    print("      Target Latency: <500ms")
    print("="*50)
    print("Type patient symptoms below (or type 'exit' to quit):")

    while True:
        # Get input from the "Medic"
        user_query = input("\n[MEDIC INPUT] > ")

        # Check for exit command
        if user_query.lower() in ["exit", "quit", "q"]:
            print("Shutting down Triage Assistant...")
            break

        if not user_query.strip():
            continue

        # Process the emergency
        try:
            response, latency = triage_emergency(user_query)

            # Display the result
            print("-" * 50)
            print(f"TRIAGE DECISION (Processed in {latency:.2f}ms):")
            print(response)
            print("-" * 50)

            # Warning if we exceed our 500ms budget
            if latency > 500:
                print("⚠️ LATENCY ALERT: System exceeded 500ms threshold.")
        
        except Exception as e:
            print(f"An error occurred: {e}")