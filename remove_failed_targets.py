import json
import os

targets_file = 'input/targets.json'
failed_report = 'output/reports/yesterday_jobs_failed.json'

with open(failed_report, 'r', encoding='utf-8') as f:
    failed_data = json.load(f)

failed_pairs = {(item.get('ats', ''), item.get('company', '')) for item in failed_data}

with open(targets_file, 'r', encoding='utf-8') as f:
    targets = json.load(f)

new_targets = []
removed_count = 0

for target in targets:
    # Skip if it's already a comment
    if '_comment' in target:
        new_targets.append(target)
        continue
    
    ats = target.get('ats', '')
    company = target.get('company', '')
    
    if (ats, company) in failed_pairs:
        # Convert to comment
        reason = next((d.get('message', 'Failed') for d in failed_data if d.get('ats') == ats and d.get('company') == company), 'Failed')
        new_targets.append({
            "_comment": f"Disabled: {ats}/{company} - {reason}"
        })
        removed_count += 1
    else:
        new_targets.append(target)

with open(targets_file, 'w', encoding='utf-8') as f:
    json.dump(new_targets, f, indent=4)

print(f"Disabled {removed_count} failed targets in {targets_file}")
