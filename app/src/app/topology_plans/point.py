import numpy as np

from dataclasses import dataclass

@dataclass
class Point:
    x: np.int32
    y: np.int32

    def to_tuple(self) -> tuple[int, int]:
        return int(self.x), int(self.y)