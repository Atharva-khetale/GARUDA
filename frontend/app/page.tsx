import Link from "next/link";

export default function Home() {
  return (
    <div className="py-16 text-center">
      <h1 className="text-4xl font-bold mb-4">
        GARUDA<span className="text-accent">.</span>
      </h1>
      <p className="text-slate-400 max-w-xl mx-auto mb-8">
        Genetic Analysis, Research, Understanding, Design &amp; Assessment.
        Evaluate engineered DNA constructs — sequence integrity, mutations,
        restriction sites, codon optimization, expression feasibility, and
        ML-based viability — in a single pipeline run.
      </p>
      <Link href="/dashboard" className="btn">
        Open Dashboard
      </Link>

      <div className="grid sm:grid-cols-3 gap-4 mt-16 text-left">
        {[
          ["Sequence & Mutation Analysis", "ORFs, codon stats, SNP/indel/frameshift classification, protein impact."],
          ["Codon Optimization & Expression", "CAI, rare codons, organism-specific optimization, 0-100 expression score."],
          ["ML Viability & Readiness Score", "XGBoost construct viability with SHAP, plus a unified readiness score."],
        ].map(([title, desc]) => (
          <div className="card" key={title}>
            <h3 className="font-semibold mb-1">{title}</h3>
            <p className="text-sm text-slate-400">{desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
