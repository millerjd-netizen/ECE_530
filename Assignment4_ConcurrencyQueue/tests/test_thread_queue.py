from src.thread_queue import run_threaded_queue


def test_threaded_queue_completes_all_tasks():
    results, elapsed = run_threaded_queue(num_tasks=3)

    assert len(results) == 3
    assert elapsed >= 0
    assert all("completed" in result for result in results)
