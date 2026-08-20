import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { createPatient, getPatient, updatePatient } from '../api/patientService.js';

const blankForm = {
  patient_id: '',
  name: '',
  date_of_birth: '',
  gender: 'female',
  blood_group: '',
  phone: '',
  emergency_contact: '',
  medical_conditions: '',
  allergies: '',
  current_medications: '',
  previous_surgeries: '',
  previous_anesthesia_complications: '',
  family_history: '',
  additional_medical_notes: '',
  planned_procedure: '',
  assigned_surgeon: '',
  ot_number: '',
  scheduled_date: '',
  priority: 'routine',
  preoperative_notes: '',
  is_archived: false,
};

function toInputDate(dateValue) {
  if (!dateValue) return '';
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) return '';
  return date.toISOString().slice(0, 10);
}

export default function PatientFormPage({ mode = 'create' }) {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = mode === 'edit' || Boolean(id);
  const [form, setForm] = useState(blankForm);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!isEdit) return;
    (async () => {
      try {
        const { data } = await getPatient(id);
        setForm({
          ...blankForm,
          ...data,
          date_of_birth: toInputDate(data.date_of_birth),
          scheduled_date: toInputDate(data.scheduled_date),
        });
      } catch (requestError) {
        setError(requestError.response?.data?.detail || 'Unable to load patient details.');
      }
    })();
  }, [id, isEdit]);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setForm((current) => ({
      ...current,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const validateForm = () => {
    if (!form.patient_id.trim()) return 'Patient ID is required.';
    if (!form.name.trim()) return 'Patient name is required.';
    if (!form.date_of_birth) return 'Date of birth is required.';
    if (!form.gender.trim()) return 'Gender is required.';
    if (form.phone && form.phone.length < 7) return 'Phone number must be at least 7 digits.';
    return '';
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const payload = {
        ...form,
        name: form.name.trim(),
        patient_id: form.patient_id.trim(),
      };

      if (isEdit) {
        await updatePatient(id, payload);
      } else {
        await createPatient(payload);
      }
      navigate('/patients');
    } catch (requestError) {
      const detail = requestError.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Unable to save patient information.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="patient-form-page">
      <div className="page-header form-header">
        <div>
          <p className="section-kicker">Patient registration</p>
          <h1>{isEdit ? 'Edit patient' : 'Register patient'}</h1>
        </div>
        <Link to="/patients" className="secondary-button">Back to patients</Link>
      </div>

      {error && <div className="status-banner error">{error}</div>}

      <form className="patient-form" onSubmit={handleSubmit}>
        <div className="form-panel">
          <div className="panel-heading">
            <div>
              <p className="muted-label">Patient details</p>
              <h2>Primary information</h2>
            </div>
          </div>

          <div className="field-grid">
            <label>
              Patient ID
              <input name="patient_id" value={form.patient_id} onChange={handleChange} required />
            </label>
            <label>
              Name
              <input name="name" value={form.name} onChange={handleChange} required />
            </label>
            <label>
              Date of Birth
              <input type="date" name="date_of_birth" value={form.date_of_birth} onChange={handleChange} required />
            </label>
            <label>
              Gender
              <select name="gender" value={form.gender} onChange={handleChange}>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="other">Other</option>
                <option value="unknown">Unknown</option>
              </select>
            </label>
            <label>
              Blood Group
              <input name="blood_group" value={form.blood_group} onChange={handleChange} placeholder="A+, O-, etc." />
            </label>
            <label>
              Phone
              <input name="phone" value={form.phone} onChange={handleChange} placeholder="+1 555 123 4567" />
            </label>
            <label>
              Emergency Contact
              <input name="emergency_contact" value={form.emergency_contact} onChange={handleChange} />
            </label>
            <label>
              Assigned Surgeon
              <input name="assigned_surgeon" value={form.assigned_surgeon} onChange={handleChange} />
            </label>
            <label>
              OT Number
              <input name="ot_number" value={form.ot_number} onChange={handleChange} />
            </label>
            <label>
              Scheduled Date
              <input type="date" name="scheduled_date" value={form.scheduled_date} onChange={handleChange} />
            </label>
            <label>
              Priority
              <select name="priority" value={form.priority} onChange={handleChange}>
                <option value="routine">Routine</option>
                <option value="priority">Priority</option>
                <option value="urgent">Urgent</option>
                <option value="emergency">Emergency</option>
              </select>
            </label>
            <label className="checkbox-field">
              <input type="checkbox" name="is_archived" checked={form.is_archived} onChange={handleChange} />
              Archived
            </label>
          </div>
        </div>

        <div className="form-panel">
          <div className="panel-heading">
            <div>
              <p className="muted-label">Clinical overview</p>
              <h2>Medical information</h2>
            </div>
          </div>
          <div className="field-grid wide-fields">
            <label className="field-span-2">
              Medical conditions
              <textarea name="medical_conditions" value={form.medical_conditions} onChange={handleChange} rows="3" />
            </label>
            <label className="field-span-2">
              Allergies
              <textarea name="allergies" value={form.allergies} onChange={handleChange} rows="3" />
            </label>
            <label className="field-span-2">
              Current medications
              <textarea name="current_medications" value={form.current_medications} onChange={handleChange} rows="3" />
            </label>
            <label className="field-span-2">
              Previous surgeries
              <textarea name="previous_surgeries" value={form.previous_surgeries} onChange={handleChange} rows="3" />
            </label>
            <label className="field-span-2">
              Previous anesthesia complications
              <textarea name="previous_anesthesia_complications" value={form.previous_anesthesia_complications} onChange={handleChange} rows="3" />
            </label>
            <label className="field-span-2">
              Family history
              <textarea name="family_history" value={form.family_history} onChange={handleChange} rows="3" />
            </label>
            <label className="field-span-2">
              Additional medical notes
              <textarea name="additional_medical_notes" value={form.additional_medical_notes} onChange={handleChange} rows="3" />
            </label>
          </div>
        </div>

        <div className="form-panel">
          <div className="panel-heading">
            <div>
              <p className="muted-label">Operating plan</p>
              <h2>Surgical information</h2>
            </div>
          </div>
          <div className="field-grid wide-fields">
            <label className="field-span-2">
              Planned procedure
              <textarea name="planned_procedure" value={form.planned_procedure} onChange={handleChange} rows="3" />
            </label>
            <label className="field-span-2">
              Pre-operative notes
              <textarea name="preoperative_notes" value={form.preoperative_notes} onChange={handleChange} rows="3" />
            </label>
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="primary-button" disabled={isSubmitting}>{isSubmitting ? 'Saving...' : isEdit ? 'Update patient' : 'Create patient'}</button>
          <Link to="/patients" className="secondary-button">Cancel</Link>
        </div>
      </form>
    </div>
  );
}
