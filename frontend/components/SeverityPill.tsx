export default function SeverityPill({ severity }: { severity: string }) {
  const map: Record<string, string> = {
    High: "bg-danger/20 text-danger",
    Medium: "bg-warn/20 text-warn",
    Low: "bg-accent2/20 text-accent2",
    None: "bg-slate-600/20 text-slate-300",
  };
  return <span className={`pill ${map[severity] || map.None}`}>{severity}</span>;
}
