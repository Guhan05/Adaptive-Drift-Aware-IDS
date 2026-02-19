# 🛡️ Adaptive Drift-Aware Autonomous Intrusion Detection System (IDS)

A real-time **Autonomous Adaptive Intrusion Detection and Prevention System** that combines:

✅ Drift-aware adaptive risk fusion engine  
✅ Stability State Index (SSI) governance controller  
✅ Autonomous posture switching (Precision / Balanced / Aggressive)  
✅ Trust-based adaptive stability modulation  
✅ Real-time / Replay / Simulation detection modes  
✅ Enterprise dashboard with governance telemetry  
✅ Automatic firewall enforcement (Windows Firewall integration)  

The system dynamically detects and prevents cyber attacks while autonomously adjusting its defense posture based on environmental stability.

---

# 🚀 Features

✔ Drift-aware adaptive detection engine  
✔ Stability State Index (SSI) governance controller  
✔ Dynamic threshold adaptation  
✔ Autonomous defense posture switching  
✔ Trust-based risk stabilization  
✔ Real-time packet detection capability  
✔ Replay mode for deterministic testing  
✔ Enterprise governance dashboard  
✔ Firewall auto-blocking and unblock control  
✔ Scrollable live event logs  
✔ Attack distribution visualization  
✔ Git version control ready  
✔ Patent-ready adaptive architecture  

---

# 📂 Project Structure

IDS_Project
├── data/
├── src/
│ ├── dashboard_backend/
│ │ └── main.py
│ │
│ ├── dashboard_frontend/
│ │ ├── src/
│ │ │ ├── pages/
│ │ │ │ └── AdaptivePanel.js
│ │ │ ├── App.js
│ │ │ └── App.css
│ │
│ ├── realtime/
│ │ └── realtime_main.py
│ │
│ ├── models/
│ ├── training/
│ ├── utils/
│ └── results/
│
├── README.md
├── requirements.txt
└── .gitignore


---

# ⚙️ Installation

## 1️⃣ Clone repository

```bash
git clone https://github.com/Guhan05/Adaptive-Drift-Aware-IDS.git
cd Adaptive-Drift-Aware-IDS
2️⃣ Install dependencies
Option A (recommended)

pip install -r requirements.txt
Option B (manual)

pip install fastapi uvicorn scapy requests numpy pandas
Frontend:

cd src/dashboard_frontend
npm install
🧠 Step-by-Step Execution Guide
Follow EXACT order below 👇

🔹 STEP 1 — Start Backend Server
This launches the telemetry and governance backend.

Command:

python -m uvicorn src.dashboard_backend.main:app --reload --port 9000
Backend runs at:

http://localhost:9000
🔹 STEP 2 — Run Detection Engine
Supports:

Replay mode (recommended for testing)

Live mode (real packet capture)

Simulation mode (research evaluation)

Replay mode:

python -m src.realtime.realtime_main --mode replay
Live mode:

python -m src.realtime.realtime_main --mode live
Simulation mode:

python -m src.realtime.realtime_main
Terminal Output Example:

[LIVE] 192.168.1.12 → 10.0.0.5 | Risk=182.4 | BLOCKED
Firewall enforcement automatically blocks malicious IPs.

🔹 STEP 3 — Start Dashboard
Command:

cd src/dashboard_frontend
npm start
Open browser:

http://localhost:3000
📊 Dashboard Shows
✔ Total flows analyzed
✔ Total attacks blocked
✔ Drift score trend
✔ Dynamic risk threshold behavior
✔ Autonomous posture switching
✔ Attack distribution chart
✔ Blocked IP management with unblock option
✔ Scrollable live detection logs
✔ Governance telemetry panel

🧠 Adaptive Governance Working
1️⃣ Drift Detection
Detects environmental instability in network traffic.

Drift ↑ → System instability ↑
2️⃣ Stability State Index (SSI)
Combines:

Risk variance

Drift variance

Mode switching frequency

Trust stability

SSI ∈ [0,1]

Higher SSI → stronger defensive posture

3️⃣ Dynamic Threshold Adaptation
Instead of static threshold:

threshold = base + gain × SSI
This allows adaptive blocking sensitivity.

4️⃣ Autonomous Posture Switching
System automatically switches between:

Precision Mode (low false positives)

Balanced Mode (moderate sensitivity)

Aggressive Mode (high security posture)

Based on SSI stability level.

5️⃣ Autonomous Enforcement
When risk exceeds dynamic threshold:

✔ IP automatically blocked via firewall
✔ Event logged in backend
✔ Dashboard updated in real-time
✔ Administrator can manually unblock

📈 Results
Metric	Value
Detection Architecture	Drift-Aware Autonomous IDS
Control Mechanism	SSI Governance
Modes Supported	Live / Replay / Simulation
Dashboard	Enterprise Telemetry Panel
Enforcement	Automatic Firewall Blocking
Adaptation	Autonomous Threshold Control
🧪 Example Workflow
Terminal 1 — Backend:

python -m uvicorn src.dashboard_backend.main:app --reload --port 9000
Terminal 2 — Detection Engine:

python -m src.realtime.realtime_main --mode replay
Terminal 3 — Dashboard:

cd src/dashboard_frontend
npm start
Open:

http://localhost:3000
🛠 Technologies Used
Python
FastAPI
React.js
Scapy
Windows Firewall (netsh)
NumPy
Pandas
Git
Uvicorn

🧹 Git Setup
git init
git add .
git commit -m "Adaptive drift-aware autonomous IDS implementation"
git push origin main
🔮 Future Improvements
Real statistical drift detection (ADWIN / KL divergence)
Machine learning risk prediction models
Cloud deployment (Docker / Kubernetes)
Distributed multi-node IDS
Automated alert notification system
Enterprise SIEM integration

👨‍💻 Author
Guhan M
Adaptive Drift-Aware Autonomous Intrusion Detection System
Patent-Oriented Research Project

⚡ Quick Start (TL;DR)
pip install fastapi uvicorn scapy requests numpy pandas
python -m uvicorn src.dashboard_backend.main:app --reload --port 9000
python -m src.realtime.realtime_main --mode replay
cd src/dashboard_frontend
npm install
npm start
Open:

http://localhost:3000
📜 License
Educational / Research use only

Patent Pending

