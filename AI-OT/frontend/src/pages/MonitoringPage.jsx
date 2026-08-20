import { useEffect, useMemo, useRef, useState } from 'react';

const sessionId = 'session-01';

const formatSummary = (value) => {
  if (typeof value === 'number') return value.toFixed(1);
  return value ?? '—';
};

export default function MonitoringPage() {
  const [status, setStatus] = useState('Monitoring Active');
  const [vitals, setVitals] = useState({
    heart_rate: { value: 72, unit: 'bpm' },
    spo2: { value: 98, unit: '%' },
    blood_pressure: { value: '118/76', unit: 'mmHg' },
    respiratory_rate: { value: 16, unit: '/min' },
    temperature: { value: 36.8, unit: '°C' },
    etco2: { value: 38, unit: 'mmHg' },
  });
  const [alerts, setAlerts] = useState([]);
  const [patientStatus, setPatientStatus] = useState('Stable');
  const [waveform, setWaveform] = useState(Array.from({ length: 45 }, (_, index) => Math.sin(index / 4) * 30 + 50));
  const [history, setHistory] = useState([]);
  const socketRef = useRef(null);

  useEffect(() => {
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.hostname}:8000/ws/monitoring/${sessionId}`;
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      setStatus('Monitoring Active');
    };

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      setStatus(payload.status || 'Monitoring Active');
      setVitals(payload.vitals || vitals);
      setAlerts(payload.alerts || []);
      setPatientStatus(payload.patient_status || 'Stable');
      setWaveform((current) => [...current.slice(-44), ...(payload.waveform?.ecg || [current[current.length - 1]])]);
      setHistory((current) => [{ ...payload, timestamp: payload.timestamp }, ...current].slice(0, 8));
    };

    socket.onerror = () => {
      setStatus('Monitoring Disconnected');
    };

    socket.onclose = () => {
      setStatus('Monitoring Disconnected');
    };

    return () => {
      socket.close();
    };
  }, []);

  const summaryCards = useMemo(() => [
    ['Heart Rate', `${formatSummary(vitals.heart_rate?.value)} ${vitals.heart_rate?.unit}`],
    ['SpO2', `${formatSummary(vitals.spo2?.value)} ${vitals.spo2?.unit}`],
    ['Blood Pressure', `${vitals.blood_pressure?.value} ${vitals.blood_pressure?.unit}`],
    ['Respiratory Rate', `${formatSummary(vitals.respiratory_rate?.value)} ${vitals.respiratory_rate?.unit}`],
    ['Temperature', `${formatSummary(vitals.temperature?.value)} ${vitals.temperature?.unit}`],
    ['EtCO2', `${formatSummary(vitals.etco2?.value)} ${vitals.etco2?.unit}`],
  ], [vitals]);

  return (
    <div className="monitoring-page">
      <div className="page-header">
        <div>
          <p className="section-kicker">Patient monitoring</p>
          <h1>Live monitoring dashboard</h1>
        </div>
        <div className={`monitor-status ${status.toLowerCase().replace(/\s+/g, '-')}`}>
          {status}
        </div>
      </div>

      <div className="monitoring-grid">
        <section className="monitor-panel">
          <div className="panel-header-row">
            <h2>Vital cards</h2>
            <span className="muted-label">SIMULATED DATA</span>
          </div>
          <div className="monitor-vital-grid">
            {summaryCards.map(([label, value]) => (
              <div key={label} className="monitor-vital-card">
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="monitor-panel alert-panel">
          <div className="panel-header-row">
            <h2>Alerts</h2>
            <span className="muted-label">SIMULATED ALERT</span>
          </div>
          {alerts.length === 0 ? (
            <div className="empty-state compact">No simulated alerts triggered.</div>
          ) : (
            alerts.map((alert, index) => (
              <div key={`${alert.type}-${index}`} className="monitor-alert">
                <span className="alert-badge">SIMULATED ALERT</span>
                <strong>{alert.type}</strong>
                <p>{alert.message}</p>
              </div>
            ))
          )}
        </section>

        <section className="monitor-panel wide-panel">
          <div className="panel-header-row">
            <h2>ECG-style waveform</h2>
            <span className="muted-label">Patient status: {patientStatus}</span>
          </div>
          <div className="waveform-wrap">
            <svg viewBox="0 0 600 200" className="ecg-svg" preserveAspectRatio="none">
              {waveform.map((point, index) => {
                const x = (index / (waveform.length - 1)) * 600;
                const y = 100 - point * 0.9;
                return <circle key={`${x}-${index}`} cx={x} cy={y} r={index === waveform.length - 1 ? 2.5 : 1.2} fill="#64f0d2" />;
              })}
            </svg>
          </div>
        </section>

        <section className="monitor-panel wide-panel">
          <div className="panel-header-row">
            <h2>Historical trends</h2>
            <span className="muted-label">Last 8 samples</span>
          </div>
          <div className="trend-list">
            {history.length === 0 ? (
              <div className="empty-state compact">Waiting for live data...</div>
            ) : (
              history.map((entry, index) => (
                <div key={`${entry.timestamp}-${index}`} className="trend-row">
                  <span>{new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
                  <strong>{entry.vitals?.heart_rate?.value ?? '—'} bpm</strong>
                  <em>{entry.vitals?.spo2?.value ?? '—'}% SpO2</em>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
