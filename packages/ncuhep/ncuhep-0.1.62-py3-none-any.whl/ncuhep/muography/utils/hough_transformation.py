import numpy as np
import matplotlib.pyplot as plt
from numba import njit


@njit
def array2combo(array: np.ndarray, layer_z: np.ndarray):

    counts = np.zeros(len(layer_z), dtype=np.int32)

    for i in range(len(layer_z)):
        counts[i] = np.sum(array[:, 1] == layer_z[i])

    combos = 1
    for c in counts:
        if c > 1:
            combos *= c

    L = len(layer_z)
    result = np.empty((combos, L, 2), dtype=array.dtype)
    index = np.zeros(L, dtype=np.int32)

    for i in range(combos):
        for j in range(L):
            layer_hits = array[array[:, 1] == layer_z[j]]
            if len(layer_hits) > 0:
                result[i, j] = layer_hits[index[j] % len(layer_hits)]
            else:
                result[i, j] = np.array([np.nan, layer_z[j]])

        for j in range(L - 1, -1, -1):
            if counts[j] > 0:
                index[j] += 1
                if index[j] < counts[j]:
                    break
                index[j] = 0

    return result


@njit
def intercept(pos1: np.ndarray, pos2: np.ndarray):
    a = np.arctan2(pos1[0] - pos2[0], pos1[1] - pos2[1])
    b = pos1[0] - np.tan(a) * pos1[1]

    return np.array([a, b])


@njit
def multiple_intercept(positions: np.ndarray, delta_b: float):
    n = positions.shape[0]
    intercepts_ = np.zeros((n, n, 2), dtype=float)
    z_ = np.zeros((n, n), dtype=float)

    for i in range(n):
        for j in range(n):
            if i <= j:
                intercepts_[i, j, :] = (np.nan, np.nan)
                z_[i, j] = np.nan
            else:
                if np.isnan(positions[i, 0]) or np.isnan(positions[j, 0]):
                    intercepts_[i, j, :] = (np.nan, np.nan)
                    z_[i, j] = np.nan
                else:
                    intercepts_[i, j, :] = intercept_(positions[i], positions[j])
                    z_[i, j] = np.abs(positions[j, 1] - positions[i, 1])

    intercepts_ = intercepts_.reshape(-1, 2)
    z_ = z_.reshape(-1)

    mask = np.ones(intercepts_.shape[0], dtype=np.bool_)
    for i in range(intercepts_.shape[0]):
        if np.isnan(intercepts_[i, 0]) or np.isnan(intercepts_[i, 1]):
            mask[i] = False

    intercepts_ = intercepts_[mask]
    z_ = z_[mask]

    centroid_a = np.average(intercepts_[:, 0], weights=1/z_)
    centroid_b = np.mean(intercepts_[:, 1])

    centroid = np.array([centroid_a, centroid_b])

    intercepts_ -= centroid

    b_lsq = np.sum((intercepts_[:, 1]/delta_b)**2)
    a_lsq = np.sum((intercepts_[:, 0]/(delta_b/z_))**2)

    lsq = a_lsq + b_lsq
    return lsq



