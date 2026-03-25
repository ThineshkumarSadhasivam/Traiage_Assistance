import time
from data_store import PATIENT_HISTORY, DISASTER_PROTOCOLS

class ContextPruner:
    def __init__(self):
        # We define what constitutes a 'Critical' match
        pass

    def prune(self, query):
        start_time = time.time()
        query_words = set(query.lower().split())
        
        # 1. PRUNE HISTORY: Only keep if a word matches AND it's not 'dental'
        pruned_history = []
        for h in PATIENT_HISTORY:
            history_words = set(h['text'].lower().replace('.', '').split())
            # If there's an overlap in words and it's not a dental noise record
            if query_words.intersection(history_words) and h['tag'] != 'Dental':
                pruned_history.append(h['text'])

        # 2. PRUNE PROTOCOLS: Only keep the ONE protocol that matches best
        pruned_protocols = []
        for p in DISASTER_PROTOCOLS:
            if any(word in p['condition'].lower() for word in query_words):
                pruned_protocols.append(p['action'])

        duration = (time.time() - start_time) * 1000
        return pruned_history, pruned_protocols, duration