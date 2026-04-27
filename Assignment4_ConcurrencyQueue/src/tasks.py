import numpy as np
from .config import MATRIX_SIZE


def generate_matrix_pair():
    a = np.random.rand(MATRIX_SIZE, MATRIX_SIZE)
    b = np.random.rand(MATRIX_SIZE, MATRIX_SIZE)
    return a, b


def run_task(task_id):
    a, b = generate_matrix_pair()
    result = np.matmul(a, b)
    return f"Task {task_id} completed with shape {result.shape}"
