import queue
import threading
import time

from .config import NUM_TASKS, NUM_WORKERS, QUEUE_SIZE
from .tasks import run_task


def worker(task_queue, results):
    while True:
        task_id = task_queue.get()

        if task_id is None:
            task_queue.task_done()
            break

        result = run_task(task_id)
        results.append(result)
        task_queue.task_done()


def run_threaded_queue(num_tasks=NUM_TASKS):
    start_time = time.time()
    task_queue = queue.Queue(maxsize=QUEUE_SIZE)
    results = []

    threads = []
    for _ in range(NUM_WORKERS):
        thread = threading.Thread(target=worker, args=(task_queue, results))
        thread.start()
        threads.append(thread)

    for task_id in range(num_tasks):
        task_queue.put(task_id)

    for _ in range(NUM_WORKERS):
        task_queue.put(None)

    task_queue.join()

    for thread in threads:
        thread.join()

    elapsed = time.time() - start_time
    return results, elapsed


if __name__ == "__main__":
    output, seconds = run_threaded_queue()
    for item in output:
        print(item)
    print(f"Threaded queue completed in {seconds:.2f} seconds")
