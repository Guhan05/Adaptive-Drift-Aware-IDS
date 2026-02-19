import time
import random
import argparse
import requests
import subprocess
from collections import deque, defaultdict
from datetime import datetime

# Optional Scapy import for live mode
try:
    from scapy.all import sniff, IP, TCP, UDP
    SCAPY_AVAILABLE = True
except:
    SCAPY_AVAILABLE = False

BACKEND_URL = "http://localhost:9000"

# ---------------- CONFIG ----------------

BASE_THRESHOLD = 150
dynamic_threshold = 150

MAX_THRESHOLD = 200
MIN_THRESHOLD = 130

BLOCK_DURATION = 300  # seconds (5 minutes)

SAFE_IPS = {
    "127.0.0.1",
    "0.0.0.0",
}

blocked_ips = {}

risk_window = deque(maxlen=50)
drift_window = deque(maxlen=20)
mode_window = deque(maxlen=50)

trust_scores = defaultdict(lambda: 0.7)

current_mode = "STABLE"
current_profile = "precision"

SSI_GAIN = 25
DAMPING = 0.2
TRUST_GOV_GAIN = 0.5

# ---------------- PROFILE ----------------

def configure_profile(profile):
    global SSI_GAIN, DAMPING, TRUST_GOV_GAIN, MIN_THRESHOLD, current_profile

    current_profile = profile

    if profile == "precision":
        SSI_GAIN = 25
        TRUST_GOV_GAIN = 0.5
        DAMPING = 0.25
        MIN_THRESHOLD = 145

    elif profile == "balanced":
        SSI_GAIN = 20
        TRUST_GOV_GAIN = 0.3
        DAMPING = 0.2
        MIN_THRESHOLD = 140

    elif profile == "aggressive":
        SSI_GAIN = 15
        TRUST_GOV_GAIN = 0.1
        DAMPING = 0.15
        MIN_THRESHOLD = 130

# ---------------- DRIFT ----------------

def calculate_drift():
    return random.uniform(0, 0.3)

# ---------------- MODE ----------------

def update_mode(drift):
    global current_mode
    if drift < 0.1:
        current_mode = "STABLE"
    elif drift < 0.2:
        current_mode = "ALERT"
    else:
        current_mode = "DEFENSIVE"
    mode_window.append(current_mode)

# ---------------- SSI ----------------

def compute_variance(values):
    if len(values) < 2:
        return 0
    mean = sum(values) / len(values)
    return sum((x - mean) ** 2 for x in values) / len(values)

def compute_mode_switch_rate():
    if len(mode_window) < 2:
        return 0
    switches = sum(
        1 for i in range(1, len(mode_window))
        if mode_window[i] != mode_window[i - 1]
    )
    return switches / len(mode_window)

def compute_average_trust():
    if not trust_scores:
        return 0.7
    return sum(trust_scores.values()) / len(trust_scores)

def compute_ssi():
    risk_var = compute_variance(risk_window)
    drift_var = compute_variance(drift_window)
    mode_rate = compute_mode_switch_rate()

    avg_trust = compute_average_trust()
    trust_multiplier = 1 + TRUST_GOV_GAIN * (1 - avg_trust)

    adjusted_risk_var = risk_var * trust_multiplier

    risk_norm = min(adjusted_risk_var / 1000, 1)
    drift_norm = min(drift_var / 0.05, 1)

    ssi = 0.5 * risk_norm + 0.3 * drift_norm + 0.2 * mode_rate
    return min(ssi, 1)

# ---------------- GOVERNANCE ----------------

def governance_controller(ssi):
    global dynamic_threshold

    target = BASE_THRESHOLD + (SSI_GAIN * ssi)

    dynamic_threshold = (
        (1 - DAMPING) * dynamic_threshold +
        DAMPING * target
    )

    dynamic_threshold = max(
        MIN_THRESHOLD,
        min(dynamic_threshold, MAX_THRESHOLD)
    )

# ---------------- TRUST ----------------

def update_trust(ip, blocked):
    if blocked:
        trust_scores[ip] -= 0.05
    else:
        trust_scores[ip] += 0.01

    trust_scores[ip] = max(0, min(1, trust_scores[ip]))

# ---------------- FIREWALL CONTROL ----------------

def block_ip(ip):
    if ip in SAFE_IPS:
        return

    if ip in blocked_ips:
        return

    rule_name = f"IDS_BLOCK_{ip}"

    cmd = (
        f'netsh advfirewall firewall add rule '
        f'name="{rule_name}" dir=in action=block remoteip={ip}'
    )

    subprocess.run(cmd, shell=True)

    blocked_ips[ip] = time.time()
    print(f"[FIREWALL] Blocked {ip}")

def unblock_expired():
    now = time.time()

    for ip in list(blocked_ips.keys()):
        if now - blocked_ips[ip] > BLOCK_DURATION:
            rule_name = f"IDS_BLOCK_{ip}"
            cmd = (
                f'netsh advfirewall firewall delete rule '
                f'name="{rule_name}"'
            )
            subprocess.run(cmd, shell=True)
            del blocked_ips[ip]
            print(f"[FIREWALL] Unblocked {ip}")

# ---------------- BACKEND COMM ----------------

def send_event(event):
    try:
        requests.post(f"{BACKEND_URL}/ingest", json=event, timeout=1)
    except:
        pass

def send_governance(ssi, threshold, trust, profile):
    try:
        requests.post(
            f"{BACKEND_URL}/ingest_governance",
            json={
                "ssi": ssi,
                "threshold": threshold,
                "trust": trust,
                "profile": profile
            },
            timeout=1
        )
    except:
        pass

# ---------------- EVENT PROCESSING ----------------

def process_event(src_ip, dst_ip, risk, live=False):

    unblock_expired()

    drift = calculate_drift()
    drift_window.append(drift)
    update_mode(drift)

    risk_window.append(risk)

    ssi = compute_ssi()
    governance_controller(ssi)

    blocked = False

    if live:
        avg_trust = trust_scores[src_ip]

        if (
            risk > dynamic_threshold and
            ssi > 0.5 and
            avg_trust < 0.6
        ):
            block_ip(src_ip)
            blocked = True
    else:
        blocked = risk > dynamic_threshold

    update_trust(src_ip, blocked)

    event = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "risk": round(risk, 2),
        "level": "HIGH" if blocked else "LOW",
        "mode": current_mode,
        "drift": round(drift, 4),
        "action": "BLOCKED" if blocked else "MONITOR",
        "alert": True if blocked else False
    }

    send_event(event)
    send_governance(
        ssi,
        dynamic_threshold,
        compute_average_trust(),
        current_profile
    )

# ---------------- REPLAY MODE ----------------

def replay_mode():
    print("Running REPLAY MODE (Ctrl+C to stop)")
    try:
        while True:
            src_ip = f"192.168.1.{random.randint(1,20)}"
            dst_ip = f"10.0.0.{random.randint(1,10)}"
            risk = random.uniform(5, 220)

            process_event(src_ip, dst_ip, risk, live=False)

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nReplay mode stopped safely.")

# ---------------- LIVE MODE ----------------

def packet_handler(packet):
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst

        risk = 0
        if TCP in packet:
            risk += 40
        if UDP in packet:
            risk += 20
        if len(packet) > 1000:
            risk += 60

        process_event(src_ip, dst_ip, risk, live=True)

def live_mode():
    if not SCAPY_AVAILABLE:
        print("Scapy not installed. Run: pip install scapy")
        return

    print("Running LIVE MODE (Admin required, Ctrl+C to stop)")
    try:
        sniff(prn=packet_handler, store=False)
    except KeyboardInterrupt:
        print("\nLive mode stopped safely.")

# ---------------- ENTRY ----------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        default="replay",
        choices=["replay", "live"]
    )
    args = parser.parse_args()

    configure_profile("precision")

    try:
        if args.mode == "live":
            live_mode()
        else:
            replay_mode()
    except KeyboardInterrupt:
        print("\nSystem shutdown complete.")
