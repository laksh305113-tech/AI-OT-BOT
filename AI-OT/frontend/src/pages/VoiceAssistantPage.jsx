import { useEffect, useMemo, useRef, useState } from 'react';
import { sendVoiceCommand } from '../api/voiceService.js';

const quickCommands = [
  'Show patient history.',
  'Show latest X-ray.',
  'Start monitoring.',
  'Show camera 2.',
  'Zoom camera 2 to 2x.',
  'Increase OT light intensity to 80 percent.',
  'Show robot status.',
];

export default function VoiceAssistantPage() {
  const [transcript, setTranscript] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setStatus('Speech recognition is not supported in this browser. Text input remains available.');
      return undefined;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    recognition.onresult = (event) => {
      const finalText = Array.from(event.results)
        .map((entry) => entry[0]?.transcript || '')
        .join(' ')
        .trim();
      if (finalText) setTranscript(finalText);
    };
    recognition.onerror = () => {
      setStatus('Speech recognition encountered an error. Please use text input instead.');
    };
    recognition.onend = () => {
      setStatus('Voice capture ended.');
    };
    recognitionRef.current = recognition;
    return () => recognition.stop();
  }, []);

  const handleSend = async (textOverride) => {
    const commandText = (textOverride ?? transcript ?? '').trim();
    if (!commandText) {
      setError('Please enter or say a command first.');
      return;
    }

    setLoading(true);
    setError('');
    setStatus('Processing command...');

    try {
      const { data } = await sendVoiceCommand(commandText);
      setResult({
        status: data.status,
        intent: data.intent,
        device: data.device,
        value: data.value,
        reason: data.reason,
        simulated_result: data.simulated_result,
      });
      setStatus('Command processed safely in simulation mode.');
      setTranscript('');
    } catch (requestError) {
      const detail = requestError.response?.data?.detail || 'Unable to process command.';
      setError(detail);
      setStatus('Command rejected.');
    } finally {
      setLoading(false);
    }
  };

  const micLabel = useMemo(() => (recognitionRef.current ? 'Start voice command' : 'Voice input unavailable'), []);

  return (
    <div className="voice-page">
      <div className="page-header">
        <div>
          <p className="section-kicker">Voice assistant</p>
          <h1>Speech-driven OT commands</h1>
        </div>
      </div>

      <div className="voice-layout">
        <section className="voice-panel">
          <label className="voice-label">
            Command input
            <textarea
              value={transcript}
              onChange={(event) => setTranscript(event.target.value)}
              rows="5"
              placeholder="Say or type a command such as: Show camera 2 or Increase OT light intensity to 80 percent."
            />
          </label>

          <div className="voice-actions">
            <button type="button" className="primary-button" onClick={() => handleSend()} disabled={loading}>
              {loading ? 'Processing...' : 'Send command'}
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                const recognition = recognitionRef.current;
                if (!recognition) {
                  setStatus('Speech recognition is unavailable in this browser.');
                  return;
                }
                try { recognition.start(); setStatus('Listening...'); } catch { setStatus('Listening...'); }
              }}
            >
              {micLabel}
            </button>
          </div>

          {error && <div className="status-banner error">{error}</div>}
          {status && <div className="status-banner success">{status}</div>}
        </section>

        <aside className="voice-panel">
          <h2>Quick commands</h2>
          <div className="quick-command-grid">
            {quickCommands.map((command) => (
              <button key={command} type="button" className="quick-action-button" onClick={() => { setTranscript(command); handleSend(command); }}>
                {command}
              </button>
            ))}
          </div>
        </aside>
      </div>

      {result && (
        <section className="voice-result-panel">
          <h2>Structured command result</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </section>
      )}
    </div>
  );
}
