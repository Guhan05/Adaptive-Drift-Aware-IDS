# 🔐 Hybrid Intrusion Detection System (IDS)

A real‑time **Hybrid Intrusion Detection System** that combines:

✅ Artificial Neural Network (Deep Learning)  
✅ Fuzzy Logic Decision System  
✅ Real‑time / Simulated Traffic Detection  
✅ Live Dashboard (Streamlit)  
✅ CICIDS2017 Dataset  

The system classifies network traffic into:

- Normal Traffic
- High Risk Attack

---

# 🚀 Features

✔ ANN based classifier  
✔ Fuzzy risk decision layer  
✔ Real‑time predictions  
✔ Streamlit dashboard  
✔ Logging system  
✔ 98%+ accuracy  
✔ Modular architecture  
✔ Git version control ready  

---

# 📂 Project Structure

IDS_Project
├───data
└───src
    ├───dashboard
    ├───models
    ├───realtime
    │   └───__pycache__
    ├───results
    ├───training
    │   └───__pycache__
    ├───utils
    └───__pycache__



---

# ⚙️ Installation

## 1️⃣ Clone repository

```bash
git clone <your-repo-url>
cd IDS_Project
2️⃣ Install dependencies
Option A (recommended)
pip install -r requirements.txt
Option B (manual)
pip install tensorflow pandas scikit-learn streamlit numpy
🧠 Step‑by‑Step Execution Guide
Follow EXACT order below 👇

🔹 STEP 1 — Train the Model
This trains ANN and saves model file.

Command
python -m src.training.train
Output
src/models/ids_model.h5
🔹 STEP 2 — Run Real‑Time Detection
Simulates live traffic and makes predictions.

Command
python -m src.realtime.realtime_main
Terminal Output Example
Decision: Normal Traffic
Decision: High Risk Attack
Decision: Normal Traffic
Logs saved to
src/results/logs.csv
🔹 STEP 3 — Start Dashboard
Launch web UI.

Command
python -m streamlit run src/dashboard/app.py
Open browser
http://localhost:8501
📊 Dashboard Shows
✔ Packets analyzed
✔ Attacks detected
✔ Live decision graph
✔ Recent predictions table

🧠 Hybrid Model Working
1️⃣ ANN
Learns traffic patterns and outputs probability:

0 → Normal
1 → Attack
2️⃣ Fuzzy Logic
Converts probability → risk level:

Low → Normal Traffic
High → High Risk Attack
Improves reliability and reduces false alarms.

📈 Results
Metric	Value
Accuracy	~98%
Model	ANN + Fuzzy
Dataset	CICIDS2017
🧪 Example Workflow
Terminal 1
python -m src.realtime.realtime_main
Terminal 2
python -m streamlit run src/dashboard/app.py
Now watch live detection on dashboard.

🛠 Technologies Used
Python

TensorFlow / Keras

Pandas

Scikit‑learn

Streamlit

Git

🧹 Git Setup
git init
git add .
git commit -m "Initial commit"
git push
🔮 Future Improvements
Live packet capture (Scapy)

Sound alerts 🚨

Email alerts

Attack heatmap

Web deployment

👨‍💻 Author
Guhan M
Hybrid Intrusion Detection System

⚡ Quick Start (TL;DR)
pip install tensorflow pandas scikit-learn streamlit
python -m src.training.train
python -m src.realtime.realtime_main
python -m streamlit run src/dashboard/app.py
📜 License
Educational / Academic use only

