import numpy as np


def compute_embedding(image):
    # Simple flatten + normalize (MVP embedding)
    vector = image.flatten().astype("float32")
    norm = np.linalg.norm(vector)
    return vector / norm if norm > 0 else vector