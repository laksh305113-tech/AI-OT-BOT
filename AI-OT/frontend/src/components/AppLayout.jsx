import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';
import Topbar from './Topbar.jsx';

export default function AppLayout() {
  return <div className="command-center"><Sidebar /><div className="workspace"><Topbar /><main className="page-content"><Outlet /></main></div></div>;
}
