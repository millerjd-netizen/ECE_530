from .process_queue import run_process_queue
from .thread_queue import run_threaded_queue


def run_load_tests():
    task_counts = [1, 10, 25, 50]

    print("Concurrency Queue Load Test")
    print("===========================")

    for count in task_counts:
        thread_results, thread_time = run_threaded_queue(count)
        process_results, process_time = run_process_queue(count)

        print(f"\nTasks: {count}")
        print(f"Threaded: {len(thread_results)} completed in {thread_time:.2f} seconds")
        print(f"Multiprocess: {len(process_results)} completed in {process_time:.2f} seconds")


if __name__ == "__main__":
    run_load_tests()
