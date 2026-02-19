import React, { useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
} from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  BarChart,
  Bar,
} from "recharts";
import AdaptivePanel from "./pages/AdaptivePanel";
import "./App.css";

const COLORS = ["#00C49F", "#FFBB28", "#FF4444"];

function Overview({ darkMode }) {
  const [stats, setStats] = useState({});
  const [logs, setLogs] = useState([]);
  const [riskTrend, setRiskTrend] = useState([]);
  const [attacks, setAttacks] = useState({});
  const [blocked, setBlocked] = useState({});
  const [filterIP, setFilterIP] = useState("");
  const [filterLevel, setFilterLevel] = useState("");
  const [filterAction, setFilterAction] = useState("");

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:9000/stats")
        .then((res) => res.json())
        .then(setStats);

      fetch("http://localhost:9000/logs")
        .then((res) => res.json())
        .then(setLogs);

      fetch("http://localhost:9000/risk-trend")
        .then((res) => res.json())
        .then(setRiskTrend);

      fetch("http://localhost:9000/attacks")
        .then((res) => res.json())
        .then(setAttacks);

      fetch("http://localhost:9000/blocked")
        .then((res) => res.json())
        .then(setBlocked);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const filteredLogs = logs.filter((log) => {
    return (
      (!filterIP ||
        log.src_ip?.includes(filterIP) ||
        log.dst_ip?.includes(filterIP)) &&
      (!filterLevel || log.level === filterLevel) &&
      (!filterAction || log.action === filterAction)
    );
  });

  const pieData = Object.keys(attacks).map((key) => ({
    name: key,
    value: attacks[key],
  }));

  return (
    <div className="page">
      <h1>Adaptive IDS Enterprise Dashboard</h1>

      {/* Stats */}
      <div className="stats-grid">
        <div className="card">Total Flows: {stats.total_flows}</div>
        <div className="card">Total Blocks: {stats.total_blocks}</div>
        <div className="card">Drift: {stats.drift}</div>
        <div className="card">Avg Risk: {stats.avg_risk}</div>
      </div>

      {/* Charts */}
      <div className="chart-grid">
        <div className="card">
          <h3>Risk Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={riskTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="risk" stroke="#00C49F" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Attack Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieData} dataKey="value" outerRadius={100}>
                {pieData.map((entry, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Blocked IP */}
      <div className="card">
        <h3>Blocked IP List</h3>
        <ul>
          {Object.keys(blocked).length === 0 && <li>No blocked IPs</li>}
          {Object.entries(blocked).map(([ip, time]) => (
            <li key={ip}>
              {ip} — {time}
            </li>
          ))}
        </ul>
      </div>

      {/* Logs */}
      <div className="card">
        <h3>Live Event Logs</h3>

        <div className="filters">
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
        </div>

        <div className="log-table">
          <table>
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
              {filteredLogs.map((log, i) => (
                <tr key={i}>
                  <td>{log.timestamp}</td>
                  <td>{log.src_ip}</td>
                  <td>{log.dst_ip}</td>
                  <td>{log.risk}</td>
                  <td>{log.level}</td>
                  <td>{log.mode}</td>
                  <td>{log.drift}</td>
                  <td>{log.action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [darkMode, setDarkMode] = useState(true);

  return (
    <Router>
      <div className={darkMode ? "dark" : "light"}>
        <nav className="navbar">
          <div>
            <Link to="/">Overview</Link>
            <Link to="/adaptive">Adaptive Panel</Link>
          </div>

          <button onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? "Light" : "Dark"} mode
          </button>
        </nav>

        <Routes>
          <Route path="/" element={<Overview darkMode={darkMode} />} />
          <Route
            path="/adaptive"
            element={<AdaptivePanel darkMode={darkMode} />}
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
