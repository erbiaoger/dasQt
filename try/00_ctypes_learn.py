import ctypes
import numpy as np
import dataclasses
import math
import typing

type Coordinate = tuple[int, int]
"""the coordinate of chess"""

type Operation = tuple[Coordinate, Coordinate] | None
"""a valid operation"""

type ID = typing.Literal[
    -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8]
"""all ids of chesses"""



@dataclasses.dataclass
class Node:
    """Node of the min-max searching tree"""

    score: float
    operation: Operation = None


def _np_to_array(data: np.ndarray) -> ctypes.Array[ctypes.Array[ctypes.c_int]]:
    """Python 二维棋局列表转换为 C 二维数组"""
    # nt, nx = data.shape
    # arr = (ctypes.c_int * nt * nx)()
    arr = np.ctypeslib.as_ctypes(data)
    # for i in range(nt):
    #     for j in range(9):
    #         arr[i][j] = data[i][j]
    return arr



def choose_algo(data: np.ndarray) -> Node:
    """"""
    node = Node(ctypes.CDLL('./cpp/libA.dylib').search(_np_to_array(data), result := (ctypes.c_int * 4)()), ((result[0], result[1]), (result[2], result[3])))

    return node


if __name__ == '__main__':
    data = np.random.randint(0, 11, size=(10, 9))

    node = choose_algo(data)
    print(node)
