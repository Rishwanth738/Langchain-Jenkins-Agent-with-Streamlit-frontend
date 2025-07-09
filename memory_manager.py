import json
import os
from datetime import datetime

MEMORY_FILE = "agent_memory.json"

def log_interaction(prompt, jenkins_result):
    data = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "jenkins_result": jenkins_result
    }

    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump([data], f, indent=2)
    else:
        with open(MEMORY_FILE, "r") as f:
            existing = json.load(f)
        existing.append(data)
        with open(MEMORY_FILE, "w") as f:
            json.dump(existing, f, indent=2)

def get_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []