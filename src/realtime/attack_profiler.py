def profile_attack(features, risk_score):

    flow_pkts = features.get("Tot Fwd Pkts", 0) + features.get("Tot Bwd Pkts", 0)
    flow_bytes = features.get("TotLen Fwd Pkts", 0) + features.get("TotLen Bwd Pkts", 0)
    flow_rate = features.get("Flow Pkts/s", 0)

    syn_flags = features.get("SYN Flag Cnt", 0)
    rst_flags = features.get("RST Flag Cnt", 0)

    # High packet rate flood
    if flow_rate > 1000 and flow_pkts > 200:
        return "DDoS / Flood Pattern"

    # SYN heavy → likely scanning or SYN flood
    if syn_flags > 10 and rst_flags > 5:
        return "Port Scanning"

    # Very high packets but low bytes
    if flow_pkts > 300 and flow_bytes < 50000:
        return "Brute Force Pattern"

    # Large sustained transfer
    if flow_bytes > 5_000_000:
        return "Possible Data Exfiltration"

    # Low and slow suspicious
    if risk_score > 70 and flow_rate < 5:
        return "Low-and-Slow Suspicious Behavior"

    return "Generic Malicious Behavior"
