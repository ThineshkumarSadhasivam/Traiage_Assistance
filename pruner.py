import time
from data_store import PATIENT_HISTORY, DISASTER_PROTOCOLS

class ContextPruner:
    def __init__(self):
        # Maps common words to medical protocol terms
        self.synonyms = {
            "broken": "fracture",
            "leg": "bone",
            "heart": "cardiac",
            "breath": "asthma"
        }

    def prune(self, query):
        start_time = time.time()
        query_lower = query.lower()
        
        # 1. PRUNE HISTORY: Keep only if a specific keyword matches
        # This keeps the context window tiny
        pruned_history = [h['text'] for h in PATIENT_HISTORY 
                         if h['tag'] != 'Dental' 
                         and any(word in h['text'].lower() for word in query_lower.split())]

        # 2. PRUNE PROTOCOLS: ONLY keep the protocol if the keyword matches EXACTLY
        pruned_protocols = []
        for p in DISASTER_PROTOCOLS:
            condition = p['condition'].lower()
            # We only add the protocol if a query word (or its synonym) is in the condition
            match_found = any(word in condition for word in query_lower.split()) or \
                          any(self.synonyms.get(word, "N/A") in condition for word in query_lower.split())
            
            if match_found:
                pruned_protocols.append(f"PROTOCOL FOR {p['condition']}: {p['action']}")

        duration = (time.time() - start_time) * 1000
        
        # DEBUG: Let's see what we are actually sending to the LLM
        print(f"--- DEBUG: Pruned Context contains {len(pruned_protocols)} protocols ---")
        
        return pruned_history, pruned_protocols, duration