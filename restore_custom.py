import json
import os

targets_file = 'input/targets.json'

with open(targets_file, 'r', encoding='utf-8') as f:
    targets = json.load(f)

# List of companies that we successfully found correct slugs for
restore_list = {
    'momentumcommerce': {'ats': 'greenhouse', 'company': 'momentum'},
    'https://walmart.wd5.myworkdayjobs.com/WalmartExternal': {'ats': 'workday', 'company': 'https://walmart.wd5.myworkdayjobs.com/WalmartExternal'},
    'https://gartner.wd5.myworkdayjobs.com/EXT': {'ats': 'workday', 'company': 'https://gartner.wd5.myworkdayjobs.com/EXT'},
    'bain': {'ats': 'workday', 'company': 'https://baincapital.myworkdayjobs.com/BainCapital'}
}

# Mapping of what actual ATS unsupported ones use
unsupported_ats = {
    'meta': 'Proprietary',
    'zomato': 'Referrals/Proprietary',
    'jobs.myntra.com': 'Proprietary (careers.myntra.com)',
    'uhg': 'Taleo Enterprise',
    'gotogroup': 'Unknown/Proprietary',
    'careers.bbinsight.com': 'Dead URL (DNS Failed)',
    'cisco2': 'MyWorkdayJobs (jobs.cisco.com)',
    'intuit': 'Proprietary (jobs.intuit.com)',
    'jpmc': 'Oracle Recruiting Cloud',
    'nutanix': 'Jobvite/Proprietary',
    'atherenergy': 'Darwinbox HCM',
    'gommt': 'Darwinbox HCM',
    '1mg': 'Darwinbox HCM',
    'delhivery': 'Darwinbox HCM',
    'rapido': 'Darwinbox HCM',
    'navi': 'TurboHire',
    'urbancompany': 'TurboHire',
    'pinelabsgroup.turbohire.co': 'TurboHire',
    'lenskart.turbohire.co': 'TurboHire',
    'khatabook.turbohire.co': 'TurboHire',
    'zepto.talentrecruit.com': 'TalentRecruit',
    'careers.cult.fit': 'Zwayam',
    'jupiter.keka.com': 'Keka',
    'careers.tesco.com': 'Tribepad',
    'SiemensEnergy': 'SmartRecruiters (Zero Jobs/Migrated)',
    'Nielsen': 'SmartRecruiters (Zero Jobs/Migrated)',
    'https://careers-cvent.icims.com': 'Hirebridge',
    'https://careers-apac-atlassian.icims.com': 'Proprietary (atlassian.com/company/careers)',
    'cred': 'Proprietary (cred.club/careers)'
}

new_targets = []
for target in targets:
    if '_comment' in target:
        comment = target['_comment']
        if 'Disabled:' in comment:
            # Extract company name from the comment e.g. "Disabled: greenhouse/momentumcommerce - ..."
            parts = comment.split(' - ')[0].replace('Disabled: ', '').split('/')
            if len(parts) >= 2:
                old_ats = parts[0]
                old_comp = '/'.join(parts[1:]) # Rejoin in case URL has slashes
                
                # Try exact match or partial match for URLs
                found_restore = None
                for k, v in restore_list.items():
                    if old_comp.endswith(k) or k == old_comp:
                        found_restore = v
                        break
                
                if found_restore:
                    new_targets.append(found_restore)
                    print(f"Restored: {found_restore}")
                    continue
                
                # Check for descriptive mapping
                mapped = None
                for k, v in unsupported_ats.items():
                    if old_comp.endswith(k) or k == old_comp:
                        mapped = v
                        break
                
                if mapped:
                    new_targets.append({
                        "_comment": f"{old_comp.upper()} uses {mapped}. A new scraper must be built for this ATS before it can be monitored."
                    })
                else:
                    new_targets.append(target)
            else:
                new_targets.append(target)
        else:
            new_targets.append(target)
    else:
        new_targets.append(target)

with open(targets_file, 'w', encoding='utf-8') as f:
    json.dump(new_targets, f, indent=4)

print("Updated targets.json")
