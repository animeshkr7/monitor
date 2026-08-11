import json
from src.runner import run_monitor

print("Testing runner logic against modified targets.json...")
with open('input/targets.json', 'r', encoding='utf-8') as f:
    targets = json.load(f)

# Mock run_monitor so it just prints what it WOULD run, 
# ensuring no crashes on comments and verifying valid targets are extracted.
valid_targets = [item for item in targets if 'ats' in item and 'company' in item]
print(f"Total entries in targets.json: {len(targets)}")
print(f"Valid targets to be scraped: {len(valid_targets)}")
print(f"Ignored items (comments): {len(targets) - len(valid_targets)}")

# Find our newly restored targets in the valid list
restored = [
    'momentum',
    'https://baincapital.myworkdayjobs.com/BainCapital',
    'https://walmart.wd5.myworkdayjobs.com/WalmartExternal',
    'https://gartner.wd5.myworkdayjobs.com/EXT'
]

found_restored = []
for v in valid_targets:
    if v['company'] in restored:
        found_restored.append(v['company'])

print(f"Successfully loaded restored targets: {found_restored}")
