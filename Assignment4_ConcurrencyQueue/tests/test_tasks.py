from src.tasks import generate_matrix_pair, run_task
from src.config import MATRIX_SIZE


def test_generate_matrix_pair_shapes():
    a, b = generate_matrix_pair()

    assert a.shape == (MATRIX_SIZE, MATRIX_SIZE)
    assert b.shape == (MATRIX_SIZE, MATRIX_SIZE)


def test_run_task_returns_completion_message():
    result = run_task(1)

    assert "Task 1 completed" in result
    assert "shape" in result
