import { NavLink } from 'react-router-dom';

const navigation = [
  ['/', 'Dashboard', '⌂'], ['/patients', 'Patients', '♙'], ['/ot-sessions', 'OT Sessions', '◷'], ['/ai-assistant', 'AI Assistant', '✦'], ['/voice-assistant', 'Voice Assistant', '◍'],
  ['/monitoring', 'Monitoring', '⌁'], ['/imaging', 'Medical Imaging', '◉'], ['/camera', 'Camera', '◫'], ['/ot-control', 'OT Control', '⌘'],
  ['/robot', 'Robotic Surgery', '◌'], ['/alerts', 'Alerts', '△'], ['/reports', 'Reports', '▤'], ['/audit-logs', 'Audit Logs', '≡'], ['/settings', 'Settings', '⚙'],
];

export default function Sidebar() {
  return <aside className="sidebar"><NavLink to="/" className="brand"><span className="brand-mark">A</span><span>AI-<b>OT</b></span></NavLink><p className="nav-label">Command center</p><nav aria-label="Main navigation">{navigation.map(([to, label, icon]) => <NavLink key={to} to={to} end={to === '/'} className="nav-item"><span className="nav-icon">{icon}</span><span>{label}</span></NavLink>)}</nav><div className="sidebar-footer"><span className="status-dot" /> Simulation mode</div></aside>;
}
