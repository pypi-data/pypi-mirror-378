import numpy as np
from numba import njit, prange
import os
import time
import pandas as pd


@njit(cache=True)
def pcnt_correction(pcnt):
    timestamp = np.zeros_like(pcnt)
    previous_timestamp = None

    for n, pcnt in enumerate(pcnt):
        if previous_timestamp is None:
            previous_timestamp = pcnt
            timestamp[n] = pcnt
        else:
            if pcnt < previous_timestamp:
                if previous_timestamp - pcnt > 2 ** 17:
                    timestamp[n] = pcnt + 2 ** 20
                else:
                    timestamp[n] = previous_timestamp
            else:
                timestamp[n] = pcnt

            previous_timestamp = timestamp[n]

    return timestamp


def get_timestamp(pcnt, tcnt):
    pcnt = pcnt.astype(np.uint64)
    pcnt = pcnt << 32
    tcnt = tcnt.astype(np.uint64)

    timestamp = pcnt + tcnt
    return timestamp


@njit(parallel=True, cache=True)
def get_layer(boardID, mapping):
    layerID = np.zeros(len(boardID))
    for N in prange(len(boardID)):
        ID = boardID[N]
        layerID[N] = mapping[int(ID) - 1]

    return layerID


@njit(parallel=True, cache=True)
def get_unique_id(boardID, channelID, mapping):
    unique_id = np.zeros_like(boardID, dtype=np.uint16)
    for n in prange(len(boardID)):
        unique_id[n] = mapping[int(boardID[n] - 1), int(channelID[n])]

    return unique_id


# 0 - Type
# 1 - Board ID
# 2 - Channel ID
# 3 - EVT
# 4 - Timestamp
# 5 - PCNT
# 6 - TCNT
# 7 - PWIDTH


@njit(cache=True)
def label(timestamp, event_threshold=75, hit_threshold=15):
    current_label = 0
    initial_timestamp = timestamp[0]
    previous_timestamp = timestamp[0]
    labels = np.zeros(len(timestamp), dtype=np.uint64)

    for n in range(1, len(timestamp)):
        current_timestamp = timestamp[n]

        if current_timestamp - previous_timestamp > hit_threshold or current_timestamp - initial_timestamp > event_threshold:
            current_label += 1
            initial_timestamp = current_timestamp

        previous_timestamp = current_timestamp
        labels[n] = current_label

    return labels


def event_grouping(data, event_selection):
    # Create a structured array for all hits
    dtype = [
        ("EVENTID", data["EVENTID"].dtype),
        ("BOARDID", data["BOARDID"].dtype),
        ("CHANNELID", data["CHANNELID"].dtype),
        ("LAYERID", data["LAYERID"].dtype),
        ("UNIQUEID", data["UNIQUEID"].dtype),
        ("TIMESTAMP", data["TIMESTAMP"].dtype),
        ("PCNT", data["PCNT"].dtype),
        ("TCNT", data["TCNT"].dtype),
        ("PWIDTH", data["PWIDTH"].dtype),
    ]
    hits = np.empty(len(data["EVENTID"]), dtype=dtype)
    for key in hits.dtype.names:
        hits[key] = data[key]

    # Group by EVENTID and filter events
    event_ids, start_idx, counts = np.unique(hits["EVENTID"], return_index=True, return_counts=True)
    keep_mask = np.zeros(len(hits), dtype=bool)

    for eid, idx, count in zip(event_ids, start_idx, counts):
        event_slice = slice(idx, idx + count)
        event = {k: hits[k][event_slice] for k in hits.dtype.names if k != "EVENTID"}
        if event_selection(event):
            keep_mask[event_slice] = True

    return hits[keep_mask]


def event_grouping_fast(data, layers=(1, 2, 3, 4), max_per_layer=(3, 3, 3, 2), max_total=8):
    """
    Vectorized grouping & filtering.
    - `layers`: the 4 actual LAYERID codes in ascending order (e.g., (1,2,3,4) or (0,1,2,3)).
    - `max_per_layer`: per-layer maxima applied in that same order.
    - `max_total`: maximum total hits per event (all hits, any layer).
    Returns a structured array of kept rows (same dtype set as your original).
    """
    EVENTID = data["EVENTID"]
    LAYERID = data["LAYERID"]
    n = EVENTID.size

    # Prepare output dtype (no full copy up-front)
    dtype = [
        ("EVENTID", EVENTID.dtype),
        ("BOARDID", data["BOARDID"].dtype),
        ("CHANNELID", data["CHANNELID"].dtype),
        ("LAYERID", LAYERID.dtype),
        ("UNIQUEID", data["UNIQUEID"].dtype),
        ("TIMESTAMP", data["TIMESTAMP"].dtype),
        ("PCNT", data["PCNT"].dtype),
        ("TCNT", data["TCNT"].dtype),
        ("PWIDTH", data["PWIDTH"].dtype),
    ]
    if n == 0:
        return np.empty(0, dtype=dtype)

    # 1) Sort once by EVENTID (stable)
    order = np.argsort(EVENTID, kind="mergesort")
    eid_sorted = EVENTID[order]
    starts = np.r_[0, 1 + np.flatnonzero(np.diff(eid_sorted))]
    stops = np.r_[starts[1:], n]
    counts_total = stops - starts  # total hits per event (all layers)

    # 2) Map your actual layer codes -> {0,1,2,3}
    layers = np.asarray(layers)
    lid_sorted = LAYERID[order]
    idx = np.searchsorted(layers, lid_sorted)
    valid = (idx < layers.size) & (layers[idx] == lid_sorted)
    mapped = np.where(valid, idx, -1)  # -1 = not one of the four target layers

    # 3) Per-layer counts via segment sums
    c = []
    for k in range(layers.size):
        c_k = np.add.reduceat((mapped == k).astype(np.int32), starts)
        c.append(c_k)
    c0, c1, c2, c3 = c

    # 4) Apply selection (require all four target layers present)
    have_all = (c0 > 0) & (c1 > 0) & (c2 > 0) & (c3 > 0)
    limits_ok = (c0 <= max_per_layer[0]) & (c1 <= max_per_layer[1]) \
                & (c2 <= max_per_layer[2]) & (c3 <= max_per_layer[3])
    total_ok = (counts_total <= max_total)
    keep_group = have_all & limits_ok & total_ok

    # 5) Expand to row mask and map back to original order
    mask_sorted = np.repeat(keep_group, counts_total)
    row_mask = np.empty(n, dtype=bool)
    row_mask[order] = mask_sorted
    keep_idx = np.nonzero(row_mask)[0]

    out = np.empty(keep_idx.size, dtype=dtype)
    for name, _ in dtype:
        out[name] = data[name][keep_idx]
    return out


def parser(dir, file, unique_id_mapping, layer_mapping, event_threshold=75, hit_threshold=75):
    filepath = os.path.join(dir, file)

    cols = [1, 2, 4, 5, 6, 7]  # zero-based column indices
    names = ["BOARDID", "CHANNELID", "TIMESTAMP", "PCNT", "TCNT", "PWIDTH"]
    dtypes = {"BOARDID": "uint8",
              "CHANNELID": "uint8",
              "TIMESTAMP": "float64",
              "PCNT": "uint32",
              "TCNT": "uint32",
              "PWIDTH": "uint8"}

    df = pd.read_csv(
        filepath,
        sep="\t",
        header=None,
        usecols=cols,
        names=names,
        comment="#",  # lines starting with '#' (e.g. "#Frame") are skipped
        dtype=dtypes,
        engine="c",
        memory_map=True,
        na_filter=False,  # tiny speedup
        skip_blank_lines=False  # keep exact row count semantics
    )

    BOARDID = df["BOARDID"].to_numpy(copy=False)
    CHANNELID = df["CHANNELID"].to_numpy(copy=False)
    TIMESTAMP = df["TIMESTAMP"].to_numpy(copy=False)
    PCNT = df["PCNT"].to_numpy(copy=False)
    TCNT = df["TCNT"].to_numpy(copy=False)
    PWIDTH = df["PWIDTH"].to_numpy(copy=False)

    valid_line_count = len(df)

    data = {
        "BOARDID": BOARDID,
        "CHANNELID": CHANNELID,
        "TIMESTAMP": TIMESTAMP,
        "PCNT": PCNT,
        "TCNT": TCNT,
        "PWIDTH": PWIDTH
    }

    # mask = data["PWIDTH"] > 15
    # data = {key: data[key][mask] for key in data}

    start = time.time()
    data["PCNT"] = pcnt_correction(data["PCNT"])

    timeelapsed = np.amax(data["PCNT"]) - np.amin(data["PCNT"])

    if timeelapsed > 87000:
        print(f"Time elapsed: {timeelapsed}")

    data["TIMESTAMP"] = get_timestamp(data["PCNT"], data["TCNT"]).astype(np.uint64)

    sort = np.argsort(data["TIMESTAMP"])

    data = {key: data[key][sort] for key in data}

    data["UNIQUEID"] = get_unique_id(data["BOARDID"], data["CHANNELID"], unique_id_mapping)
    data["LAYERID"] = get_layer(data["BOARDID"], layer_mapping)

    data["EVENTID"] = label(data["TIMESTAMP"], event_threshold=event_threshold, hit_threshold=hit_threshold)

    events = event_grouping_fast(data)

    return events



