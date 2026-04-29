import faiss
import numpy as np


class FaissIndex:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.vectors = []

    def add(self, vec):
        vec = np.array([vec]).astype("float32")
        self.index.add(vec)
        self.vectors.append(vec)

    def search(self, vec, k=3):
        vec = np.array([vec]).astype("float32")
        distances, indices = self.index.search(vec, k)
        return distances, indices