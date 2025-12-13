"""Categorize bugs by difficulty"""
import json
from pathlib import Path

# Load catalog
with open('bugs/catalog.json', 'r') as f:
    bugs = json.load(f)

# Categorize (simple heuristic - you can improve this)
categorized = {
    'easy': [],
    'medium': [],
    'hard': []
}

for i, bug in enumerate(bugs):
    # Simple categorization based on bug_id
    # Lower IDs are usually simpler bugs
    bug_id = bug['bug_id']
    
    if bug_id <= 10:
        categorized['easy'].append(i)
    elif bug_id <= 20:
        categorized['medium'].append(i)
    else:
        categorized['hard'].append(i)

# Save categorized bugs
with open('bugs/categorized.json', 'w') as f:
    json.dump(categorized, f, indent=2)

print(f"Easy: {len(categorized['easy'])} bugs")
print(f"Medium: {len(categorized['medium'])} bugs")
print(f"Hard: {len(categorized['hard'])} bugs")
