export default function Card({ title, children, className = '', action }) {
  return <section className={`card ${className}`}><div className="card-heading"><h3>{title}</h3>{action}</div>{children}</section>;
}
