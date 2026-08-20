import { useEffect, useMemo, useState } from 'react';
import { getPatients } from '../api/patientService.js';
import { askAiAssistant } from '../api/aiService.js';

const quickActions = [
  'Summarize this patient.',
  'What allergies does this patient have?',
  'What medications is the patient taking?',
  'What previous surgeries are recorded?',
  'Show the patient\'s latest imaging.',
];

export default function AIChatPage() {
  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState('');
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: 'I can summarize available patient information and answer record-based questions. I do not diagnose or prescribe treatment.',
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const { data } = await getPatients({ archived: 'false' });
        setPatients(data);
        if (data.length > 0) {
          setSelectedPatientId(String(data[0].id));
        }
      } catch (requestError) {
        setError(requestError.response?.data?.detail || 'Unable to load patient records.');
      }
    })();
  }, []);

  const selectedPatient = useMemo(
    () => patients.find((patient) => String(patient.id) === String(selectedPatientId)) || null,
    [patients, selectedPatientId],
  );

  const handleAsk = async (promptText = question) => {
    const trimmed = (promptText || '').trim();
    if (!trimmed) {
      setError('Please enter a question before sending.');
      return;
    }

    setError('');
    setLoading(true);
    setMessages((current) => [...current, { sender: 'user', text: trimmed }]);

    try {
      const { data } = await askAiAssistant({
        patientId: selectedPatient ? selectedPatient.id : null,
        question: trimmed,
      });
      setMessages((current) => [...current, { sender: 'assistant', text: data.answer }]);
      setQuestion('');
    } catch (requestError) {
      const detail = requestError.response?.data?.detail || 'The assistant could not answer that request.';
      setMessages((current) => [...current, { sender: 'assistant', text: `Unable to answer: ${detail}` }]);
      setError('Unable to generate a response right now.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-chat-page">
      <div className="page-header">
        <div>
          <p className="section-kicker">AI assistant</p>
          <h1>Clinical support</h1>
        </div>
      </div>

      <div className="ai-chat-layout">
        <aside className="ai-context-panel">
          <h2>Current patient context</h2>
          <label>
            Patient
            <select value={selectedPatientId} onChange={(event) => setSelectedPatientId(event.target.value)}>
              {patients.length === 0 ? <option value="">No patients available</option> : patients.map((patient) => (
                <option key={patient.id} value={patient.id}>{patient.name} ({patient.patient_id})</option>
              ))}
            </select>
          </label>

          {selectedPatient ? (
            <div className="patient-context-card">
              <strong>{selectedPatient.name}</strong>
              <span>ID: {selectedPatient.patient_id}</span>
              <span>Age: {selectedPatient.age ?? '—'}</span>
              <span>Gender: {selectedPatient.gender || 'unknown'}</span>
              <span>Procedure: {selectedPatient.planned_procedure || 'No information is available in the patient\'s records.'}</span>
              <span>Surgeon: {selectedPatient.assigned_surgeon || 'No information is available in the patient\'s records.'}</span>
            </div>
          ) : (
            <div className="empty-state compact">No patient selected.</div>
          )}

          <div className="quick-actions-panel">
            <h3>Quick actions</h3>
            <div className="quick-button-grid">
              {quickActions.map((action) => (
                <button key={action} type="button" className="quick-action-button" onClick={() => handleAsk(action)} disabled={loading}>
                  {action}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <section className="ai-chat-panel">
          <div className="chat-window" aria-live="polite">
            {messages.map((message, index) => (
              <div key={`${message.sender}-${index}`} className={`chat-bubble ${message.sender}`}>
                <div className="bubble-label">{message.sender === 'assistant' ? 'AI assistant' : 'You'}</div>
                <p>{message.text}</p>
              </div>
            ))}
            {loading && <div className="chat-bubble assistant loading-bubble"><div className="bubble-label">AI assistant</div><p>Thinking…</p></div>}
          </div>

          {error && <div className="status-banner error">{error}</div>}

          <div className="chat-composer">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              rows="3"
              placeholder="Ask about allergies, medications, prior surgeries, or procedure details..."
            />
            <div className="composer-actions">
              <span className="ai-disclaimer">AI responses are for informational assistance only and are not a substitute for professional clinical judgment.</span>
              <button type="button" className="primary-button" onClick={() => handleAsk()} disabled={loading}>
                {loading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
