import re

# List of keywords to filter out jobs by title (case-insensitive)
FILTER_KEYWORDS = [
    "lead", "manager", "part-time", "tender", "recruiter", "director", 
    "marketing", "sales", "reliability", "staff", "luxnix", "technical support", 
    "principal", "customer success", "executive", "vice president", "president", 
    "security engineer", "data engineer", "counsel", "incident", 
    "operational analyst", "hr", "wealth", "data center", "seo", "soc", "officer",
    "platform engineer", "medical", "assistant", "nurse", "patient",
    "radiology", "architect", "guide", "typescript", "react native",
    "sensor", "avp", "scrum", "c++", "rpa", "intern", "internship",
    "financial controller", "field", "cloud engineer", "student", 
    "college", "vp", "growth", "part time"
]

# Pre-compile a regex pattern for faster matching (using lookarounds instead of \b to support keywords ending in non-word chars like C++)
_FILTER_PATTERN = re.compile(r'(?<!\w)(?:' + '|'.join(map(re.escape, FILTER_KEYWORDS)) + r')(?!\w)', re.IGNORECASE)

def filter_report_data(report_data: dict) -> dict:
    """
    Filters jobs from report_data based on titles containing FILTER_KEYWORDS.
    If a company's yesterdays_jobs becomes empty after filtering, it moves from
    with_yesterday_jobs to no_yesterday_jobs.
    """
    # Create a copy to avoid mutating the original heavily while iterating
    import copy
    data = copy.deepcopy(report_data)
    
    with_jobs = data.get("with_yesterday_jobs", [])
    no_jobs = data.get("no_yesterday_jobs", [])
    
    new_with_jobs = []
    
    for entry in with_jobs:
        jobs = entry.get("yesterdays_jobs", [])
        filtered_jobs = []
        for job in jobs:
            title = job.get("title", "")
            # Check if title contains any keyword
            if not _FILTER_PATTERN.search(title):
                filtered_jobs.append(job)
                
        if filtered_jobs:
            entry["yesterdays_jobs"] = filtered_jobs
            new_with_jobs.append(entry)
        else:
            # All jobs were filtered out
            entry["yesterdays_jobs"] = []
            no_jobs.append(entry)
            
    data["with_yesterday_jobs"] = new_with_jobs
    data["no_yesterday_jobs"] = no_jobs
    
    return data
