from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict, deque
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_LOGS = 500
MAX_HISTORY = 300

state = {
    "total_flows": 0,
    "total_blocks": 0,
    "drift": 0.0,
    "risk_sum": 0.0,
    "logs": [],
    "attack_counts": defaultdict(int),
    "blocked_ips": {},

    "risk_history": deque(maxlen=MAX_HISTORY),
    "drift_history": deque(maxlen=MAX_HISTORY),
    "ssi_history": deque(maxlen=MAX_HISTORY),
    "threshold_history": deque(maxlen=MAX_HISTORY),
    "trust_scores": defaultdict(lambda: 0.7),
    "profile_history": deque(maxlen=MAX_HISTORY),
}


# ---------------- IDS EVENT INGEST ----------------

@app.post("/ingest")
def ingest(event: dict):

    state["total_flows"] += 1

    risk = float(event.get("risk", 0))
    drift = float(event.get("drift", 0))
    threshold = float(event.get("threshold", 150))
    action = event.get("action", "MONITOR")
    src_ip = event.get("src_ip")

    state["risk_sum"] += risk
    state["drift"] = drift

    if action == "BLOCKED":
        state["total_blocks"] += 1
        if src_ip:
            state["blocked_ips"][src_ip] = event.get(
                "timestamp", datetime.now().strftime("%H:%M:%S")
            )

    level = event.get("level", "LOW")
    state["attack_counts"][level] += 1

    # Ensure protocol exists
    if "protocol" not in event:
        event["protocol"] = "N/A"

    state["logs"].append(event)
    if len(state["logs"]) > MAX_LOGS:
        state["logs"].pop(0)

    state["risk_history"].append({
        "time": event.get("timestamp"),
        "risk": risk,
        "threshold": threshold
    })

    state["drift_history"].append({
        "time": event.get("timestamp"),
        "drift": drift
    })

    return {"status": "ok"}


# ---------------- GOVERNANCE INGEST ----------------

@app.post("/ingest_governance")
def ingest_governance(data: dict):

    ssi = float(data.get("ssi", 0))
    threshold = float(data.get("threshold", 150))
    trust = float(data.get("trust", 0.7))
    profile = data.get("profile", "precision")

    state["ssi_history"].append(ssi)
    state["threshold_history"].append(threshold)
    state["profile_history"].append(profile)

    ip = data.get("ip")
    if ip:
        state["trust_scores"][ip] = trust

    return {"status": "ok"}


# ---------------- DASHBOARD DATA ----------------

@app.get("/stats")
def stats():
    avg_risk = (
        state["risk_sum"] / state["total_flows"]
        if state["total_flows"] > 0 else 0
    )

    return {
        "total_flows": state["total_flows"],
        "total_blocks": state["total_blocks"],
        "drift": round(state["drift"], 4),
        "avg_risk": round(avg_risk, 2)
    }


@app.get("/risk-trend")
def risk_trend():
    return list(state["risk_history"])


@app.get("/drift-trend")
def drift_trend():
    return list(state["drift_history"])


@app.get("/attacks")
def attacks():
    return dict(state["attack_counts"])


@app.get("/blocked")
def get_blocked():
    return state["blocked_ips"]


@app.post("/unblock")
def unblock(data: dict):
    ip = data.get("ip")
    if ip in state["blocked_ips"]:
        del state["blocked_ips"][ip]
    return {"status": "unblocked"}


@app.get("/logs")
def logs():
    return state["logs"][-100:]


@app.get("/governance")
def get_governance():

    current_profile = (
        state["profile_history"][-1]
        if state["profile_history"]
        else "precision"
    )

    current_ssi = (
        state["ssi_history"][-1]
        if state["ssi_history"]
        else 0
    )

    current_threshold = (
        state["threshold_history"][-1]
        if state["threshold_history"]
        else 150
    )

    avg_trust = (
        sum(state["trust_scores"].values()) / len(state["trust_scores"])
        if state["trust_scores"] else 0.7
    )

    trust_distribution = [
        {"ip": ip, "trust": score}
        for ip, score in state["trust_scores"].items()
    ]

    return {
        "profile": current_profile,
        "ssi": round(current_ssi, 4),
        "dynamic_threshold": round(current_threshold, 2),
        "avg_trust": round(avg_trust, 3),
        "trust_distribution": trust_distribution
    }
