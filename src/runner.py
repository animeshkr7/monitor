import os
import concurrent.futures
from datetime import datetime
from src.scraper import scrape_yesterdays_jobs
from src.reporter import generate_reports
from src.inactivity_tracker import update_inactivity_tracker
from send_notification import send_notification

def run_monitor(targets: list[dict]) -> None:
    """
    Executes the job scraping concurrently for a given list of targets.
    - Runs scrapers in parallel pool (max_workers=10).
    - Failed condition: failed to fetch even 1 job overall (total_jobs == 0 or status != SUCCESS).
    - Updates per-company inactivity tracker & checks for >7 days inactivity alerts.
    - Generates JSON reports and triggers email notification with attached failed JSON.
    """
    print(f"\n{'='*60}\nStarting Unified ATS Monitor at {datetime.now()}\n{'='*60}")

    report = {
        "with_yesterday_jobs": [],
        "no_yesterday_jobs": [],
        "failed_or_migrated": []
    }

    valid_targets = [item for item in targets if 'ats' in item and 'company' in item]

    results_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures_to_item = {
            executor.submit(scrape_yesterdays_jobs, item['ats'], item['company']): item
            for item in valid_targets
        }
        
        for future in concurrent.futures.as_completed(futures_to_item):
            item = futures_to_item[future]
            ats_name = item['ats']
            company_slug = item['company']
            
            try:
                result = future.result(timeout=180)
            except concurrent.futures.TimeoutError:
                print(f"  -> TIMEOUT: [{ats_name}] {company_slug} took longer than 3 minutes.")
                result = {"status": "TIMEOUT", "message": "Scraping took longer than 3 minutes.", "total_jobs": 0, "yesterdays_jobs": []}
            except Exception as e:
                print(f"  -> FATAL THREAD ERROR: [{ats_name}] {company_slug}: {e}")
                result = {"status": "FATAL_ERROR", "message": str(e), "total_jobs": 0, "yesterdays_jobs": []}
                
            entry = {
                "ats": ats_name,
                "company": company_slug,
                "status": result["status"],
                "message": result["message"],
                "total_jobs": result.get("total_jobs", 0),
                "yesterdays_jobs": result["yesterdays_jobs"]
            }

            # Scraper failure condition: failed to fetch even 1 job overall (total_jobs == 0 or status != SUCCESS)
            total_jobs = result.get("total_jobs", 0)
            if result["status"] == "SUCCESS" and total_jobs > 0:
                if len(result["yesterdays_jobs"]) > 0:
                    report["with_yesterday_jobs"].append(entry)
                else:
                    report["no_yesterday_jobs"].append(entry)
            else:
                report["failed_or_migrated"].append(entry)

    # 1. Update per-company inactivity tracker state & get > 7 days alerts
    inactivity_alerts = update_inactivity_tracker(report)

    # 2. Generate JSON report files
    generate_reports(report)

    # 3. Send email notification (attaches failed JSON, report JSON, log file)
    send_notification(report, inactivity_alerts)
    
    # Force kill any lingering background threads safely
    os._exit(0)

# --- Module Level Tests ---
if __name__ == '__main__':
    print("Testing module 'runner.py'...")
    dummy_targets = [
        {"ats": "ashby", "company": "elevenlabs"}
    ]
    run_monitor(dummy_targets)
