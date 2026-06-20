export default function ScoreCard({
  label,
  score,
  sub,
}: {
  label: string;
  score: number;
  sub?: string;
}) {
  const color =
    score >= 80 ? "text-accent2" : score >= 50 ? "text-warn" : "text-danger";

  return (
    <div className="card flex flex-col items-center justify-center text-center">
      <span className="label">{label}</span>
      <span className={`text-4xl font-bold mt-1 ${color}`}>{score}</span>
      <span className="text-xs text-slate-500">/ 100</span>
      {sub && <span className="text-sm mt-1 text-slate-300">{sub}</span>}
    </div>
  );
}
