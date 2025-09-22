from ncuhep.muography.utils import multiple_intercept, array2combo
import numpy as np
import os
from numba import njit, prange
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

@njit(cache=True, fastmath=True)
def uniqueid2position(unique_id, layer_id, idx, x_row, y_row, idx_row):
    # returns nothing; fills x_row[:], y_row[:], idx_row[:] in-place
    # geometry table: (base_sub, cols, half_cols, half_rows, z)
    # layer_id: 1->(-,12,5.5,5.5,-750), 2->(144,8,3.5,3.5,-250), 3->(208,8,3.5,3.5, 250), 4->(272,12,5.5,5.5, 750)
    if layer_id == 2:
        base, cols, half, z = 144, 8, 3.5, -250.0
        u = unique_id - base
        yy = (u // cols) * 50.0 - 50.0 * half
        xx = (u %  cols) * 50.0 - 50.0 * half
    elif layer_id == 3:
        base, cols, half, z = 144 + 64, 8, 3.5, 250.0
        u = unique_id - base
        yy = (u // cols) * 50.0 - 50.0 * half
        xx = (u %  cols) * 50.0 - 50.0 * half
    elif layer_id == 4:
        base, cols, half, z = 144 + 64 + 64, 12, 5.5, 750.0
        u = unique_id - base
        yy = (u // cols) * 50.0 - 50.0 * half
        xx = (u %  cols) * 50.0 - 50.0 * half
    else:  # layer 1
        cols, half, z = 12, 5.5, -750.0
        u = unique_id
        yy = (u // cols) * 50.0 - 50.0 * half
        xx = (u %  cols) * 50.0 - 50.0 * half

    x_row[0] = xx;         x_row[1] = z
    y_row[0] = yy;         y_row[1] = z
    idx_row[0] = idx;      idx_row[1] = z


def split_events_sorted(array):
    # one stable sort
    order = np.argsort(array['EVENTID'], kind='mergesort')
    eid_sorted = array['EVENTID'][order]
    starts = np.r_[0, 1 + np.flatnonzero(eid_sorted[1:] != eid_sorted[:-1])]
    stops  = np.r_[starts[1:], eid_sorted.size]

    events = []
    for s, e in zip(starts, stops):
        sl = order[s:e]
        events.append({
            "BOARDID":  array['BOARDID'][sl],
            "CHANNELID":array['CHANNELID'][sl],
            "LAYERID":  array['LAYERID'][sl],
            "UNIQUEID": array['UNIQUEID'][sl],
            "TIMESTAMP":array['TIMESTAMP'][sl],
            "PCNT":     array['PCNT'][sl],
            "TCNT":     array['TCNT'][sl],
            "PWIDTH":   array['PWIDTH'][sl],
        })
    return events

def identify(events):
    layer_z = np.array([-750, -250, 250, 750], dtype=np.float32)
    delta_b = 50 / np.sqrt(12)
    reults = np.empty(len(events), dtype=object)

    for i in tqdm(range(len(events))):
        event = events[i]

        unique_id = event["UNIQUEID"]
        layer_id = event["LAYERID"]
        index = np.arange(len(unique_id), dtype=np.float32)

        if len(unique_id) > 8:
            reults[i] = None
            continue

        x_array = np.empty((len(unique_id), 2), np.float32)
        y_array = np.empty_like(x_array)
        index_array = np.empty_like(x_array)

        for n in range(len(unique_id)):
            uniqueid2position(unique_id[n], layer_id[n], index[n], x_array[n], y_array[n], index_array[n])

        x_combinations = array2combo(x_array, layer_z)
        y_combinations = array2combo(y_array, layer_z)
        index_combinations = array2combo(index_array, layer_z)


        lsq = None
        best_index = None
        for x_combination, y_combination, index_combination in zip(x_combinations, y_combinations, index_combinations):
            x_lsq = multiple_intercept(x_combination, delta_b)
            y_lsq = multiple_intercept(y_combination, delta_b)


            if np.isnan(x_lsq) or np.isnan(y_lsq):
                continue

            if lsq is None or x_lsq + y_lsq < lsq:
                lsq = x_lsq + y_lsq
                best_index = index_combination[:, 0]

        if best_index is not None:
            idxs = best_index[np.isfinite(best_index)].astype(np.intp, copy=False)
            mask = np.zeros(len(unique_id), dtype=bool)
            mask[idxs] = True

            reults[i] = {
                "BOARDID": event["BOARDID"][mask],
                "CHANNELID": event["CHANNELID"][mask],
                "LAYERID": event["LAYERID"][mask],
                "UNIQUEID": event["UNIQUEID"][mask],
                "TIMESTAMP": event["TIMESTAMP"][mask],
                "PCNT": event["PCNT"][mask],
                "TCNT": event["TCNT"][mask],
                "PWIDTH": event["PWIDTH"][mask],
            }
        else:
            reults[i] = None

    return reults

def identifier(events):
    split_events = split_events_sorted(events)
    identified_events = identify(split_events)

    return identified_events





