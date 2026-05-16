import { useEffect, useMemo, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import {
  Activity, Cpu, Zap, Shield, Lock, Atom, GitBranch, Database,
  Play, RefreshCw, Network, Binary, KeySquare, Sparkles
} from "lucide-react";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
  LineChart, Line, CartesianGrid,
} from "recharts";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const QUANT_COLORS = {
  Q2_K: "#ef4444", Q3_K: "#f97316", Q4_K_M: "#eab308",
  Q5_K_M: "#84cc16", Q6_K: "#22d3ee", Q8_0: "#a78bfa",
  IQ2_XS: "#10b981", IQ3_M: "#14b8a6", IQ4_XS: "#06b6d4", IQ4_NL: "#3b82f6",
};

function Panel({ icon: Icon, title, subtitle, children, testid }) {
  return (
    <div
      data-testid={testid}
      className="relative border border-zinc-800/80 bg-zinc-950/60 backdrop-blur-sm rounded-none p-5 transition-all hover:border-amber-400/40"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 border border-amber-500/30 bg-amber-500/5">
            <Icon className="w-4 h-4 text-amber-400" />
          </div>
          <div>
            <h3 className="text-[11px] tracking-[0.3em] uppercase text-zinc-400 font-mono">{title}</h3>
            {subtitle && <p className="text-xs text-zinc-600 mt-0.5 font-mono">{subtitle}</p>}
          </div>
        </div>
      </div>
      <div className="text-sm text-zinc-200">{children}</div>
    </div>
  );
}

function Stat({ label, value, hint }) {
  return (
    <div className="flex justify-between items-baseline border-b border-zinc-900 py-1.5 last:border-0">
      <span className="text-[11px] uppercase tracking-wider text-zinc-500 font-mono">{label}</span>
      <span className="font-mono text-zinc-100 text-sm">{value}{hint && <span className="text-zinc-600 ml-1 text-[10px]">{hint}</span>}</span>
    </div>
  );
}

function Btn({ onClick, busy, children, testid, variant = "primary" }) {
  const styles = variant === "primary"
    ? "border-amber-400/60 text-amber-300 hover:bg-amber-400/10 hover:border-amber-300"
    : "border-zinc-700 text-zinc-300 hover:border-zinc-500 hover:text-zinc-100";
  return (
    <button
      data-testid={testid}
      onClick={onClick}
      disabled={busy}
      className={`px-3 py-1.5 text-[11px] uppercase tracking-[0.2em] font-mono border ${styles} disabled:opacity-40 disabled:cursor-not-allowed transition-all`}
    >
      {busy ? <RefreshCw className="w-3 h-3 animate-spin inline" /> : children}
    </button>
  );
}

const CommandCenter = () => {
  const [status, setStatus] = useState(null);
  const [manifest, setManifest] = useState(null);
  const [profiles, setProfiles] = useState({});
  const [bridge, setBridge] = useState(null);
  const [qfx, setQfx] = useState(null);
  const [nnox, setNnox] = useState(null);
  const [onyx, setOnyx] = useState(null);
  const [qint, setQint] = useState(null);
  const [ztds, setZtds] = useState(null);
  const [xyz, setXyz] = useState(null);
  const [qent, setQent] = useState(null);
  const [busy, setBusy] = useState({});
  const [pipeline, setPipeline] = useState(null);
  const [history, setHistory] = useState([]);
  const [message, setMessage] = useState("FXION-ONYX QUANTUM GENESIS PAYLOAD");

  const set = (k, v) => setBusy(b => ({ ...b, [k]: v }));

  const loadStatic = async () => {
    try {
      const [s, m, p, b, h] = await Promise.all([
        axios.get(`${API}/system/status`),
        axios.get(`${API}/manifest`),
        axios.get(`${API}/qfx/profiles`),
        axios.get(`${API}/neuronbridge/summary`),
        axios.get(`${API}/pipeline/history`),
      ]);
      setStatus(s.data); setManifest(m.data);
      setProfiles(p.data.profiles); setBridge(b.data);
      setHistory(h.data.history || []);
    } catch (e) { console.error(e); }
  };

  useEffect(() => { loadStatic(); }, []);

  const runQfx = async () => { set("qfx", 1); try { const r = await axios.post(`${API}/qfx/optimize`, { rounds: 16 }); setQfx(r.data); } finally { set("qfx", 0); } };
  const runNnox = async () => { set("nnox", 1); try { const r = await axios.post(`${API}/nnox/route`, { jobs: 12 }); setNnox(r.data); } finally { set("nnox", 0); } };
  const runOnyx = async () => { set("onyx", 1); try { const r = await axios.post(`${API}/onyx/run`, { steps: 8 }); setOnyx(r.data); } finally { set("onyx", 0); } };
  const runQint = async () => { set("qint", 1); try { const r = await axios.post(`${API}/qint/compress`, { size: 8192, seed: Date.now() % 1000 }); setQint(r.data); } finally { set("qint", 0); } };
  const runZtds = async () => { set("ztds", 1); try { const r = await axios.post(`${API}/ztds/encrypt`, { message }); setZtds(r.data); } finally { set("ztds", 0); } };
  const runXyz = async () => { set("xyz", 1); try { const r = await axios.get(`${API}/xyz/handshake`); setXyz(r.data); } finally { set("xyz", 0); } };
  const runQent = async () => { set("qent", 1); try { const r = await axios.post(`${API}/quantum/entropy`, { size: 2048 }); setQent(r.data); } finally { set("qent", 0); } };

  const runAll = async () => {
    set("all", 1);
    try {
      const r = await axios.post(`${API}/pipeline/run-all`);
      setPipeline(r.data);
      setQfx(r.data.qfx); setNnox({ summary: r.data.nnox, routes: [] });
      setOnyx({ report: r.data.onyx, metrics: [] }); setQint(r.data.qint_int2);
      setZtds(r.data.ztds); setXyz(r.data.xyz_elliptic); setQent(r.data.quantum_entropy);
      const h = await axios.get(`${API}/pipeline/history`); setHistory(h.data.history || []);
      const s = await axios.get(`${API}/system/status`); setStatus(s.data);
    } finally { set("all", 0); }
  };

  const resetEngine = async () => { set("reset", 1); try { await axios.post(`${API}/system/reset`); await loadStatic(); setQfx(null); setNnox(null); setOnyx(null); setPipeline(null); } finally { set("reset", 0); } };

  const radarData = useMemo(() => {
    return Object.entries(profiles).map(([name, p]) => ({
      quant: name,
      accuracy: Math.round(p.accuracy * 100),
      speed: Math.round((p.base_tps / 220) * 100),
      vram: Math.round((1 - p.vram_gb / 4) * 100),
    }));
  }, [profiles]);

  const qfxBarData = useMemo(() => {
    if (!qfx?.stats) return [];
    return Object.entries(qfx.stats).map(([q, s]) => ({ quant: q, reward: s.avg_reward, pulls: s.pulls, family: s.family }));
  }, [qfx]);

  const modulesConnected = [
    { name: "system_class",   ok: !!status,   icon: Cpu },
    { name: "qfx_optimizer",  ok: !!qfx,      icon: Zap },
    { name: "nnox_scheduler", ok: !!nnox,     icon: Network },
    { name: "onyx_runtime",   ok: !!onyx,     icon: Activity },
    { name: "qint_int2",      ok: !!qint,     icon: Binary },
    { name: "ztds_entropy",   ok: !!ztds,     icon: Lock },
    { name: "xyz_elliptic",   ok: !!xyz,      icon: Shield },
    { name: "quantum_entropy",ok: !!qent,     icon: Atom },
    { name: "neuron_bridge",  ok: !!bridge,   icon: GitBranch },
  ];
  const connectedCount = modulesConnected.filter(m => m.ok).length;

  return (
    <div className="min-h-screen bg-black text-zinc-100" style={{ fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}>
      {/* grain overlay */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.04] z-0" style={{
        backgroundImage: "radial-gradient(circle at 1px 1px, rgba(251,191,36,0.5) 1px, transparent 0)",
        backgroundSize: "32px 32px"
      }}/>

      {/* HEADER */}
      <header className="relative border-b border-zinc-900/80 bg-zinc-950/40 backdrop-blur-md sticky top-0 z-20">
        <div className="max-w-[1600px] mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-10 h-10 border border-amber-400/60 flex items-center justify-center bg-amber-400/5">
                <Sparkles className="w-5 h-5 text-amber-300" />
              </div>
              <div className="absolute -bottom-1 -right-1 w-2 h-2 bg-emerald-400 animate-pulse" />
            </div>
            <div>
              <h1 className="text-lg tracking-[0.35em] uppercase text-amber-300 font-bold">FXION · ONYX</h1>
              <p className="text-[10px] tracking-[0.4em] uppercase text-zinc-500 font-mono">
                Omnitech Q8 · Quantum Genesis · Build {manifest?.build || "FINAL-Q8"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right text-[10px] font-mono">
              <div className="text-zinc-500 uppercase tracking-wider">Modules Online</div>
              <div className="text-emerald-300 text-sm">{connectedCount} / {modulesConnected.length}</div>
            </div>
            <Btn onClick={runAll} busy={busy.all} testid="run-all-btn">
              <Play className="w-3 h-3 inline mr-2"/>Run Full Stack
            </Btn>
            <Btn onClick={resetEngine} busy={busy.reset} variant="ghost" testid="reset-btn">Reset</Btn>
          </div>
        </div>
        {/* connection strip */}
        <div className="max-w-[1600px] mx-auto px-6 pb-3 flex flex-wrap gap-2">
          {modulesConnected.map((m, i) => (
            <div key={m.name} data-testid={`module-pill-${m.name}`}
              className={`flex items-center gap-1.5 px-2 py-1 text-[10px] uppercase tracking-wider font-mono border ${
                m.ok ? "border-emerald-500/40 text-emerald-300 bg-emerald-500/5"
                     : "border-zinc-800 text-zinc-600"
              }`}>
              <m.icon className="w-3 h-3"/>
              {m.name}
              <span className={`ml-1 w-1.5 h-1.5 rounded-full ${m.ok ? "bg-emerald-400 animate-pulse" : "bg-zinc-700"}`}/>
            </div>
          ))}
        </div>
      </header>

      <main className="relative max-w-[1600px] mx-auto px-6 py-8 z-10">
        {/* TOP ROW: System + NeuronBridge + Manifest */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          <Panel icon={Cpu} title="FXION System" subtitle="UCB1 · Q8 Augmented Policy" testid="system-panel">
            {status && <>
              <Stat label="Mode" value={status.mode}/>
              <Stat label="Best Quant" value={status.best_quant}/>
              <Stat label="GPU" value={status.gpu.name}/>
              <Stat label="History" value={status.history_len}/>
              <Stat label="Running" value={status.running ? "● Active" : "○ Idle"}/>
            </>}
          </Panel>

          <Panel icon={GitBranch} title="NeuronBridge 8.712" subtitle="Quantum Genesis Config" testid="bridge-panel">
            {bridge && <>
              <Stat label="Version" value={bridge.version}/>
              <Stat label="Topology" value={`${bridge.layers}L × ${bridge.bridges_per_layer}B`}/>
              <Stat label="QBits Total" value={bridge.qbits_total.toLocaleString()}/>
              <Stat label="Primary Quant" value={bridge.primary_quant}/>
              <Stat label="Target TPS / QPS" value={`${bridge.target_tps} / ${bridge.target_qps}`}/>
              <Stat label="Clock Lock" value={`${bridge.clock_lock_mhz} MHz`}/>
              <Stat label="Self Heal" value={bridge.self_heal_enabled ? "✓ Armed" : "✗"}/>
            </>}
          </Panel>

          <Panel icon={Database} title="Manifest" subtitle="OMNITECH FINAL-Q8" testid="manifest-panel">
            {manifest && <>
              <Stat label="Project" value={manifest.project}/>
              <Stat label="Version" value={manifest.version}/>
              <Stat label="Build" value={manifest.build}/>
              <Stat label="Quant Policy" value={manifest.policy}/>
              <Stat label="Target GPU" value={manifest.gpu}/>
              <Stat label="Modes" value={manifest.modes}/>
              <Stat label="Modules" value={manifest.modules.length}/>
            </>}
          </Panel>
        </div>

        {/* QUANT RADAR + QFX */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
          <Panel icon={Activity} title="Quant Profile Radar" subtitle="Accuracy · Speed · VRAM Efficiency" testid="radar-panel">
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#27272a" />
                  <PolarAngleAxis dataKey="quant" tick={{ fill: "#a1a1aa", fontSize: 10, fontFamily: "monospace" }} />
                  <PolarRadiusAxis domain={[0, 100]} tick={{ fill: "#52525b", fontSize: 9 }} stroke="#27272a" />
                  <Radar name="Accuracy" dataKey="accuracy" stroke="#fbbf24" fill="#fbbf24" fillOpacity={0.25}/>
                  <Radar name="Speed" dataKey="speed" stroke="#10b981" fill="#10b981" fillOpacity={0.2}/>
                  <Radar name="VRAM" dataKey="vram" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.15}/>
                  <Tooltip contentStyle={{ background: "#09090b", border: "1px solid #27272a", fontFamily: "monospace", fontSize: 11 }}/>
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </Panel>

          <Panel icon={Zap} title="QFX Optimizer · UCB1 RL" subtitle={qfx ? `Best: ${qfx.best} · ${qfx.rounds} rounds` : "INT4 / Q8 / IQ adaptive"} testid="qfx-panel">
            <div className="flex justify-end mb-2"><Btn onClick={runQfx} busy={busy.qfx} testid="run-qfx-btn">Optimize 16 rounds</Btn></div>
            {qfxBarData.length > 0 ? (
              <div className="h-[260px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={qfxBarData}>
                    <CartesianGrid stroke="#18181b" strokeDasharray="2 2"/>
                    <XAxis dataKey="quant" tick={{ fill: "#71717a", fontSize: 9, fontFamily: "monospace" }} angle={-30} textAnchor="end" height={50}/>
                    <YAxis tick={{ fill: "#71717a", fontSize: 9, fontFamily: "monospace" }} />
                    <Tooltip contentStyle={{ background: "#09090b", border: "1px solid #27272a", fontFamily: "monospace", fontSize: 11 }}/>
                    <Bar dataKey="reward" radius={[2, 2, 0, 0]}>
                      {qfxBarData.map((entry, i) => (
                        <Cell key={i} fill={QUANT_COLORS[entry.quant] || "#a1a1aa"}/>
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[260px] flex items-center justify-center text-zinc-600 text-xs uppercase tracking-widest">
                Press Optimize to run UCB1 bandit
              </div>
            )}
          </Panel>
        </div>

        {/* NNOX + ONYX + QINT */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          <Panel icon={Network} title="NNOX Scheduler" subtitle="GPU · CPU · Hybrid routing" testid="nnox-panel">
            <Btn onClick={runNnox} busy={busy.nnox} testid="run-nnox-btn">Route 12 jobs</Btn>
            <div className="mt-3">
              {nnox?.summary ? <>
                <Stat label="Total Jobs" value={nnox.summary.total}/>
                <Stat label="GPU" value={nnox.summary.gpu}/>
                <Stat label="CPU" value={nnox.summary.cpu}/>
                <Stat label="Hybrid" value={nnox.summary.hybrid}/>
                <Stat label="Avg Latency" value={`${nnox.summary.avg_latency_ms} ms`}/>
              </> : <p className="text-xs text-zinc-600 mt-4">No routes yet.</p>}
            </div>
          </Panel>

          <Panel icon={Activity} title="ONYX Runtime" subtitle="Live inference loop" testid="onyx-panel">
            <Btn onClick={runOnyx} busy={busy.onyx} testid="run-onyx-btn">Run 8 steps</Btn>
            <div className="mt-3">
              {onyx?.report ? <>
                <Stat label="Steps" value={onyx.report.steps}/>
                <Stat label="Avg TPS" value={onyx.report.avg_tps} hint="tok/s"/>
                <Stat label="Total Tokens" value={onyx.report.total_tokens}/>
                <Stat label="Active Quant" value={onyx.report.quant}/>
              </> : <p className="text-xs text-zinc-600 mt-4">Not yet executed.</p>}
            </div>
          </Panel>

          <Panel icon={Binary} title="QINT INT2 Compression" subtitle="Experimental 2-bit weights" testid="qint-panel">
            <Btn onClick={runQint} busy={busy.qint} testid="run-qint-btn">Compress 8192 weights</Btn>
            <div className="mt-3">
              {qint ? <>
                <Stat label="Algorithm" value={qint.algorithm}/>
                <Stat label="Ratio" value={`${qint.compression_ratio}×`}/>
                <Stat label="Original" value={`${qint.original_bytes} B`}/>
                <Stat label="Compressed" value={`${qint.compressed_bytes} B`}/>
                <Stat label="MAE" value={qint.mae.toExponential(2)}/>
                <Stat label="Est. Accuracy" value={`${(qint.estimated_accuracy * 100).toFixed(2)}%`}/>
              </> : <p className="text-xs text-zinc-600 mt-4">Not yet compressed.</p>}
            </div>
          </Panel>
        </div>

        {/* CYBERSECURITY ROW */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          <Panel icon={Lock} title="ZTDS · Dynamic Entropy XOR" subtitle="Algebraic GF(2⁸) stream" testid="ztds-panel">
            <div className="flex gap-2 mb-3">
              <input
                data-testid="ztds-input"
                className="flex-1 bg-zinc-950 border border-zinc-800 px-2 py-1.5 text-xs font-mono text-zinc-200 focus:border-amber-400 focus:outline-none"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="message to encrypt..."
              />
              <Btn onClick={runZtds} busy={busy.ztds} testid="run-ztds-btn">Encrypt</Btn>
            </div>
            {ztds && <>
              <Stat label="Key ID" value={ztds.key_id}/>
              <Stat label="Length" value={`${ztds.length} B`}/>
              <Stat label="PT Entropy" value={`${ztds.plaintext_entropy_bits} bpb`}/>
              <Stat label="CT Entropy" value={`${ztds.ciphertext_entropy_bits} bpb`}/>
              <Stat label="Roundtrip" value={ztds.match ? "✓ match" : "✗ FAIL"}/>
              <div className="mt-2 text-[10px] font-mono text-zinc-500 break-all max-h-16 overflow-y-auto border-t border-zinc-900 pt-2">
                {ztds.ciphertext_hex}
              </div>
            </>}
          </Panel>

          <Panel icon={Shield} title="X/Y/Z Axial Elliptic" subtitle="secp256k1 tri-axial ECDH" testid="xyz-panel">
            <Btn onClick={runXyz} busy={busy.xyz} testid="run-xyz-btn">Run Handshake</Btn>
            <div className="mt-3">
              {xyz ? <>
                <Stat label="Curve" value="secp256k1"/>
                <Stat label="All Axes Agree" value={xyz.all_axes_agree ? "✓ COHERENT" : "✗"}/>
                {Object.entries(xyz.axes).map(([k, v]) => (
                  <Stat key={k} label={`Axis ${k}`} value={v.shared_digest.substring(0,12) + "…"}/>
                ))}
                <div className="mt-2 text-[9px] font-mono text-zinc-500 break-all border-t border-zinc-900 pt-2">
                  sha512: {xyz.coherence_digest_sha512.substring(0, 64)}…
                </div>
              </> : <p className="text-xs text-zinc-600 mt-4">No handshake yet.</p>}
            </div>
          </Panel>

          <Panel icon={Atom} title="Quantum Cryptographic Entropy" subtitle="SHA3-512 sponge · Von-Neumann debias" testid="qent-panel">
            <Btn onClick={runQent} busy={busy.qent} testid="run-qent-btn">Sample 2048 bytes</Btn>
            <div className="mt-3">
              {qent ? <>
                <Stat label="Bytes" value={qent.bytes_generated}/>
                <Stat label="Shannon" value={`${qent.shannon_bits_per_byte} bpb`} hint="/ 8.000"/>
                <Stat label="χ²" value={qent.chi_square} hint={`dof ${qent.chi_square_dof}`}/>
                <Stat label="Runs" value={`${qent.runs_test.runs} / ${qent.runs_test.expected}`}/>
                <Stat label="Debias Yield" value={`${(qent.debiased_bit_yield*100).toFixed(1)}%`}/>
                <div className="mt-2 text-[9px] font-mono text-zinc-500 break-all border-t border-zinc-900 pt-2">
                  fp: {qent.fingerprint_sha3_256.substring(0, 48)}…
                </div>
              </> : <p className="text-xs text-zinc-600 mt-4">Not sampled yet.</p>}
            </div>
          </Panel>
        </div>

        {/* PIPELINE + HISTORY */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <Panel icon={Sparkles} title="Pipeline · Run-All" subtitle="End-to-end unified result" testid="pipeline-panel">
            {pipeline ? <>
              <Stat label="Elapsed" value={`${pipeline.elapsed_s} s`}/>
              <Stat label="Best Quant" value={pipeline.qfx.best}/>
              <Stat label="QINT Ratio" value={`${pipeline.qint_int2.compression_ratio}×`}/>
              <Stat label="ZTDS Match" value={pipeline.ztds.match ? "✓" : "✗"}/>
              <Stat label="X/Y/Z Agree" value={pipeline.xyz_elliptic.all_axes_agree ? "✓" : "✗"}/>
              <Stat label="Q-Entropy" value={`${pipeline.quantum_entropy.shannon_bits_per_byte} bpb`}/>
              <Stat label="NNOX Avg" value={`${pipeline.nnox.avg_latency_ms} ms`}/>
              <Stat label="ONYX TPS" value={pipeline.onyx.avg_tps}/>
              <Stat label="Bridge v" value={pipeline.neuron_bridge.version}/>
            </> : <p className="text-xs text-zinc-600 mt-4">Press <span className="text-amber-300">Run Full Stack</span> to execute all 11 modules in sequence.</p>}
          </Panel>

          <Panel icon={KeySquare} title="Run History" subtitle="MongoDB-persisted events" testid="history-panel">
            <div className="max-h-[280px] overflow-y-auto">
              {history.length === 0 && <p className="text-xs text-zinc-600">No runs yet.</p>}
              {history.map((h, i) => (
                <div key={h.id || i} className="border-b border-zinc-900 py-1.5 text-[11px] font-mono flex justify-between gap-2">
                  <span className="text-zinc-500 truncate">{h.event}</span>
                  <span className="text-zinc-400">{h.best || h.elapsed_s + "s"}</span>
                  <span className="text-zinc-600 text-[10px]">{(h.ts || "").substring(11, 19)}</span>
                </div>
              ))}
            </div>
          </Panel>

          <Panel icon={Activity} title="Inference TPS Trend" subtitle="Last GPU loop history" testid="trend-panel">
            {status?.history_len > 0 ? (
              <div className="h-[260px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={(qfx?.log || []).slice(-20)}>
                    <CartesianGrid stroke="#18181b" strokeDasharray="2 2"/>
                    <XAxis dataKey="round" tick={{ fill: "#71717a", fontSize: 9, fontFamily: "monospace" }}/>
                    <YAxis tick={{ fill: "#71717a", fontSize: 9, fontFamily: "monospace" }}/>
                    <Tooltip contentStyle={{ background: "#09090b", border: "1px solid #27272a", fontSize: 11 }}/>
                    <Line type="monotone" dataKey="tps" stroke="#fbbf24" strokeWidth={2} dot={{ r: 2 }}/>
                    <Line type="monotone" dataKey="reward" stroke="#10b981" strokeWidth={1.5} dot={false}/>
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : <p className="text-xs text-zinc-600 mt-4">Run QFX to populate.</p>}
          </Panel>
        </div>

        <footer className="mt-10 pt-6 border-t border-zinc-900 text-[10px] tracking-[0.3em] uppercase text-zinc-600 font-mono flex justify-between">
          <span>FXION-ONYX · OMNITECH Q8 · NeuronBridge 8.712 · Quantum Genesis</span>
          <span>Modules: {connectedCount}/{modulesConnected.length} online · UCB1 · Q8_0 prior +0.12</span>
        </footer>
      </main>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<CommandCenter />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
