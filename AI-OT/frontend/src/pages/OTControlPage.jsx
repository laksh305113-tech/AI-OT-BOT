import { useEffect, useMemo, useState } from 'react';
import { getOtDevices, sendOtDeviceCommand } from '../api/otControlService.js';

const deviceLabels = {
  surgical_light: 'OT Surgical Light',
  camera: 'Camera',
  display: 'OT Display',
  operating_table: 'Operating Table',
};

const formatValue = (value) => {
  if (typeof value === 'boolean') return value ? 'On' : 'Off';
  if (typeof value === 'object') return JSON.stringify(value);
  return value;
};

export default function OTControlPage() {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [command, setCommand] = useState('intensity');
  const [payload, setPayload] = useState('80');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const { data } = await getOtDevices();
        setDevices(data.devices || []);
        if ((data.devices || []).length > 0) {
          setSelectedDevice(data.devices[0].id);
        }
      } catch (requestError) {
        setError(requestError.response?.data?.detail || 'Unable to load OT devices.');
      }
    })();
  }, []);

  const selected = useMemo(
    () => devices.find((device) => device.id === selectedDevice) || devices[0] || null,
    [devices, selectedDevice],
  );

  const handleExecute = async () => {
    if (!selected) return;
    const parsed = (() => {
      if (command === 'position') {
        try {
          return { position: JSON.parse(payload) };
        } catch {
          return { position: { x: 50, y: 0 } };
        }
      }
      if (['power', 'fullscreen', 'manual_override', 'emergency_stop'].includes(command)) {
        return { [command]: payload === 'true' || payload === '1' };
      }
      if (['intensity', 'brightness', 'zoom', 'focus', 'height', 'pan', 'tilt'].includes(command)) {
        return { [command]: Number(payload) };
      }
      if (command === 'input_source') {
        return { input_source: payload };
      }
      return { [command]: payload };
    })();

    setLoading(true);
    setError('');
    setStatus('');

    try {
      const { data } = await sendOtDeviceCommand(selected.id, command, parsed);
      setStatus(`Command accepted: ${data.command_name} -> ${data.status}`);
      const refreshed = await getOtDevices();
      setDevices(refreshed.data.devices || []);
    } catch (requestError) {
      const detail = requestError.response?.data?.detail || 'Command rejected.';
      setError(typeof detail === 'string' ? detail : JSON.stringify(detail));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ot-control-page">
      <div className="page-header">
        <div>
          <p className="section-kicker">OT control center</p>
          <h1>Simulated theatre controls</h1>
        </div>
        <div className="monitor-status monitoring-active">SIMULATION ACTIVE</div>
      </div>

      <div className="monitoring-grid">
        <section className="monitor-panel">
          <div className="panel-header-row">
            <h2>Connected devices</h2>
            <span className="muted-label">SIMULATED</span>
          </div>
          <div className="device-list">
            {(devices || []).map((device) => (
              <button
                key={device.id}
                type="button"
                className={`device-card ${selected?.id === device.id ? 'selected' : ''}`}
                onClick={() => setSelectedDevice(device.id)}
              >
                <strong>{device.display_name}</strong>
                <span>{deviceLabels[device.device_type] || device.device_type}</span>
                <small>{device.allowed_commands.join(', ')}</small>
              </button>
            ))}
          </div>
        </section>

        <section className="monitor-panel">
          <div className="panel-header-row">
            <h2>Device control</h2>
            <span className="muted-label">Safety gating enabled</span>
          </div>
          {selected && (
            <div className="control-panel">
              <div className="field-label">
                <label>
                  Selected device
                  <select value={selectedDevice} onChange={(event) => setSelectedDevice(event.target.value)}>
                    {devices.map((device) => <option key={device.id} value={device.id}>{device.display_name}</option>)}
                  </select>
                </label>
              </div>
              <div className="field-label">
                <label>
                  Command
                  <select value={command} onChange={(event) => setCommand(event.target.value)}>
                    {(selected.allowed_commands || []).map((item) => <option key={item} value={item}>{item}</option>)}
                  </select>
                </label>
              </div>
              <div className="field-label">
                <label>
                  Payload
                  <input value={payload} onChange={(event) => setPayload(event.target.value)} placeholder={'e.g. 80 or {"x": 30, "y": 40}'} />
                </label>
              </div>
              <div className="toolbar-group">
                <button type="button" className="primary-button" onClick={handleExecute} disabled={loading}>
                  {loading ? 'Sending...' : 'Execute command'}
                </button>
                <button type="button" className="secondary-button" onClick={() => setPayload('')}>Clear payload</button>
              </div>
              {status && <div className="status-banner success">{status}</div>}
              {error && <div className="status-banner error">{error}</div>}
            </div>
          )}
        </section>

        <section className="monitor-panel wide-panel">
          <div className="panel-header-row">
            <h2>Device state</h2>
            <span className="muted-label">Live simulated state</span>
          </div>
          {selected ? (
            <div className="device-state-grid">
              {Object.entries(selected.state || {}).map(([key, value]) => (
                <div key={key} className="monitor-vital-card">
                  <span>{key}</span>
                  <strong>{formatValue(value)}</strong>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state compact">No device selected.</div>
          )}
        </section>

        <section className="monitor-panel wide-panel">
          <div className="panel-header-row">
            <h2>Safety controls</h2>
            <span className="muted-label">Emergency stop</span>
          </div>
          <div className="safety-actions">
            <button type="button" className="primary-button danger" onClick={() => sendOtDeviceCommand(selected.id, 'emergency_stop', { emergency_stop: true })}>Emergency Stop</button>
            <button type="button" className="secondary-button" onClick={() => sendOtDeviceCommand(selected.id, 'manual_override', { manual_override: true })}>Manual Override</button>
          </div>
          <p className="muted-copy">When Emergency Stop is active, all simulated device commands are disabled until reset by an authorized user.</p>
        </section>
      </div>
    </div>
  );
}
