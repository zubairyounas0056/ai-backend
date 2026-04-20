from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()


def add_interval_job(func, seconds):
    scheduler.add_job(func, "interval", seconds=seconds)


def stop_all_jobs():
    scheduler.remove_all_jobs()
