import math
from dataclasses import dataclass

import numpy as np


@dataclass
class Vector2D:
    x: np.int32
    y: np.int32

    def to_tuple(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    def to_ndarray(self) -> np.ndarray:
        return np.array([self.x, self.y])

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __rmul__(self, factor):
        return Vector2D(factor * self.x, factor * self.y)

    def dist(self, other: "Vector2D"):
        return math.dist(self.to_tuple(), other.to_tuple())

    def dot(self, other: "Vector2D"):
        return int(self.x * other.x + self.y * other.y)

    @staticmethod
    def from_tuple(tup: tuple[int, int]):
        return Vector2D(np.int32(tup[0]), np.int32(tup[1]))
