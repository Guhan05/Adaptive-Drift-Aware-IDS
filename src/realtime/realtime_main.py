import time
import random
import requests
import argparse
import subprocess
import signal
import sys
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP

BACKEND_URL = "http://localhost:9000"

memory = {}
blocked_ips = {}
current_mode = "STABLE"
drift_score = 0.0
running = True  # Control flag for stopping

BLOCK_DURATION = 600  # 10 minutes


# ------------------ SIGNAL HANDLER ------------------

def signal_handler(sig, frame):
    global running
    print("\nStopping IDS gracefully...")
    running = False


signal.signal(signal.SIGINT, signal_handler)


# ------------------ CORE LOGIC ------------------

def calculate_drift():
    return random.uniform(0, 0.3)


def update_mode(drift):
    global current_mode
    if drift < 0.1:
        current_mode = "STABLE"
    elif drift < 0.2:
        current_mode = "ALERT"
    else:
        current_mode = "DEFENSIVE"


def fusion_risk(model_output, drift, ip):
    previous = memory.get(ip, 0)

    if current_mode == "STABLE":
        decay = 0.5
    elif current_mode == "ALERT":
        decay = 0.7
    else:
        decay = 0.9

    accumulated = decay * previous + model_output * (1 + drift)
    memory[ip] = accumulated
    return accumulated


def simple_anomaly_score(packet):
    score = 0

    if TCP in packet:
        if packet[TCP].flags == "S":
            score += 50

    if UDP in packet:
        score += 10

    if len(packet) > 1000:
        score += 30

    return min(score, 100)


def block_ip(ip):
    if ip in blocked_ips:
        return

    rule_name = f"IDS_BLOCK_{ip}"
    cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip}'
    subprocess.run(cmd, shell=True)

    blocked_ips[ip] = time.time()
    print(f"[FIREWALL] Blocked {ip}")


def unblock_expired_ips():
    current_time = time.time()
    for ip in list(blocked_ips.keys()):
        if current_time - blocked_ips[ip] > BLOCK_DURATION:
            rule_name = f"IDS_BLOCK_{ip}"
            cmd = f'netsh advfirewall firewall delete rule name="{rule_name}"'
            subprocess.run(cmd, shell=True)
            del blocked_ips[ip]
            print(f"[FIREWALL] Unblocked {ip}")


def decide_action(risk, ip):
    threshold = 150 * (1 + drift_score)

    if risk > threshold:
        block_ip(ip)
        return "BLOCKED", "HIGH"
    elif risk > 60:
        return "MONITOR", "MEDIUM"
    return "MONITOR", "LOW"


# ------------------ PACKET PROCESSOR ------------------

def process_packet(packet):
    global drift_score

    if not running:
        return True  # Stop sniffing

    if IP not in packet:
        return False

    unblock_expired_ips()

    drift_score = calculate_drift()
    update_mode(drift_score)

    src_ip = packet[IP].src
    dst_ip = packet[IP].dst

    model_output = simple_anomaly_score(packet)
    final_risk = fusion_risk(model_output, drift_score, src_ip)
    action, level = decide_action(final_risk, src_ip)

    event = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "risk": round(final_risk, 2),
        "level": level,
        "action": action,
        "drift": round(drift_score, 4),
        "mode": current_mode,
        "alert": True if level == "HIGH" else False
    }

    try:
        requests.post(f"{BACKEND_URL}/ingest", json=event)
    except:
        pass

    print(f"[LIVE] {src_ip} → {dst_ip} | Risk={final_risk:.2f} | {action}")

    return False


# ------------------ MODES ------------------

def live_mode():
    print("Live packet capture started... Press Ctrl+C to stop.")
    sniff(
        prn=process_packet,
        store=False,
        stop_filter=lambda x: not running
    )
    print("Live capture stopped.")


def replay_mode():
    global drift_score

    print("Replay mode started... Press Ctrl+C to stop.")
    try:
        while True:
            drift_score = calculate_drift()
            update_mode(drift_score)

            src_ip = f"192.168.1.{random.randint(1, 50)}"
            dst_ip = f"10.0.0.{random.randint(1, 10)}"

            model_output = random.uniform(10, 90)
            final_risk = fusion_risk(model_output, drift_score, src_ip)
            action, level = decide_action(final_risk, src_ip)

            event = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "risk": round(final_risk, 2),
                "level": level,
                "action": action,
                "drift": round(drift_score, 4),
                "mode": current_mode,
                "alert": True if level == "HIGH" else False
            }

            requests.post(f"{BACKEND_URL}/ingest", json=event)
            print(f"[REPLAY] {src_ip} → {dst_ip} | Risk={final_risk:.2f}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nReplay stopped.")


# ------------------ ENTRY POINT ------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="replay")
    args = parser.parse_args()

    if args.mode == "live":
        live_mode()
    else:
        replay_mode()
