import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getPatient } from '../api/patientService.js';

const tabList = [
  'overview',
  'medical-history',
  'allergies',
  'medications',
  'previous-surgeries',
  'lab-reports',
  'medical-imaging',
  'surgical-history',
];

function formatDate(dateValue) {
  if (!dateValue) return '—';
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

function renderList(items, emptyText) {
  if (!items || items.length === 0) {
    return <p className="empty-state compact">{emptyText}</p>;
  }

  return (
    <ul className="detail-list">
      {items.map((item, index) => (
        <li key={index}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
      ))}
    </ul>
  );
}

export default function PatientDetailsPage() {
  const { id } = useParams();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError('');
      try {
        const { data } = await getPatient(id);
        setPatient(data);
      } catch (requestError) {
        setError(requestError.response?.data?.detail || 'Unable to load patient details.');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const overviewFields = useMemo(() => [
    ['Patient ID', patient?.patient_id],
    ['Name', patient?.name],
    ['Age', patient?.age],
    ['Date of birth', formatDate(patient?.date_of_birth)],
    ['Gender', patient?.gender],
    ['Blood group', patient?.blood_group],
    ['Phone', patient?.phone],
    ['Emergency contact', patient?.emergency_contact],
    ['Assigned surgeon', patient?.assigned_surgeon],
    ['OT number', patient?.ot_number],
    ['Scheduled date', formatDate(patient?.scheduled_date)],
    ['Priority', patient?.priority],
  ], [patient]);

  if (loading) return <div className="empty-state">Loading patient details...</div>;
  if (error) return <div className="status-banner error">{error}</div>;
  if (!patient) return <div className="empty-state">No patient record found.</div>;

  return (
    <div className="patient-details-page">
      <div className="page-header detail-header">
        <div>
          <p className="section-kicker">Patient details</p>
          <h1>{patient.name}</h1>
        </div>
        <div className="detail-actions">
          <Link to="/patients" className="secondary-button">Back</Link>
          <Link to={`/patients/${patient.id}/edit`} className="primary-button">Edit patient</Link>
        </div>
      </div>

      <div className="detail-summary-card">
        <div className="summary-main">
          <span className="summary-label">Patient ID</span>
          <strong>{patient.patient_id}</strong>
        </div>
        <div className="summary-main">
          <span className="summary-label">Procedure</span>
          <strong>{patient.planned_procedure || 'Not assigned'}</strong>
        </div>
        <div className="summary-main">
          <span className="summary-label">Priority</span>
          <strong className={`priority-pill ${patient.priority || 'routine'}`}>{patient.priority || 'routine'}</strong>
        </div>
      </div>

      <div className="tab-list" role="tablist">
        {tabList.map((tab) => (
          <button
            key={tab}
            type="button"
            className={activeTab === tab ? 'tab-button active' : 'tab-button'}
            onClick={() => setActiveTab(tab)}
          >
            {tab.replace(/-/g, ' ')}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="detail-section">
          <div className="overview-grid">
            {overviewFields.map(([label, value]) => (
              <div key={label} className="stat-block">
                <span>{label}</span>
                <strong>{value ?? '—'}</strong>
              </div>
            ))}
          </div>
          <div className="notes-block">
            <h3>Pre-operative notes</h3>
            <p>{patient.preoperative_notes || 'No pre-operative notes recorded.'}</p>
          </div>
        </div>
      )}

      {activeTab === 'medical-history' && (
        <div className="detail-section">
          <h3>Medical history</h3>
          <p>{patient.medical_history?.summary || patient.medical_conditions || 'No medical history recorded.'}</p>
          <h3>Family history</h3>
          <p>{patient.family_history || 'No family history recorded.'}</p>
          <h3>Previous anesthesia complications</h3>
          <p>{patient.previous_anesthesia_complications || 'No anesthesia complications recorded.'}</p>
          <h3>Additional medical notes</h3>
          <p>{patient.additional_medical_notes || 'No extra notes recorded.'}</p>
        </div>
      )}

      {activeTab === 'allergies' && (
        <div className="detail-section">
          <h3>Allergies</h3>
          <p>{patient.allergies || 'No allergies recorded.'}</p>
        </div>
      )}

      {activeTab === 'medications' && (
        <div className="detail-section">
          <h3>Current medications</h3>
          <p>{patient.current_medications || 'No medications recorded.'}</p>
        </div>
      )}

      {activeTab === 'previous-surgeries' && (
        <div className="detail-section">
          <h3>Previous surgeries</h3>
          <p>{patient.previous_surgeries || 'No previous surgeries recorded.'}</p>
        </div>
      )}

      {activeTab === 'lab-reports' && (
        <div className="detail-section">
          <h3>Lab reports</h3>
          {renderList(patient.lab_reports?.map((lab) => `${lab.report_type}: ${lab.result_summary}`), 'No lab reports available.')}
        </div>
      )}

      {activeTab === 'medical-imaging' && (
        <div className="detail-section">
          <h3>Medical imaging</h3>
          {renderList(patient.medical_images?.map((image) => `${image.modality} — ${image.description || image.storage_reference}`), 'No medical imaging available.')}
        </div>
      )}

      {activeTab === 'surgical-history' && (
        <div className="detail-section">
          <h3>Surgical history</h3>
          {renderList(patient.surgical_sessions?.map((session) => `${session.ot_room} — ${session.procedure_name} (${session.status})`), 'No surgical history available.')}
        </div>
      )}
    </div>
  );
}
