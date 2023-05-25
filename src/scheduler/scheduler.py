from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events

# Import needed models
from publications.services import checkPublicationExpiration
from auth.services import checkMembershipExpiration
import sys

def start():

    scheduler = BackgroundScheduler()
    # Not recommended to save jobs in the database
    # just use them while the server is running
    # scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 24 hours
    scheduler.add_job(
        checkPublicationExpiration, 'interval', minutes=5, 
        name='update_bids', jobstore='default'
        )
    scheduler.add_job(
        checkMembershipExpiration, 'interval', minutes=5, 
        name='membership_expiration', jobstore='default'
        )
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...", file=sys.stdout)
    
def stop():
    scheduler = BackgroundScheduler()
    scheduler.shutdown()
    print("Scheduler stopped...", file=sys.stdout)
