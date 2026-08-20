export default function StatusPill({ children, tone = 'ready' }) {
  return <span className={`status-pill ${tone}`}><span className="status-dot" />{children}</span>;
}
