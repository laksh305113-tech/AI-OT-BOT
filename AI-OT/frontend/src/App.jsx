import { Route, Routes } from 'react-router-dom';
import AppLayout from './components/AppLayout.jsx';
import Dashboard from './pages/Dashboard.jsx';
import PlaceholderPage from './pages/PlaceholderPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import PatientsPage from './pages/PatientsPage.jsx';
import PatientFormPage from './pages/PatientFormPage.jsx';
import PatientDetailsPage from './pages/PatientDetailsPage.jsx';
import AIChatPage from './pages/AIChatPage.jsx';
import VoiceAssistantPage from './pages/VoiceAssistantPage.jsx';
import MedicalImagingPage from './pages/MedicalImagingPage.jsx';
import MonitoringPage from './pages/MonitoringPage.jsx';
import OTControlPage from './pages/OTControlPage.jsx';
import SessionManagementPage from './pages/SessionManagementPage.jsx';
import ProtectedRoute from './auth/ProtectedRoute.jsx';

const pages = {
  '/patients': ['Patients', 'Synthetic patient records will appear here.'],
  '/ot-sessions': ['OT Sessions', 'Operating theatre sessions will appear here.'],
  '/ai-assistant': ['AI Assistant', 'Simulated clinical-assistance tools will appear here.'],
  '/monitoring': ['Monitoring', 'Simulated monitoring information will appear here.'],
  '/imaging': ['Medical Imaging', 'Simulated imaging studies will appear here.'],
  '/camera': ['Camera', 'Simulated OT camera feeds will appear here.'],
  '/ot-control': ['OT Control', 'Simulated OT device controls will appear here.'],
  '/robot': ['Robotic Surgery', 'Simulated robotic-surgery controls will appear here.'],
  '/alerts': ['Alerts', 'System alerts and notifications will appear here.'],
  '/reports': ['Reports', 'Prototype reports will appear here.'],
  '/audit-logs': ['Audit Logs', 'Prototype activity logs will appear here.'],
  '/settings': ['Settings', 'Application settings will appear here.'],
};

function App() {
  return <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route element={<ProtectedRoute />}>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/patients" element={<PatientsPage />} />
        <Route path="/patients/new" element={<PatientFormPage mode="create" />} />
        <Route path="/patients/:id" element={<PatientDetailsPage />} />
        <Route path="/patients/:id/edit" element={<PatientFormPage mode="edit" />} />
        <Route path="/ai-assistant" element={<AIChatPage />} />
        <Route path="/voice-assistant" element={<VoiceAssistantPage />} />
        <Route path="/imaging" element={<MedicalImagingPage />} />
        <Route path="/monitoring" element={<MonitoringPage />} />
        <Route path="/ot-control" element={<OTControlPage />} />
        <Route path="/sessions" element={<SessionManagementPage />} />
        {Object.entries(pages).filter(([path]) => path !== '/patients' && path !== '/ai-assistant' && path !== '/voice-assistant' && path !== '/imaging' && path !== '/monitoring' && path !== '/ot-control' && path !== '/sessions').map(([path, [title, description]]) => <Route key={path} path={path} element={<PlaceholderPage title={title} description={description} />} />)}
      </Route>
    </Route>
  </Routes>;
}

export default App;
