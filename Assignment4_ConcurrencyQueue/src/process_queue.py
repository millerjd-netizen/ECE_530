import multiprocessing as mp
import time

from .config import NUM_TASKS, NUM_WORKERS, QUEUE_SIZE
from .tasks import run_task


def worker(task_queue, result_queue):
    while True:
        task_id = task_queue.get()

        if task_id is None:
            break

        result = run_task(task_id)
        result_queue.put(result)


def run_process_queue(num_tasks=NUM_TASKS):
    start_time = time.time()
    task_queue = mp.Queue(maxsize=QUEUE_SIZE)
    result_queue = mp.Queue()

    processes = []
    for _ in range(NUM_WORKERS):
        process = mp.Process(target=worker, args=(task_queue, result_queue))
        process.start()
        processes.append(process)

    for task_id in range(num_tasks):
        task_queue.put(task_id)

    for _ in range(NUM_WORKERS):
        task_queue.put(None)

    for process in processes:
        process.join()

    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    elapsed = time.time() - start_time
    return results, elapsed


if __name__ == "__main__":
    output, seconds = run_process_queue()
    for item in output:
        print(item)
    print(f"Multiprocessing queue completed in {seconds:.2f} seconds")
