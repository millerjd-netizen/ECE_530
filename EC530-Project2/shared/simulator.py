import numpy as np


def generate_random_image(size=(64, 64)):
    return (np.random.rand(*size, 3) * 255).astype(np.uint8)


def generate_random_vector(dim=128):
    return np.random.rand(dim).astype("float32")