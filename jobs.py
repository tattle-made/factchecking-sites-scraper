import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from live_scraping import scrape_new_articles
from upload_to_s3 import upload_files
from register_to_portal import register_to_portal

def setup_job():
    print('JOB_INITIALIZED')
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=run_job, trigger="interval", seconds=3)
    scheduler.start()

def run_job():
    print('JOB_STARTED')
    # scrape_new_articles()
    # upload_files()
    # register_to_portal()
    print('JOB_END')
