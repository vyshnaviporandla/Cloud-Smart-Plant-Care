import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import {
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signOut,
} from "firebase/auth";
import { auth } from "./firebase";
import "./App.css";

const API_BASE = "https://cloud-smart-plant-care.onrender.com/api";
const DEVICE_ID = "PLANT-001";

function App() {
  // Firebase authentication
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  // Login form
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState("");

  // Dashboard state
  const [device, setDevice] = useState(null);
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);
  const [wateringHistory, setWateringHistory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const [thresholdInput, setThresholdInput] = useState("");
  const [updatingThreshold, setUpdatingThreshold] = useState(false);
  const [updatingAutoWater, setUpdatingAutoWater] = useState(false);

  // Watch Firebase login state
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setAuthLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Login
  const handleLogin = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      setLoginError("Please enter email and password.");
      return;
    }

    try {
      setLoginLoading(true);
      setLoginError("");

      await signInWithEmailAndPassword(
        auth,
        email,
        password
      );
    } catch (error) {
      console.error("Login error:", error);

      if (
        error.code === "auth/invalid-credential" ||
        error.code === "auth/invalid-login-credentials"
      ) {
        setLoginError("Invalid email or password.");
      } else if (error.code === "auth/user-not-found") {
        setLoginError("User account not found.");
      } else if (error.code === "auth/wrong-password") {
        setLoginError("Incorrect password.");
      } else if (error.code === "auth/too-many-requests") {
        setLoginError(
          "Too many login attempts. Please try again later."
        );
      } else {
        setLoginError("Unable to sign in. Please try again.");
      }
    } finally {
      setLoginLoading(false);
    }
  };

  // Logout
  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const loadData = async () => {
    try {
      const devicesResponse = await fetch(
        `${API_BASE}/devices`
      );

      const devices = await devicesResponse.json();

      if (devices.length > 0) {
        const currentDevice = devices[0];

        setDevice(currentDevice);

        setThresholdInput(
          String(currentDevice.moisture_threshold ?? 30)
        );

        const latestResponse = await fetch(
          `${API_BASE}/devices/${currentDevice.device_id}/latest`
        );

        const latestData = await latestResponse.json();
        setLatest(latestData);

        const historyResponse = await fetch(
          `${API_BASE}/devices/${currentDevice.device_id}/history`
        );

        const historyData = await historyResponse.json();

        const readings = Array.isArray(historyData)
          ? historyData
          : historyData.readings ||
            historyData.history ||
            [];

        setHistory(
          readings.slice(-30).map((reading) => ({
            time: new Date(
              reading.timestamp
            ).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit",
            }),
            moisture: Number(reading.soil_moisture),
          }))
        );

        const wateringResponse = await fetch(
          `${API_BASE}/devices/${currentDevice.device_id}/watering-history`
        );

        const wateringData = await wateringResponse.json();

        const wateringEvents = Array.isArray(wateringData)
          ? wateringData
          : wateringData.events ||
            wateringData.history ||
            [];

        setWateringHistory(wateringEvents);
      }

      const alertsResponse = await fetch(
        `${API_BASE}/alerts`
      );

      const alertsData = await alertsResponse.json();

      setAlerts(Array.isArray(alertsData) ? alertsData : []);
    } catch (error) {
      console.error("Dashboard error:", error);
      setMessage("Unable to connect to backend.");
    } finally {
      setLoading(false);
    }
  };

  // Load dashboard only after authentication
  useEffect(() => {
    if (!user) {
      return;
    }

    setLoading(true);

    loadData();

    const interval = setInterval(loadData, 5000);

    return () => clearInterval(interval);
  }, [user]);

  const manualWater = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/devices/${DEVICE_ID}/water`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage("Manual watering started.");

        await loadData();

        setTimeout(() => {
          setMessage("");
        }, 3000);
      } else {
        setMessage(
          data.message || "Unable to start watering."
        );
      }
    } catch (error) {
      setMessage("Backend connection failed.");
    }
  };

  const updateThreshold = async () => {
    const threshold = Number(thresholdInput);

    if (
      !Number.isFinite(threshold) ||
      threshold < 1 ||
      threshold > 99
    ) {
      setMessage(
        "Threshold must be between 1% and 99%."
      );
      return;
    }

    try {
      setUpdatingThreshold(true);

      const response = await fetch(
        `${API_BASE}/devices/${DEVICE_ID}/threshold`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            threshold: threshold,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage(
          `Moisture threshold updated to ${threshold}%.`
        );

        await loadData();

        setTimeout(() => {
          setMessage("");
        }, 3000);
      } else {
        setMessage(
          data.message || "Unable to update threshold."
        );
      }
    } catch (error) {
      console.error(error);
      setMessage("Backend connection failed.");
    } finally {
      setUpdatingThreshold(false);
    }
  };

  const toggleAutoWater = async () => {
    if (!device) {
      return;
    }

    try {
      setUpdatingAutoWater(true);

      const newStatus = !device.auto_water;

      const response = await fetch(
        `${API_BASE}/devices/${DEVICE_ID}/auto-water`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            enabled: newStatus,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage(
          newStatus
            ? "Automatic watering enabled."
            : "Automatic watering disabled."
        );

        await loadData();

        setTimeout(() => {
          setMessage("");
        }, 3000);
      } else {
        setMessage(
          data.message ||
            "Unable to update auto watering."
        );
      }
    } catch (error) {
      console.error(error);
      setMessage("Backend connection failed.");
    } finally {
      setUpdatingAutoWater(false);
    }
  };

  const acknowledgeAlert = async (alertId) => {
    try {
      const response = await fetch(
        `${API_BASE}/alerts/${alertId}/acknowledge`,
        {
          method: "PUT",
        }
      );

      if (response.ok) {
        setMessage("Alert acknowledged.");

        await loadData();

        setTimeout(() => {
          setMessage("");
        }, 2500);
      }
    } catch (error) {
      setMessage(
        "Unable to acknowledge alert."
      );
    }
  };

  // Firebase authentication loading screen
  if (authLoading) {
    return (
      <div className="loading-screen">
        <h2>🌱 Smart Plant Care</h2>
        <p>Checking authentication...</p>
      </div>
    );
  }

  // Login screen
  if (!user) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="login-icon">🌱</div>

          <h1>Smart Plant Care</h1>

          <p className="login-subtitle">
            Cloud-Connected Plant Monitoring
          </p>

          <form onSubmit={handleLogin}>
            <div className="login-field">
              <label>Email</label>

              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) =>
                  setEmail(e.target.value)
                }
                autoComplete="email"
              />
            </div>

            <div className="login-field">
              <label>Password</label>

              <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                autoComplete="current-password"
              />
            </div>

            {loginError && (
              <div className="login-error">
                {loginError}
              </div>
            )}

            <button
              type="submit"
              className="login-button"
              disabled={loginLoading}
            >
              {loginLoading
                ? "Signing in..."
                : "🔐 Sign In"}
            </button>
          </form>

          <div className="login-footer">
            <span className="status-dot"></span>
            Secure Firebase Authentication
          </div>
        </div>
      </div>
    );
  }

  // Dashboard loading
  if (loading) {
    return (
      <div className="loading-screen">
        <h2>🌱 Smart Plant Care</h2>
        <p>
          Connecting to plant monitoring system...
        </p>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>🌱 Smart Plant Care</h1>
          <p>
            Cloud-Connected Plant Monitoring &
            Automatic Watering
          </p>
        </div>

        <div className="header-right">
          <div className="connection">
            <span className="status-dot"></span>
            System Online
          </div>

          <div className="user-section">
            <span className="user-email">
              👤 {user.email}
            </span>

            <button
              className="logout-button"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="container">
        {message && (
          <div className="message">{message}</div>
        )}

        {device && (
          <section className="device-card">
            <div>
              <span className="label">ACTIVE DEVICE</span>

              <h2>{device.plant_name}</h2>

              <p>
                {device.plant_type} • {device.location}
              </p>
            </div>

            <div className="device-id">
              <span>Device ID</span>
              <strong>{device.device_id}</strong>
            </div>
          </section>
        )}

        <section className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon">💧</div>

            <span>Soil Moisture</span>

            <strong>
              {latest?.soil_moisture !== undefined
                ? `${Number(
                    latest.soil_moisture
                  ).toFixed(1)}%`
                : "--"}
            </strong>

            <small>
              Threshold:{" "}
              {device?.moisture_threshold ?? "--"}%
            </small>
          </div>

          <div className="metric-card">
            <div className="metric-icon">🌡️</div>

            <span>Temperature</span>

            <strong>
              {latest?.temperature !== undefined
                ? `${Number(
                    latest.temperature
                  ).toFixed(1)}°C`
                : "--"}
            </strong>

            <small>Live sensor reading</small>
          </div>

          <div className="metric-card">
            <div className="metric-icon">💦</div>

            <span>Humidity</span>

            <strong>
              {latest?.humidity !== undefined
                ? `${Number(
                    latest.humidity
                  ).toFixed(1)}%`
                : "--"}
            </strong>

            <small>Air humidity</small>
          </div>

          <div className="metric-card">
            <div className="metric-icon">☀️</div>

            <span>Light Level</span>

            <strong>
              {latest?.light_level !== undefined
                ? `${Number(
                    latest.light_level
                  ).toFixed(1)}%`
                : "--"}
            </strong>

            <small>Current light intensity</small>
          </div>
        </section>

        <section className="panel chart-panel">
          <div className="panel-header">
            <div>
              <h2>📈 Soil Moisture History</h2>

              <p className="panel-subtitle">
                Recent readings from the virtual IoT
                sensor
              </p>
            </div>

            <span className="chart-live">
              <span className="status-dot"></span>
              LIVE
            </span>
          </div>

          <div className="chart-container">
            {history.length > 0 ? (
              <ResponsiveContainer
                width="100%"
                height={320}
              >
                <LineChart data={history}>
                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 11 }}
                    interval="preserveStartEnd"
                  />

                  <YAxis
                    domain={[0, 100]}
                    tick={{ fontSize: 11 }}
                    tickFormatter={(value) =>
                      `${value}%`
                    }
                  />

                  <Tooltip
                    formatter={(value) => [
                      `${Number(value).toFixed(1)}%`,
                      "Moisture",
                    ]}
                  />

                  <ReferenceLine
                    y={
                      device?.moisture_threshold || 30
                    }
                    strokeDasharray="5 5"
                    label={{
                      value: "Threshold",
                      position: "insideTopRight",
                    }}
                  />

                  <Line
                    type="monotone"
                    dataKey="moisture"
                    strokeWidth={3}
                    dot={false}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-chart">
                <span>📊</span>
                <p>
                  Waiting for sensor history...
                </p>
              </div>
            )}
          </div>
        </section>

        <section className="control-grid">
          <div className="panel">
            <div className="panel-header">
              <h2>🚿 Watering System</h2>

              <span
                className={
                  device?.pump_status
                    ? "badge active"
                    : "badge inactive"
                }
              >
                {device?.pump_status
                  ? "PUMP ON"
                  : "PUMP OFF"}
              </span>
            </div>

            <div className="watering-status">
              <div className="pump-circle">
                {device?.pump_status
                  ? "💦"
                  : "🚿"}
              </div>

              <div>
                <h3>
                  {device?.pump_status
                    ? "Watering in progress"
                    : "Watering stopped"}
                </h3>

                <p>
                  Automatic watering is{" "}
                  <strong>
                    {device?.auto_water
                      ? "enabled"
                      : "disabled"}
                  </strong>
                  .
                </p>
              </div>
            </div>

            <button
              className="water-button"
              onClick={manualWater}
            >
              💧 Start Manual Watering
            </button>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>⚙️ Automation</h2>
            </div>

            <div className="automation-row">
              <span>Auto Watering</span>

              <button
                className={`toggle-button ${
                  device?.auto_water
                    ? "toggle-on"
                    : "toggle-off"
                }`}
                onClick={toggleAutoWater}
                disabled={updatingAutoWater}
              >
                <span className="toggle-circle"></span>

                {updatingAutoWater
                  ? "Updating..."
                  : device?.auto_water
                  ? "ON"
                  : "OFF"}
              </button>
            </div>

            <div className="threshold-control">
              <div className="threshold-header">
                <span>Moisture Threshold</span>

                <strong>
                  {device?.moisture_threshold ?? "--"}%
                </strong>
              </div>

              <div className="threshold-input-row">
                <input
                  type="number"
                  min="1"
                  max="99"
                  step="1"
                  value={thresholdInput}
                  onChange={(e) =>
                    setThresholdInput(
                      e.target.value
                    )
                  }
                />

                <span>%</span>

                <button
                  className="save-threshold-button"
                  onClick={updateThreshold}
                  disabled={updatingThreshold}
                >
                  {updatingThreshold
                    ? "Saving..."
                    : "Save"}
                </button>
              </div>

              <small>
                Automatic watering starts when soil
                moisture falls below this value.
              </small>
            </div>

            <div className="automation-row">
              <span>Device Status</span>

              <span className="badge active">
                ONLINE
              </span>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>💦 Watering History</h2>

              <p className="panel-subtitle">
                Record of automatic and manual
                watering events
              </p>
            </div>

            <span className="history-count">
              {wateringHistory.length} Events
            </span>
          </div>

          {wateringHistory.length === 0 ? (
            <div className="empty-state">
              <span>💧</span>
              <p>
                No watering events recorded yet.
              </p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Trigger</th>
                    <th>Before</th>
                    <th>After</th>
                    <th>Duration</th>
                  </tr>
                </thead>

                <tbody>
                  {wateringHistory
                    .slice(0, 10)
                    .map((event) => (
                      <tr key={event.id}>
                        <td>
                          {new Date(
                            event.timestamp
                          ).toLocaleString()}
                        </td>

                        <td>
                          <span
                            className={`trigger-badge ${String(
                              event.trigger_type
                            ).toLowerCase()}`}
                          >
                            {event.trigger_type}
                          </span>
                        </td>

                        <td>
                          {Number(
                            event.moisture_before
                          ).toFixed(1)}
                          %
                        </td>

                        <td>
                          {Number(
                            event.moisture_after
                          ).toFixed(1)}
                          %
                        </td>

                        <td>
                          {event.duration}s
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>🚨 Recent Alerts</h2>

            <span className="alert-count">
              {alerts.length}
            </span>
          </div>

          {alerts.length === 0 ? (
            <div className="empty-state">
              <span>✅</span>

              <p>No alerts available.</p>
            </div>
          ) : (
            <div className="alerts-list">
              {alerts.slice(0, 5).map((alert) => (
                <div
                  className="alert-item"
                  key={alert.id}
                >
                  <div>
                    <strong>
                      {alert.alert_type}
                    </strong>

                    <p>{alert.message}</p>
                  </div>

                  <div className="alert-actions">
                    <span
                      className={`alert-level ${String(
                        alert.level
                      ).toLowerCase()}`}
                    >
                      {alert.level}
                    </span>

                    {alert.status === "OPEN" && (
                      <button
                        className="ack-button"
                        onClick={() =>
                          acknowledgeAlert(
                            alert.id
                          )
                        }
                      >
                        Acknowledge
                      </button>
                    )}

                    {alert.status !== "OPEN" && (
                      <span className="acknowledged">
                        ✓ Acknowledged
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <footer>
          <p>
            Cloud Smart Plant Care • IoT + Cloud
            Computing Project
          </p>
        </footer>
      </main>
    </div>
  );
}

export default App;