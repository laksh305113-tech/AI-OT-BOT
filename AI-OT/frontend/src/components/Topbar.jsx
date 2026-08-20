import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext.jsx';

export default function Topbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const initials = user?.display_name?.split(' ').map((part) => part[0]).slice(0, 2).join('') || 'OT';
  const handleLogout = () => { logout(); navigate('/login'); };
  return <header className="topbar"><div><p className="breadcrumb">OPERATING THEATRE / <span>OT-01</span></p><h2>Command Center</h2></div><div className="topbar-actions"><button className="icon-button" aria-label="Notifications">♢<span className="notification-badge">2</span></button><div className="profile"><span className="avatar">{initials}</span><div><strong>{user?.display_name}</strong><small>{user?.role?.replace('_', ' ')}</small></div><button className="logout-button" onClick={handleLogout}>Logout</button></div></div></header>;
}
