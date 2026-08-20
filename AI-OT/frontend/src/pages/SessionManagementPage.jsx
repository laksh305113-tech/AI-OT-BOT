import { useEffect, useMemo, useState } from 'react';
import { createSession, endSession, getSession, getSessions, pauseSession, resumeSession, recordSessionEvent } from '../api/sessionService.js';

const defaultSession = {
  patient_id: 1,
  surgeon: 'Dr. Sam',
  procedure: 'Synthetic procedure',
  ot_number: 'OT-01',
  status: 'active',
};

const sampleTimeline = [
  ['09:00', 'Session started', 'Theatre session opened and readiness checks completed.'],
  ['09:02', 'Monitoring started', 'Patient monitoring stream was activated.'],
  ['09:04', 'Medical image opened', 'Image review workflow initiated.'],
  ['09:07', 'Camera zoom changed', 'Camera zoom adjusted to 2x.'],
  ['09:10', 'Alert generated', 'Simulated monitoring alert created.'],
  ['09:12', 'Alert acknowledged', 'Alert was reviewed and accepted.'],
];

export default function SessionManagementPage() {
  const [sessions, setSessions] = useState([]);
  const [selectedId, setSelectedId] = useState('');
  const [form, setForm] = useState(defaultSession);
  const [timeline, setTimeline] = useState(sampleTimeline);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const selectedSession = useMemo(
    () => sessions.find((session) => String(session.id) === String(selectedId)) || null,
    [sessions, selectedId],
  );

  const loadSessions = async () => {
    try {
      const { data } = await getSessions();
      setSessions(data.sessions || []);
      if (!selectedId && (data.sessions || []).length > 0) {
        setSelectedId(String(data.sessions[0].id));
      }
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to load sessions.');
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (!selectedId) return undefined;
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.hostname}:8000/ws/sessions/${selectedId}`;
    const socket = new WebSocket(wsUrl);
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.timeline && payload.timeline.length > 0) {
        const next = payload.timeline.map((entry) => [new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), entry.message, entry.kind || 'event']);
        setTimeline(next.length > 0 ? next : sampleTimeline);
      }
    };
    return () => socket.close();
  }, [selectedId]);

  const refreshSession = async (id) => {
    if (!id) return;
    try {
      const { data } = await getSession(id);
      setSessions((current) => {
        const next = current.filter((session) => String(session.id) !== String(data.id));
        return [...next, data];
      });
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to refresh the session.');
    }
  };

  const handleCreate = async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await createSession(form);
      setSelectedId(String(data.id));
      setStatus('Session started');
      await refreshSession(data.id);
      await loadSessions();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to start the session.');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action) => {
    if (!selectedId) return;
    const handlers = {
      pause: pauseSession,
      resume: resumeSession,
      end: endSession,
    };
    const actionFn = handlers[action];
    if (!actionFn) return;
    try {
      await actionFn(selectedId);
      await refreshSession(selectedId);
      await recordSessionEvent(selectedId, action, { action, timestamp: new Date().toISOString() });
      setStatus(`Session ${action}d`);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || `Unable to ${action} the session.`);
    }
  };

  return (
    <div className="session-page">
      <div className="page-header">
        <div>
          <p className="section-kicker">Surgical session management</p>
          <h1>Live theatre sessions</h1>
        </div>
        <div className="monitor-status monitoring-active">SIMULATED SESSIONS</div>
      </div>

      <div className="monitoring-grid">
        <section className="monitor-panel">
          <div className="panel-header-row">
            <h2>Session controls</h2>
            <span className="muted-label">Session lifecycle</span>
          </div>
          <div className="control-panel">
            <label className="field-label">
              Patient ID
              <input type="number" value={form.patient_id} onChange={(event) => setForm({ ...form, patient_id: Number(event.target.value) })} />
            </label>
            <label className="field-label">
              Surgeon
              <input value={form.surgeon} onChange={(event) => setForm({ ...form, surgeon: event.target.value })} />
            </label>
            <label className="field-label">
              Procedure
              <input value={form.procedure} onChange={(event) => setForm({ ...form, procedure: event.target.value })} />
            </label>
            <label className="field-label">
              OT number
              <input value={form.ot_number} onChange={(event) => setForm({ ...form, ot_number: event.target.value })} />
            </label>
            <div className="safety-actions">
              <button type="button" className="primary-button" onClick={handleCreate} disabled={loading}>{loading ? 'Starting...' : 'Start Session'}</button>
              <button type="button" className="secondary-button" onClick={() => handleAction('pause')}>Pause Session</button>
              <button type="button" className="secondary-button" onClick={() => handleAction('resume')}>Resume Session</button>
              <button type="button" className="secondary-button" onClick={() => handleAction('end')}>End Session</button>
            </div>
            {status && <div className="status-banner success">{status}</div>}
            {error && <div className="status-banner error">{error}</div>}
          </div>
        </section>

        <section className="monitor-panel">
          <div className="panel-header-row">
            <h2>Session list</h2>
            <span className="muted-label">Live sessions</span>
          </div>
          <div className="device-list">
            {sessions.length === 0 ? (
              <div className="empty-state compact">No sessions yet.</div>
            ) : (
              sessions.map((session) => (
                <button key={session.id} type="button" className={`device-card ${selectedId === String(session.id) ? 'selected' : ''}`} onClick={() => setSelectedId(String(session.id))}>
                  <strong>{session.session_id || `Session-${session.id}`}</strong>
                  <span>{session.procedure}</span>
                  <small>{session.surgeon} • {session.ot_number} • {session.status}</small>
                </button>
              ))
            )}
          </div>
        </section>

        <section className="monitor-panel wide-panel">
          <div className="panel-header-row">
            <h2>Live surgical timeline</h2>
            <span className="muted-label">Realtime event stream</span>
          </div>
          <div className="trend-list">
            {timeline.map(([time, title, detail], index) => (
              <div key={`${time}-${index}`} className="trend-row">
                <span>{time}</span>
                <strong>{title}</strong>
                <em>{detail}</em>
              </div>
            ))}
          </div>
        </section>

        <section className="monitor-panel wide-panel">
          <div className="panel-header-row">
            <h2>Selected session</h2>
            <span className="muted-label">Current overview</span>
          </div>
          {selectedSession ? (
            <div className="device-state-grid">
              <div className="monitor-vital-card"><span>Session ID</span><strong>{selectedSession.session_id}</strong></div>
              <div className="monitor-vital-card"><span>Patient</span><strong>{selectedSession.patient_name || selectedSession.patient_id}</strong></div>
              <div className="monitor-vital-card"><span>Surgeon</span><strong>{selectedSession.surgeon}</strong></div>
              <div className="monitor-vital-card"><span>Procedure</span><strong>{selectedSession.procedure}</strong></div>
              <div className="monitor-vital-card"><span>OT number</span><strong>{selectedSession.ot_number}</strong></div>
              <div className="monitor-vital-card"><span>Status</span><strong>{selectedSession.status}</strong></div>
            </div>
          ) : (
            <div className="empty-state compact">Select a session to view details.</div>
          )}
        </section>
      </div>
    </div>
  );
}
