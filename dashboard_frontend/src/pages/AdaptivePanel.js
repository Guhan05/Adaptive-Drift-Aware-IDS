import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

function AdaptivePanel() {
  const [gov, setGov] = useState({});
  const [riskTrend, setRiskTrend] = useState([]);
  const [driftTrend, setDriftTrend] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:9000/governance")
        .then((res) => res.json())
        .then(setGov);

      fetch("http://localhost:9000/risk-trend")
        .then((res) => res.json())
        .then(setRiskTrend);

      fetch("http://localhost:9000/drift-trend")
        .then((res) => res.json())
        .then(setDriftTrend);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="page">
      <h1>Adaptive Governance Research Panel</h1>

      <div className="stats-grid">
        <div className="card">
          Current Profile: {gov.profile}
        </div>
        <div className="card">
          Dynamic Threshold: {gov.dynamic_threshold}
        </div>
        <div className="card">SSI: {gov.ssi}</div>
        <div className="card">Avg Trust: {gov.avg_trust}</div>
      </div>

      <div className="chart-grid">
        <div className="card">
          <h3>Risk vs Threshold</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={riskTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line dataKey="risk" stroke="#00C49F" />
              <Line dataKey="threshold" stroke="#FF4444" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Drift Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={driftTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line dataKey="drift" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}

export default AdaptivePanel;
