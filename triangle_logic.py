import numpy as np
from itertools import combinations

class TriangleDetector:
    def __init__(self):
        self.points = []
        self.adjacency_matrix = np.array([])

    def reset(self):
        self.points = []
        self.adjacency_matrix = np.array([])

    def add_point(self, point):
        if point not in self.points:
            self.points.append(point)
            self._update_adjacency_matrix()

    def add_line(self, start, end):
        self.add_point(start)
        self.add_point(end)
        start_index = self.points.index(start)
        end_index = self.points.index(end)
        self.adjacency_matrix[start_index, end_index] = 1
        self.adjacency_matrix[end_index, start_index] = 1

    def _update_adjacency_matrix(self):
        n = len(self.points)
        new_matrix = np.zeros((n, n), dtype=int)
        if self.adjacency_matrix.size > 0:
            old_size = self.adjacency_matrix.shape[0]
            new_matrix[:old_size, :old_size] = self.adjacency_matrix
        self.adjacency_matrix = new_matrix

    def find_triangles(self):
        triangles = []
        n = len(self.points)
        for i, j, k in combinations(range(n), 3):
            if (self.adjacency_matrix[i, j] and 
                self.adjacency_matrix[j, k] and 
                self.adjacency_matrix[k, i]):
                triangles.append((self.points[i], self.points[j], self.points[k]))
        return triangles

    def is_acute(self, triangle):
        a, b, c = triangle
        vectors = [
            (b[0] - a[0], b[1] - a[1]),
            (c[0] - b[0], c[1] - b[1]),
            (a[0] - c[0], a[1] - c[1])
        ]
        dot_products = [
            vectors[i][0] * vectors[(i+1)%3][0] + vectors[i][1] * vectors[(i+1)%3][1]
            for i in range(3)
        ]
        return all(dp < 0 for dp in dot_products)