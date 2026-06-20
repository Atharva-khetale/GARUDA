"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getToken, runFullAnalysis } from "@/lib/api";
import ScoreCard from "@/components/ScoreCard";
import SeverityPill from "@/components/SeverityPill";

const ORGANISMS = [
  { value: "human", label: "Human" },
  { value: "mouse", label: "Mouse" },
  { value: "ecoli", label: "E. coli" },
  { value: "yeast", label: "Yeast" },
  { value: "cho", label: "CHO Cells" },
];

const SAMPLE_DNA =
  "ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAGGCCTAAAGGGCCTTTTAAAGGATCCAAGCTTGAATTCAGCTGACATCATAATCAGCCATACCACATTTGTAGAGGTTTTACTTGCTTTAAAAAACCTCCCACACCTCCCCCTGAACCTGAAACATAAAATGAATGCAATTGTTGTTGTTAACTTGTTTATTGCAGCTTATAATGGTTACAAATAAAGCAATAGCATCACAAATTTCACAAATAAAGCATTTTTTTCACTGCATTCTAGTTGTGGTTTGTCCAAACTCATCAATGTATCTTATCATGTCTGGATCCGGATCCTGA";

export default function Dashboard() {
  const router = useRouter();
  const [original, setOriginal] = useState(SAMPLE_DNA);
  const [mutated, setMutated] = useState("");
  const [organism, setOrganism] = useState("human");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);

  useEffect(() => {
    if (!getToken()) router.push("/login");
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setResult(null);
    try {
      const data = await runFullAnalysis({
        original_sequence: original,
        mutated_sequence: mutated || undefined,
        organism: organism as any,
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="text-lg font-semibold mb-3">Construct Analysis</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Original DNA sequence (or FASTA)</label>
            <textarea
              className="input font-mono text-xs"
              rows={4}
              required
              value={original}
              onChange={(e) => setOriginal(e.target.value)}
            />
          </div>
          <div>
            <label className="label">Mutated DNA sequence (optional)</label>
            <textarea
              className="input font-mono text-xs"
              rows={3}
              value={mutated}
              onChange={(e) => setMutated(e.target.value)}
              placeholder="Leave blank to skip mutation & protein impact analysis"
            />
          </div>
          <div className="flex items-end gap-4">
            <div className="w-48">
              <label className="label">Target organism</label>
              <select
                className="select"
                value={organism}
                onChange={(e) => setOrganism(e.target.value)}
              >
                {ORGANISMS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <button className="btn" disabled={loading}>
              {loading ? "Running pipeline..." : "Run Full Analysis"}
            </button>
          </div>
          {error && <p className="text-danger text-sm">{error}</p>}
        </form>
      </div>

      {result && <Results result={result} />}
    </div>
  );
}

function Results({ result }: { result: any }) {
  const readiness = result.readiness_score;
  const seq = result.sequence_analysis;
  const expr = result.expression_feasibility;
  const opt = result.codon_optimization;
  const restriction = result.restriction_analysis;
  const mutation = result.mutation_report;
  const protein = result.protein_impact;
  const ml = result.ml_prediction;

  return (
    <div className="space-y-6">
      {/* Readiness summary */}
      <div className="grid sm:grid-cols-3 gap-4">
        <ScoreCard label="Construct Readiness" score={readiness.construct_score} sub={readiness.recommendation} />
        <ScoreCard
          label="Expression Score"
          score={readiness.expression_score}
          sub={readiness.expression_category}
        />
        <div className="card">
          <span className="label">Mutation Severity</span>
          <div className="mt-2">
            <SeverityPill severity={readiness.mutation_severity} />
          </div>
          <span className="label mt-4 block">Optimization Needed</span>
          <p className="text-sm mt-1">{readiness.optimization_needed}</p>
        </div>
      </div>

      {/* Sequence Analysis */}
      <Section title="Sequence Analysis (Module 1)">
        <div className="grid sm:grid-cols-4 gap-4 text-sm">
          <Stat label="Type" value={seq.seq_type} />
          <Stat label="Length (nt)" value={seq.length} />
          <Stat label="GC Content" value={`${seq.gc_content}%`} />
          <Stat label="ORFs Found" value={seq.orfs?.length ?? 0} />
        </div>
        <div className="mt-4">
          <span className="label">Translated protein</span>
          <p className="font-mono text-xs break-all mt-1 text-slate-300">{seq.protein_sequence}</p>
        </div>
      </Section>

      {/* Expression */}
      <Section title="Expression Feasibility (Module 6)">
        <div className="grid sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            {Object.entries(expr.component_scores).map(([k, v]) => (
              <Bar key={k} label={k.replace(/_/g, " ")} value={v as number} />
            ))}
          </div>
          <ul className="text-sm text-slate-300 space-y-1 list-disc list-inside">
            {expr.reasoning.map((r: string, i: number) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      </Section>

      {/* Codon Optimization */}
      <Section title="Codon Optimization (Module 5)">
        <div className="grid sm:grid-cols-2 gap-4 text-sm">
          <ComparisonTable
            title="Before"
            rows={[
              ["CAI", opt.before.cai],
              ["GC Content", `${opt.before.gc_content}%`],
              ["Rare Codons", opt.before.rare_codon_count],
            ]}
          />
          <ComparisonTable
            title="After"
            rows={[
              ["CAI", opt.after.cai],
              ["GC Content", `${opt.after.gc_content}%`],
              ["Rare Codons", opt.after.rare_codon_count],
            ]}
          />
        </div>
        <p className="text-sm mt-3 text-slate-400">
          {opt.codons_changed} of {opt.total_codons} codons changed for {opt.organism} (CAI Δ{" "}
          {opt.expected_improvement.cai_delta >= 0 ? "+" : ""}
          {opt.expected_improvement.cai_delta}).
        </p>
      </Section>

      {/* Restriction sites */}
      <Section title="Restriction Enzyme Analysis (Module 4)">
        {restriction.total_cut_sites === 0 ? (
          <p className="text-sm text-slate-400">No sites found for the default enzyme panel.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="text-slate-400 text-left">
              <tr>
                <th className="py-1">Enzyme</th>
                <th>Recognition Site</th>
                <th>Cut Positions</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(restriction.enzymes).map(([name, data]: [string, any]) => (
                <tr key={name} className="border-t border-border">
                  <td className="py-1">{name}</td>
                  <td className="font-mono">{data.recognition_site}</td>
                  <td>{data.cut_positions.join(", ") || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>

      {/* Mutation + Protein impact */}
      {mutation && (
        <Section title="Mutation Analysis (Module 2 & 3)">
          <table className="w-full text-sm mb-4">
            <thead className="text-slate-400 text-left">
              <tr>
                <th className="py-1">Position</th>
                <th>Original</th>
                <th>Mutated</th>
                <th>Type</th>
                <th>Impact</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {mutation.mutations.map((m: any, i: number) => (
                <tr key={i} className="border-t border-border">
                  <td className="py-1">{m.position}</td>
                  <td className="font-mono">{m.original_codon ?? "—"}</td>
                  <td className="font-mono">{m.mutated_codon ?? "—"}</td>
                  <td>{m.mutation_type}</td>
                  <td className="text-slate-400">{m.impact}</td>
                  <td>
                    <SeverityPill severity={m.severity} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {protein && (
            <div className="grid sm:grid-cols-2 gap-4 text-sm">
              <Stat label="Functional Impact Score" value={`${protein.functional_impact_score} / 100`} />
              <Stat label="Verdict" value={protein.verdict} />
              <Stat label="Amino Acid Changes" value={protein.amino_acid_changes} />
              <Stat label="Protein Length Change" value={protein.protein_length_change} />
            </div>
          )}
        </Section>
      )}

      {/* ML Prediction */}
      <Section title="ML Construct Viability (Module 7)">
        <div className="grid sm:grid-cols-3 gap-4 text-sm">
          <Stat label="Model" value={ml.model} />
          <Stat label="Prediction" value={ml.prediction} />
          <Stat label="Confidence" value={`${(ml.confidence * 100).toFixed(1)}%`} />
        </div>
        {Object.keys(ml.feature_importance || {}).length > 0 && (
          <div className="mt-4 space-y-2">
            {Object.entries(ml.feature_importance).map(([k, v]) => (
              <Bar key={k} label={k.replace(/_/g, " ")} value={(v as number) * 100} />
            ))}
          </div>
        )}
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card">
      <h2 className="font-semibold mb-3">{title}</h2>
      {children}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: any }) {
  return (
    <div>
      <span className="label">{label}</span>
      <p className="mt-1">{String(value)}</p>
    </div>
  );
}

function ComparisonTable({ title, rows }: { title: string; rows: [string, any][] }) {
  return (
    <div>
      <span className="label">{title}</span>
      <table className="w-full mt-1">
        <tbody>
          {rows.map(([k, v]) => (
            <tr key={k} className="border-t border-border">
              <td className="py-1 text-slate-400">{k}</td>
              <td className="text-right">{String(v)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Bar({ label, value }: { label: string; value: number }) {
  const pct = Math.max(0, Math.min(100, value));
  const color = pct >= 80 ? "bg-accent2" : pct >= 50 ? "bg-warn" : "bg-danger";
  return (
    <div>
      <div className="flex justify-between text-xs mb-1 capitalize">
        <span>{label}</span>
        <span>{pct.toFixed(1)}</span>
      </div>
      <div className="h-2 rounded bg-border overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
