import Card from '../components/Card.jsx';
import StatusPill from '../components/StatusPill.jsx';

const vitals = [['Heart Rate', '72', 'bpm'], ['SpO2', '98', '%'], ['Blood Pressure', '118/76', 'mmHg'], ['Respiratory Rate', '16', '/min'], ['Temperature', '36.8', '°C']];
const devices = [['OT Light', 'Online'], ['Camera', 'Standby'], ['Display', 'Online'], ['Operating Table', 'Ready'], ['Robot', 'Standby']];
const timeline = [['08:30', 'OT prepared', 'Room systems passed simulation check'], ['08:42', 'Team briefing', 'Pre-procedure workflow recorded'], ['09:00', 'Session scheduled', 'Awaiting synthetic patient selection']];

export default function Dashboard() {
  return <><div className="dashboard-intro"><div><p className="section-kicker">LIVE OVERVIEW</p><h1>Good morning, Dr. Sharma</h1><p>OT-01 is prepared and awaiting the next simulated session.</p></div><div className="simulation-chip">● Simulation environment</div></div><div className="dashboard-grid">
    <Card title="Current OT Session" className="session-card" action={<StatusPill>Ready</StatusPill>}><div className="session-data"><div><span>Patient</span><strong>No patient selected</strong></div><div><span>Procedure</span><strong>No active procedure</strong></div><div><span>Operating theatre</span><strong>OT-01</strong></div></div><div className="session-footer"><span className="status-dot" /> Systems ready for simulated workflow</div></Card>
    <Card title="Alerts" className="alerts-card" action={<button className="text-button">View all</button>}><div className="alert info"><span>i</span><div><strong>Simulation data active</strong><p>All displayed patient and device values are placeholders.</p></div></div><div className="alert warning"><span>!</span><div><strong>Camera in standby</strong><p>Camera simulation is ready when a session begins.</p></div></div></Card>
    <Card title="Patient Monitor" className="monitor-card" action={<span className="muted-label">SIMULATED VALUES</span>}><div className="vitals-grid">{vitals.map(([name, value, unit]) => <div className="vital" key={name}><span>{name}</span><strong>{value}<small>{unit}</small></strong><em>● Stable</em></div>)}</div></Card>
    <Card title="Device Status" className="devices-card" action={<StatusPill>5 connected</StatusPill>}><div className="device-list">{devices.map(([name, state]) => <div className="device" key={name}><span className="device-icon">◈</span><strong>{name}</strong><StatusPill tone={state === 'Online' || state === 'Ready' ? 'ready' : 'standby'}>{state}</StatusPill></div>)}</div></Card>
    <Card title="AI Assistant" className="assistant-card" action={<span className="assistant-orb">✦</span>}><p className="assistant-copy">Choose a simulated workflow assistant action.</p><div className="quick-actions">{['Patient Summary', 'Medical History', 'Show Imaging', 'Start Monitoring', 'Camera', 'Robot Status'].map(action => <button key={action}>{action}</button>)}</div></Card>
    <Card title="Surgical Timeline" className="timeline-card" action={<button className="text-button">Full timeline</button>}><ol className="timeline">{timeline.map(([time, title, detail]) => <li key={time}><time>{time}</time><span className="timeline-node" /><div><strong>{title}</strong><p>{detail}</p></div></li>)}</ol></Card>
  </div></>;
}
