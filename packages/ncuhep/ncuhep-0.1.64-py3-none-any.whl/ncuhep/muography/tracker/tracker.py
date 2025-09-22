import numpy as np
from ..utils import track_reconstruction
from numba import njit, prange


@njit
def uniqueid2position(unique_id, layer_id):
    if layer_id == 2:
        unique_id -= 144
        y = unique_id // 8
        x = unique_id % 8

        y *= 50
        x *= 50

        y -= 50 * 3.5
        x -= 50 * 3.5

        z = -250
    elif layer_id == 3:
        unique_id -= 144 + 64

        y = unique_id // 8
        x = unique_id % 8

        y *= 50
        x *= 50

        y -= 50 * 3.5
        x -= 50 * 3.5

        z = 250
    elif layer_id == 4:
        unique_id -= 144 + 64 + 64

        y = unique_id // 12
        x = unique_id % 12

        y *= 50
        x *= 50

        y -= 50 * 5.5
        x -= 50 * 5.5

        z = 750
    else:
        y = unique_id // 12
        x = unique_id % 12

        y *= 50
        x *= 50

        y -= 50 * 5.5
        x -= 50 * 5.5

        z = -750

    return np.array([x, y, z])

@njit
def uniqueid2positions(unique_ids, layer_ids):
    positions = np.empty((len(unique_ids), 3), dtype=np.float64)
    for i in prange(len(unique_ids)):
        positions[i] = uniqueid2position(unique_ids[i], layer_ids[i])
    return positions


@njit
def lsq(positions, track):
    x = positions[:, 0]
    y = positions[:, 1]
    z = positions[:, 2]

    intercept_x, intercept_y, theta_x, theta_y = track

    m_x = np.tan(np.radians(theta_x))
    m_y = np.tan(np.radians(theta_y))

    x_ = m_x * z + intercept_x
    y_ = m_y * z + intercept_y

    chi2 = np.sum((x - x_)**2 + (y - y_)**2) / (50 ** 2 / 12)
    return chi2 / (len(positions) - 2)


def tracker(events):
    events_tracked = []
    for event in events:
        if event is None:
            continue
        positions = uniqueid2positions(event["UNIQUEID"], event["LAYERID"])
        track = track_reconstruction(positions)

        event_data = {
            "LAYERID": event["LAYERID"],
            "UNIQUEID": event["UNIQUEID"],
            "TIMESTAMP": event["TIMESTAMP"],
            "PCNT": event["PCNT"],
            "TCNT": event["TCNT"],
            "PWIDTH": event["PWIDTH"],
            "TRACK": track,
            "CHI2": lsq(positions, track)
        }

        events_tracked.append(event_data)

    return np.array(events_tracked, dtype=object)

