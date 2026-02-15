from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state = {
    "total_flows": 0,
    "total_blocks": 0,
    "drift": 0.0,
    "risk_sum": 0.0,
    "logs": [],
    "risk_history": [],
    "attack_counts": defaultdict(int),
    "blocked_ips": {}
}


@app.post("/ingest")
def ingest(event: dict):

    state["total_flows"] += 1
    risk = float(event.get("risk", 0))
    state["risk_sum"] += risk
    state["drift"] = event.get("drift", 0)

    if event.get("action") == "BLOCKED":
        state["total_blocks"] += 1

    level = event.get("level", "LOW")
    state["attack_counts"][level] += 1

    state["logs"].append(event)
    if len(state["logs"]) > 500:
        state["logs"].pop(0)

    state["risk_history"].append({
        "time": event.get("timestamp"),
        "risk": risk
    })
    if len(state["risk_history"]) > 200:
        state["risk_history"].pop(0)

    return {"status": "ok"}


@app.post("/block")
def block_ip(data: dict):
    ip = data["ip"]
    timestamp = data["timestamp"]
    state["blocked_ips"][ip] = timestamp
    return {"status": "blocked"}


@app.post("/unblock")
def unblock_ip(data: dict):
    ip = data["ip"]
    if ip in state["blocked_ips"]:
        del state["blocked_ips"][ip]
    return {"status": "unblocked"}


@app.get("/stats")
def stats():
    avg_risk = 0
    if state["total_flows"] > 0:
        avg_risk = state["risk_sum"] / state["total_flows"]

    return {
        "total_flows": state["total_flows"],
        "total_blocks": state["total_blocks"],
        "drift": round(state["drift"], 4),
        "avg_risk": round(avg_risk, 2)
    }


@app.get("/risk-trend")
def risk_trend():
    return list(state["risk_history"])


@app.get("/attacks")
def attacks():
    return dict(state["attack_counts"])


@app.get("/blocked")
def get_blocked():
    return state["blocked_ips"]


@app.get("/logs")
def logs():
    return state["logs"][-50:]
