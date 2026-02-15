import time
from collections import defaultdict
import numpy as np

FLOW_TIMEOUT = 10  # seconds

flows = {}

# =========================================================
# FLOW IDENTIFIER (5‑tuple)
# =========================================================

def get_flow_id(packet):
    src = getattr(packet, "src", "0.0.0.0")
    dst = getattr(packet, "dst", "0.0.0.0")
    sport = getattr(packet, "sport", 0)
    dport = getattr(packet, "dport", 0)
    proto = getattr(packet, "proto", 0)

    return (src, dst, sport, dport, proto)


# =========================================================
# UPDATE FLOW
# =========================================================

def update_flow(packet):
    now = time.time()
    flow_id = get_flow_id(packet)
    reverse_id = (flow_id[1], flow_id[0], flow_id[3], flow_id[2], flow_id[4])

    pkt_len = len(packet)
    header_len = len(packet.payload) if hasattr(packet, "payload") else 0

    # Determine direction
    if flow_id in flows:
        direction = "fwd"
    elif reverse_id in flows:
        flow_id = reverse_id
        direction = "bwd"
    else:
        flows[flow_id] = {
            "start_time": now,
            "last_seen": now,
            "fwd_packets": 0,
            "bwd_packets": 0,
            "fwd_bytes": 0,
            "bwd_bytes": 0,
            "fwd_lengths": [],
            "bwd_lengths": [],
            "iat_times": [],
            "last_packet_time": now,
            "flags": defaultdict(int),
            "header_fwd": 0,
            "header_bwd": 0
        }
        direction = "fwd"

    flow = flows[flow_id]

    # Update timestamps
    flow["iat_times"].append(now - flow["last_packet_time"])
    flow["last_packet_time"] = now
    flow["last_seen"] = now

    # Update direction stats
    if direction == "fwd":
        flow["fwd_packets"] += 1
        flow["fwd_bytes"] += pkt_len
        flow["fwd_lengths"].append(pkt_len)
        flow["header_fwd"] += header_len
    else:
        flow["bwd_packets"] += 1
        flow["bwd_bytes"] += pkt_len
        flow["bwd_lengths"].append(pkt_len)
        flow["header_bwd"] += header_len

    # TCP flags (if available)
    if hasattr(packet, "flags"):
        for flag in ["F", "S", "R", "P", "A", "U", "E", "C"]:
            if flag in str(packet.flags):
                flow["flags"][flag] += 1

    duration = now - flow["start_time"]

    if duration >= FLOW_TIMEOUT:
        features = compute_features(flow, duration)
        src_ip = flow_id[0]
        del flows[flow_id]
        return features, src_ip

    return None, None


# =========================================================
# FEATURE COMPUTATION
# =========================================================

def compute_features(flow, duration):

    if duration == 0:
        duration = 1

    def safe_stats(values):
        if len(values) == 0:
            return 0, 0, 0, 0
        return (
            max(values),
            min(values),
            np.mean(values),
            np.std(values)
        )

    fwd_max, fwd_min, fwd_mean, fwd_std = safe_stats(flow["fwd_lengths"])
    bwd_max, bwd_min, bwd_mean, bwd_std = safe_stats(flow["bwd_lengths"])
    iat_max, iat_min, iat_mean, iat_std = safe_stats(flow["iat_times"])

    total_packets = flow["fwd_packets"] + flow["bwd_packets"]
    total_bytes = flow["fwd_bytes"] + flow["bwd_bytes"]

    features = {
        "Flow Duration": duration,
        "Tot Fwd Pkts": flow["fwd_packets"],
        "Tot Bwd Pkts": flow["bwd_packets"],
        "TotLen Fwd Pkts": flow["fwd_bytes"],
        "TotLen Bwd Pkts": flow["bwd_bytes"],

        "Fwd Pkt Len Max": fwd_max,
        "Fwd Pkt Len Min": fwd_min,
        "Fwd Pkt Len Mean": fwd_mean,
        "Fwd Pkt Len Std": fwd_std,

        "Bwd Pkt Len Max": bwd_max,
        "Bwd Pkt Len Min": bwd_min,
        "Bwd Pkt Len Mean": bwd_mean,
        "Bwd Pkt Len Std": bwd_std,

        "Flow Byts/s": total_bytes / duration,
        "Flow Pkts/s": total_packets / duration,

        "Fwd IAT Tot": sum(flow["iat_times"]),
        "Fwd IAT Mean": iat_mean,
        "Fwd IAT Std": iat_std,
        "Fwd IAT Max": iat_max,
        "Fwd IAT Min": iat_min,

        "Fwd Header Len": flow["header_fwd"],
        "Bwd Header Len": flow["header_bwd"],

        "FIN Flag Cnt": flow["flags"]["F"],
        "SYN Flag Cnt": flow["flags"]["S"],
        "RST Flag Cnt": flow["flags"]["R"],
        "PSH Flag Cnt": flow["flags"]["P"],
        "ACK Flag Cnt": flow["flags"]["A"],
        "URG Flag Cnt": flow["flags"]["U"],
        "ECE Flag Cnt": flow["flags"]["E"]
    }

    return features
