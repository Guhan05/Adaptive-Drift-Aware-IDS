import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const COLORS = ["#00C49F", "#FFBB28", "#FF4444"];

function App() {
  const [stats, setStats] = useState({});
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [riskTrend, setRiskTrend] = useState([]);
  const [attacks, setAttacks] = useState({});
  const [blocked, setBlocked] = useState({});
  const [alert, setAlert] = useState(null);

  const [filterIP, setFilterIP] = useState("");
  const [filterLevel, setFilterLevel] = useState("");
  const [filterAction, setFilterAction] = useState("");

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:9000/stats")
        .then(res => res.json())
        .then(data => setStats(data));

      fetch("http://localhost:9000/logs")
        .then(res => res.json())
        .then(data => {
          const reversed = data.reverse();
          setLogs(reversed);
          setFilteredLogs(reversed);

          const high = reversed.find(log => log.alert === true);
          if (high) setAlert(high);
        });

      fetch("http://localhost:9000/risk-trend")
        .then(res => res.json())
        .then(data => setRiskTrend(data));

      fetch("http://localhost:9000/attacks")
        .then(res => res.json())
        .then(data => setAttacks(data));

      fetch("http://localhost:9000/blocked")
        .then(res => res.json())
        .then(data => setBlocked(data));

    }, 2000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let temp = logs;

    if (filterIP) {
      temp = temp.filter(log =>
        log.src_ip.includes(filterIP) ||
        log.dst_ip.includes(filterIP)
      );
    }

    if (filterLevel) {
      temp = temp.filter(log => log.level === filterLevel);
    }

    if (filterAction) {
      temp = temp.filter(log => log.action === filterAction);
    }

    setFilteredLogs(temp);
  }, [filterIP, filterLevel, filterAction, logs]);

  const pieData = Object.keys(attacks).map(key => ({
    name: key,
    value: attacks[key]
  }));

  const downloadCSV = () => {
    if (filteredLogs.length === 0) return;
    const headers = Object.keys(filteredLogs[0]).join(",");
    const rows = filteredLogs.map(obj =>
      Object.values(obj).join(",")
    );
    const csv = [headers, ...rows].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ids_logs.csv";
    a.click();
  };

  const unblockIP = (ip) => {
    fetch("http://localhost:9000/unblock", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ip })
    });
  };

  return (
    <div style={{ padding: "20px" }}>

      <h1>Adaptive IDS Security Dashboard</h1>

      {alert && (
        <div style={{
          backgroundColor: "red",
          color: "white",
          padding: "10px",
          marginBottom: "15px"
        }}>
          🚨 HIGH ALERT from {alert.src_ip}
        </div>
      )}

      <div style={{ display: "flex", gap: "20px", marginBottom: "20px" }}>
        <div>Total Flows: {stats.total_flows}</div>
        <div>Total Blocks: {stats.total_blocks}</div>
        <div>Drift: {stats.drift}</div>
        <div>Avg Risk: {stats.avg_risk}</div>
      </div>

      <div style={{ display: "flex", gap: "40px" }}>
        <div>
          <h3>Risk Trend</h3>
          <LineChart width={500} height={250} data={riskTrend}>
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="risk" stroke="#FF4444" />
          </LineChart>
        </div>

        <div>
          <h3>Attack Distribution</h3>
          <PieChart width={300} height={250}>
            <Pie data={pieData} dataKey="value" outerRadius={80} label>
              {pieData.map((entry, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </div>
      </div>

      <h2>Filters</h2>
      <div style={{ marginBottom: "10px" }}>
        <input
          placeholder="Filter by IP"
          value={filterIP}
          onChange={(e) => setFilterIP(e.target.value)}
        />

        <select onChange={(e) => setFilterLevel(e.target.value)}>
          <option value="">Level</option>
          <option>LOW</option>
          <option>MEDIUM</option>
          <option>HIGH</option>
        </select>

        <select onChange={(e) => setFilterAction(e.target.value)}>
          <option value="">Action</option>
          <option>MONITOR</option>
          <option>BLOCKED</option>
        </select>

        <button onClick={downloadCSV}>Download CSV</button>
      </div>

      <h2>Blocked IP Management</h2>
      <table border="1">
        <thead>
          <tr>
            <th>IP</th>
            <th>Blocked At</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(blocked).map(([ip, time]) => (
            <tr key={ip}>
              <td>{ip}</td>
              <td>{time}</td>
              <td>
                <button onClick={() => unblockIP(ip)}>Unblock</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Live Event Logs</h2>
      <div style={{ maxHeight: "400px", overflowY: "scroll", border: "1px solid gray" }}>
        <table border="1">
          <thead>
            <tr>
              <th>Time</th>
              <th>Source</th>
              <th>Destination</th>
              <th>Risk</th>
              <th>Level</th>
              <th>Mode</th>
              <th>Drift</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.map((log, index) => (
              <tr key={index}>
                <td>{log.timestamp}</td>
                <td>{log.src_ip}</td>
                <td>{log.dst_ip}</td>
                <td>{log.risk}</td>
                <td>{log.level}</td>
                <td>{log.mode}</td>
                <td>{log.drift}</td>
                <td style={{ color: log.level === "HIGH" ? "red" : "green" }}>
                  {log.action}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}

export default App;
