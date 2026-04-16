from concurrent.futures import ThreadPoolExecutor
import threading
import time
import threading

executor = ThreadPoolExecutor(max_workers=10)

running_tasks = {}
lock = threading.Lock()


def run_parallel(task_id, func):
    future = executor.submit(func)

    with lock:
        running_tasks[task_id] = future

    return future


def stop_task(task_id):
    with lock:
        future = running_tasks.get(task_id)
        if future:
            future.cancel()
            del running_tasks[task_id]


def stop_all_tasks():
    with lock:
        for task_id, future in running_tasks.items():
            future.cancel()
        running_tasks.clear()
