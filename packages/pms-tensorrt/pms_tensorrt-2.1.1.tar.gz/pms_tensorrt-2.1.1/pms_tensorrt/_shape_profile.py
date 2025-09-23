from typing import List
from pms_tensorrt._const import *


class ShapeProfile:
    def __init__(
        self,
        name: str,
        min_shape: List[int],
        opt_shape: List[int],
        max_shape: List[int],
    ):
        assert (
            len(min_shape) == len(opt_shape) == len(max_shape)
        ), "ERROR, All shapes are must be same."

        self._name = name
        self._min_shape = min_shape
        self._opt_shape = opt_shape
        self._max_shape = max_shape

    @property
    def name(self) -> str:
        return self._name

    @property
    def min_shape(self) -> List[int]:
        return self._min_shape

    @property
    def opt_shape(self) -> List[int]:
        return self._opt_shape

    @property
    def max_shape(self) -> List[int]:
        return self._max_shape
