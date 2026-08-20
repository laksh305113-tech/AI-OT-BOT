import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { archivePatient, getPatients } from '../api/patientService.js';

const priorityFilterOptions = ['all', 'routine', 'priority', 'urgent', 'emergency'];

function formatDate(dateValue) {
  if (!dateValue) return '—';
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

export default function PatientsPage() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [priority, setPriority] = useState('all');
  const [gender, setGender] = useState('all');
  const [showArchived, setShowArchived] = useState(false);
  const [notice, setNotice] = useState('');

  const fetchPatients = async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await getPatients({
        search,
        priority: priority === 'all' ? '' : priority,
        gender: gender === 'all' ? '' : gender,
        archived: showArchived ? 'true' : 'false',
      });
      setPatients(data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to load patient records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [search, priority, gender, showArchived]);

  const patientCount = useMemo(() => patients.length, [patients]);

  const handleArchive = async (patientId) => {
    try {
      await archivePatient(patientId);
      setNotice('Patient archived successfully.');
      fetchPatients();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to archive this patient.');
    }
  };

  return (
    <div className="patients-page">
      <div className="page-header">
        <div>
          <p className="section-kicker">Patient management</p>
          <h1>Patients</h1>
        </div>
        <Link to="/patients/new" className="primary-button">Add patient</Link>
      </div>

      {notice && <div className="status-banner success">{notice}</div>}
      {error && <div className="status-banner error">{error}</div>}

      <div className="patient-toolbar">
        <input
          className="search-input"
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search patient ID, name, surgeon, or procedure"
        />
        <select value={priority} onChange={(event) => setPriority(event.target.value)}>
          {priorityFilterOptions.map((option) => (
            <option key={option} value={option}>{option === 'all' ? 'All priorities' : option}</option>
          ))}
        </select>
        <select value={gender} onChange={(event) => setGender(event.target.value)}>
          <option value="all">All genders</option>
          <option value="female">Female</option>
          <option value="male">Male</option>
          <option value="other">Other</option>
          <option value="unknown">Unknown</option>
        </select>
        <label className="checkbox-inline">
          <input type="checkbox" checked={showArchived} onChange={(event) => setShowArchived(event.target.checked)} />
          Show archived
        </label>
      </div>

      <div className="table-card">
        {loading ? (
          <div className="empty-state">Loading patient records...</div>
        ) : patientCount === 0 ? (
          <div className="empty-state">No patient records match the current filters.</div>
        ) : (
          <div className="table-wrap">
            <table className="patient-table">
              <thead>
                <tr>
                  <th>Patient ID</th>
                  <th>Name</th>
                  <th>Age</th>
                  <th>Gender</th>
                  <th>Blood Group</th>
                  <th>Assigned Surgeon</th>
                  <th>OT Number</th>
                  <th>Scheduled Date</th>
                  <th>Priority</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((patient) => (
                  <tr key={patient.id}>
                    <td>{patient.patient_id}</td>
                    <td><Link to={`/patients/${patient.id}`} className="table-link">{patient.name}</Link></td>
                    <td>{patient.age ?? '—'}</td>
                    <td>{patient.gender || '—'}</td>
                    <td>{patient.blood_group || '—'}</td>
                    <td>{patient.assigned_surgeon || 'Unassigned'}</td>
                    <td>{patient.ot_number || '—'}</td>
                    <td>{formatDate(patient.scheduled_date)}</td>
                    <td><span className={`priority-pill ${patient.priority || 'routine'}`}>{patient.priority || 'routine'}</span></td>
                    <td className="actions-cell">
                      <Link to={`/patients/${patient.id}`} className="text-button">View</Link>
                      <Link to={`/patients/${patient.id}/edit`} className="text-button">Edit</Link>
                      <button type="button" className="text-button danger" onClick={() => handleArchive(patient.id)}>Archive</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
