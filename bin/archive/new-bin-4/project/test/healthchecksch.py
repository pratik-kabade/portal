from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

import time

def my_job(text):
    print(f"This is my job: {text}")

class DynamicScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(jobstores={'default': MemoryJobStore()}, executors={'default': ThreadPoolExecutor(20)})
        self.scheduler.start()

    def add_job(self, func, trigger, id, args=(), kwargs={}, **trigger_args):
        job = self.scheduler.add_job(func, trigger, id=id, args=args, kwargs=kwargs, **trigger_args)
        print(f"Job added with ID: {job.id}")

    def remove_job(self, job_id):
        try:
            self.scheduler.remove_job(job_id)
            print(f"Job with ID: {job_id} removed")
        except Exception as e:
            print(f"Error removing job: {e}")

    def run(self):
        while True:
            time.sleep(1)

if __name__ == "__main__":
    scheduler = DynamicScheduler()

    # Add jobs
    scheduler.add_job(my_job, 'interval', seconds=5, id='job1', args=('Job 1',))
    scheduler.add_job(my_job, 'interval', seconds=6, id='job2', args=('Job 2',))

    # Remove a job
    #scheduler.remove_job('job1')

  #  scheduler.run()
    print ("done")

    scheduler.add_job(my_job, 'interval', seconds=6, id='job3', args=('Job 3',))
  #  scheduler.run()
