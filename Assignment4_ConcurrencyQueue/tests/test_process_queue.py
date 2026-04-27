from src.process_queue import run_process_queue


def test_process_queue_completes_all_tasks():
    results, elapsed = run_process_queue(num_tasks=3)

    assert len(results) == 3
    assert elapsed >= 0
    assert all("completed" in result for result in results)
