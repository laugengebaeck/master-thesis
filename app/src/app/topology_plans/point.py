import numpy as np

from dataclasses import dataclass

@dataclass
class Point:
    x: np.int32
    y: np.int32

    def to_tuple(self) -> tuple[int, int]:
        return int(self.x), int(self.y)
    
    def to_ndarray(self) -> np.ndarray:
        return np.array([self.x, self.y])
    
    @staticmethod
    def from_tuple(tup: tuple[int, int]):
        return Point(np.int32(tup[0]), np.int32(tup[1]))