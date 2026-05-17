import { useEffect, useMemo, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import {
  Activity, Cpu, Zap, Shield, Lock, Atom, GitBranch, Database,
  Play, RefreshCw, Network, Binary, KeySquare, Sparkles,
  Layers, Brain, Waves, Package, ShieldCheck, Gauge
} from "lucide-react";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
  LineChart, Line, CartesianGrid, ScatterChart, Scatter, ZAxis,
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
  const [qintBench, setQintBench] = useState(null);
  const [qiLayers, setQiLayers] = useState(null);
  const [deep, setDeep] = useState(null);
  const [seismo, setSeismo] = useState(null);
  const [hardR, setHardR] = useState(null);
  const [ztdsDeep, setZtdsDeep] = useState(null);
  const [hyperAVX, setHyperAVX] = useState(null);
  const [hyperARM, setHyperARM] = useState(null);
  const [hyperCompare, setHyperCompare] = useState(null);
  const [pcie, setPcie] = useState(null);
  const [pcieSrc, setPcieSrc] = useState(null);
  const [showSrc, setShowSrc] = useState(false);
  const [live, setLive] = useState(false);
  const [liveTick, setLiveTick] = useState(null);
  const [lastSync, setLastSync] = useState(null);
  const [snapshots, setSnapshots] = useState([]);
  const [toast, setToast] = useState(null);
  const [busy, setBusy] = useState({});
  const [pipeline, setPipeline] = useState(null);
  const [history, setHistory] = useState([]);
  const [message, setMessage] = useState("FXION-ONYX QUANTUM GENESIS PAYLOAD");

  const set = (k, v) => setBusy(b => ({ ...b, [k]: v }));

  const loadStatic = async () => {
    try {
      const [s, m, p, b, h, sn] = await Promise.all([
        axios.get(`${API}/system/status`),
        axios.get(`${API}/manifest`),
        axios.get(`${API}/qfx/profiles`),
        axios.get(`${API}/neuronbridge/summary`),
        axios.get(`${API}/pipeline/history`),
        axios.get(`${API}/snapshot/list`),
      ]);
      setStatus(s.data); setManifest(m.data);
      setProfiles(p.data.profiles); setBridge(b.data);
      setHistory(h.data.history || []);
      setSnapshots(sn.data.snapshots || []);
    } catch (e) { console.error(e); }
  };

  useEffect(() => { loadStatic(); }, []);

  // LIVE polling
  useEffect(() => {
    if (!live) return;
    let mounted = true;
    const tick = async () => {
      try {
        const r = await axios.get(`${API}/live/tick`);
        if (!mounted) return;
        setLiveTick(r.data);
        setLastSync(Date.now());
        // also refresh light status
        setStatus(prev => prev ? { ...prev, best_quant: r.data.best_quant, history_len: r.data.tick.iter + 1 } : prev);
      } catch (e) {/* ignore */}
    };
    tick();
    const id = setInterval(tick, 3000);
    return () => { mounted = false; clearInterval(id); };
  }, [live]);

  const saveSnapshot = async () => {
    set("snap", 1);
    try {
      const r = await axios.post(`${API}/snapshot/save`);
      setToast(`📸 Snapshot saved · ${r.data.snapshot_id.substring(0,8)} · ${r.data.modules} modules`);
      const list = await axios.get(`${API}/snapshot/list`);
      setSnapshots(list.data.snapshots || []);
      setTimeout(() => setToast(null), 4000);
    } finally { set("snap", 0); }
  };

  const loadSnapshot = async (sid) => {
    set("snap", 1);
    try {
      const r = await axios.get(`${API}/snapshot/${sid}`);
      const p = r.data.payload;
      setPipeline(p);
      setQfx(p.qfx); setNnox({ summary: p.nnox, routes: [] });
      setOnyx({ report: p.onyx, metrics: [] });
      setQint(p.qint_int2); setZtds(p.ztds); setXyz(p.xyz_elliptic); setQent(p.quantum_entropy);
      setQintBench(p.qint_bench);
      setSeismo(p.elliptic_seismo ? { ...p.elliptic_seismo, x: [], y: [] } : null);
      setHardR(p.hard_compress);
      setToast(`✓ Snapshot ${sid.substring(0,8)} loaded`);
      setTimeout(() => setToast(null), 3000);
    } finally { set("snap", 0); }
  };

  const runQfx = async () => { set("qfx", 1); try { const r = await axios.post(`${API}/qfx/optimize`, { rounds: 16 }); setQfx(r.data); } finally { set("qfx", 0); } };
  const runNnox = async () => { set("nnox", 1); try { const r = await axios.post(`${API}/nnox/route`, { jobs: 12 }); setNnox(r.data); } finally { set("nnox", 0); } };
  const runOnyx = async () => { set("onyx", 1); try { const r = await axios.post(`${API}/onyx/run`, { steps: 8 }); setOnyx(r.data); } finally { set("onyx", 0); } };
  const runQint = async () => { set("qint", 1); try { const r = await axios.post(`${API}/qint/compress`, { size: 8192, seed: Date.now() % 1000 }); setQint(r.data); } finally { set("qint", 0); } };
  const runZtds = async () => { set("ztds", 1); try { const r = await axios.post(`${API}/ztds/encrypt`, { message }); setZtds(r.data); } finally { set("ztds", 0); } };
  const runXyz = async () => { set("xyz", 1); try { const r = await axios.get(`${API}/xyz/handshake`); setXyz(r.data); } finally { set("xyz", 0); } };
  const runQent = async () => { set("qent", 1); try { const r = await axios.post(`${API}/quantum/entropy`, { size: 2048 }); setQent(r.data); } finally { set("qent", 0); } };

  const runQintBench = async () => { set("qbench", 1); try { const r = await axios.post(`${API}/qint/bench-all`, { size: 8192 }); setQintBench(r.data); } finally { set("qbench", 0); } };
  const runQI = async () => { set("qi", 1); try { const r = await axios.get(`${API}/qi/neuronbridge`); setQiLayers(r.data); } finally { set("qi", 0); } };
  const runDeep = async () => { set("deep", 1); try { const r = await axios.post(`${API}/deep/forward`, { nodes: 16, steps: 8 }); setDeep(r.data); } finally { set("deep", 0); } };
  const runSeismo = async () => { set("seismo", 1); try { const r = await axios.post(`${API}/elliptic/seismo`, { a: 3, b: 2, n: 200 }); setSeismo(r.data); } finally { set("seismo", 0); } };
  const runHard = async () => { set("hard", 1); try { const r = await axios.post(`${API}/hard/roundtrip`, {}); setHardR(r.data); } finally { set("hard", 0); } };
  const runZtdsDeep = async () => { set("ztdsd", 1); try { const r = await axios.post(`${API}/ztds/deep`, { message, rounds: 4 }); setZtdsDeep(r.data); } finally { set("ztdsd", 0); } };

  const runHyperCompare = async () => {
    set("hyper", 1);
    try {
      const r = await axios.post(`${API}/hyperlearn/compare`, { epochs: 40, weight_dim: 256 });
      setHyperCompare(r.data);
      setHyperAVX(r.data.avx512);
      setHyperARM(r.data.cortex_a72);
    } finally { set("hyper", 0); }
  };

  const runPcie = async () => {
    set("pcie", 1);
    try {
      const [r, s] = await Promise.all([
        axios.post(`${API}/pcie/run`, { epochs: 256, capture_every: 8 }),
        axios.get(`${API}/pcie/source`),
      ]);
      setPcie(r.data);
      setPcieSrc(s.data);
    } finally { set("pcie", 0); }
  };

  const runAll = async () => {
    set("all", 1);
    try {
      const r = await axios.post(`${API}/pipeline/run-all`);
      setPipeline(r.data);
      setQfx(r.data.qfx); setNnox({ summary: r.data.nnox, routes: [] });
      setOnyx({ report: r.data.onyx, metrics: [] }); setQint(r.data.qint_int2);
      setZtds(r.data.ztds); setXyz(r.data.xyz_elliptic); setQent(r.data.quantum_entropy);
      // v2 panels
      setQintBench(r.data.qint_bench);
      setQiLayers(r.data.qi_neuronbridge ? { ...r.data.qi_neuronbridge, layers: r.data.qi_neuronbridge.layers_sample || [] } : null);
      setDeep(r.data.deep_learn_sdk ? { ...r.data.deep_learn_sdk, steps: r.data.deep_learn_sdk.steps_sample || [] } : null);
      setSeismo(r.data.elliptic_seismo ? { ...r.data.elliptic_seismo, x: [], y: [] } : null);
      setHardR(r.data.hard_compress);
      const h = await axios.get(`${API}/pipeline/history`); setHistory(h.data.history || []);
      const s = await axios.get(`${API}/system/status`); setStatus(s.data);
      // pull QI full layers + seismo wave detail asynchronously (for live charts)
      axios.get(`${API}/qi/neuronbridge`).then(x => setQiLayers(x.data)).catch(() => {});
      axios.post(`${API}/elliptic/seismo`, { a: 3, b: 2, n: 200 }).then(x => setSeismo(x.data)).catch(() => {});
      axios.post(`${API}/deep/forward`, { nodes: 16, steps: 8 }).then(x => setDeep(x.data)).catch(() => {});
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
    { name: "qi_neuronbridge",ok: !!qiLayers, icon: Layers },
    { name: "deep_learn_sdk", ok: !!deep,     icon: Brain },
    { name: "elliptic_seismo",ok: !!seismo,   icon: Waves },
    { name: "hard_compress",  ok: !!hardR,    icon: Package },
    { name: "qint_levels",    ok: !!qintBench,icon: Gauge },
    { name: "hyperlearn",     ok: !!hyperAVX, icon: Brain },
    { name: "pcie_cuda",      ok: !!pcie,     icon: Cpu },
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
            <button
              data-testid="live-toggle"
              onClick={() => setLive(l => !l)}
              className={`px-3 py-1.5 text-[11px] uppercase tracking-[0.2em] font-mono border transition-all ${
                live ? "border-emerald-400 text-emerald-300 bg-emerald-500/10" : "border-zinc-700 text-zinc-500 hover:border-zinc-500"
              }`}
            >
              <span className={`inline-block w-1.5 h-1.5 mr-2 rounded-full ${live ? "bg-emerald-400 animate-pulse" : "bg-zinc-600"}`}/>
              {live ? "LIVE" : "Live Off"}
            </button>
            <Btn onClick={saveSnapshot} busy={busy.snap} testid="snapshot-btn" variant="ghost">
              📸 Snapshot
            </Btn>
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
        {/* TOAST */}
        {toast && (
          <div data-testid="toast" className="fixed top-24 right-6 z-40 border border-emerald-400/60 bg-emerald-500/10 text-emerald-200 px-4 py-2 text-xs font-mono backdrop-blur-md">
            {toast}
          </div>
        )}

        {/* LIVE STRIP */}
        {live && liveTick && (
          <div data-testid="live-strip" className="mb-4 border border-emerald-500/30 bg-emerald-500/5 px-4 py-2 flex items-center justify-between text-[11px] font-mono">
            <div className="flex items-center gap-4 text-emerald-300">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 bg-emerald-400 animate-pulse rounded-full"/>
                LIVE
              </span>
              <span className="text-zinc-500">iter</span><span>{liveTick.tick.iter}</span>
              <span className="text-zinc-500">quant</span><span style={{color: QUANT_COLORS[liveTick.tick.quant] || "#fbbf24"}}>{liveTick.tick.quant}</span>
              <span className="text-zinc-500">tps</span><span>{liveTick.tick.tps}</span>
              <span className="text-zinc-500">reward</span><span>{liveTick.tick.reward}</span>
              <span className="text-zinc-500">best</span><span className="text-amber-300">{liveTick.best_quant}</span>
              <span className="text-zinc-500">ψ-coh</span><span>{liveTick.qi_avg_coherence}</span>
              <span className="text-zinc-500">active layers</span><span>{liveTick.qi_active}/12</span>
            </div>
            <span className="text-zinc-500">last sync: {lastSync ? Math.max(0, Math.floor((Date.now()-lastSync)/1000)) + "s ago" : "—"}</span>
          </div>
        )}
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

        {/* ───────────── V2 EXPERIMENTAL SECTION ───────────── */}
        <div className="mt-8 mb-4 flex items-center gap-3">
          <div className="h-px flex-1 bg-zinc-900"/>
          <span className="text-[10px] tracking-[0.4em] uppercase text-amber-400/70 font-mono">V2 · Experimental Layer</span>
          <div className="h-px flex-1 bg-zinc-900"/>
        </div>

        {/* QINT levels + QI NeuronBridge */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
          <Panel icon={Gauge} title="QINT 2 · 4 · 8 Bench" subtitle="compress · decompress · speed" testid="qint-bench-panel">
            <Btn onClick={runQintBench} busy={busy.qbench} testid="run-qbench-btn">Benchmark all levels (8k weights)</Btn>
            {qintBench ? (
              <div className="mt-4">
                <div className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={Object.entries(qintBench).map(([k,v])=>({level:k, ratio:v.compression_ratio, enc:v.encode_ms, dec:v.decode_ms, acc:v.estimated_accuracy*100}))}>
                      <CartesianGrid stroke="#18181b" strokeDasharray="2 2"/>
                      <XAxis dataKey="level" tick={{ fill: "#a1a1aa", fontSize: 10, fontFamily: "monospace" }}/>
                      <YAxis tick={{ fill: "#71717a", fontSize: 9, fontFamily: "monospace" }}/>
                      <Tooltip contentStyle={{ background: "#09090b", border: "1px solid #27272a", fontSize: 11 }}/>
                      <Bar dataKey="ratio" fill="#fbbf24" name="Ratio ×"/>
                      <Bar dataKey="acc" fill="#10b981" name="Acc %"/>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="grid grid-cols-3 gap-2 mt-3 text-[10px] font-mono">
                  {Object.entries(qintBench).map(([k,v]) => (
                    <div key={k} className="border border-zinc-900 p-2">
                      <div className="text-amber-300 mb-1">{k}</div>
                      <div className="text-zinc-500">enc {v.encode_ms}ms</div>
                      <div className="text-zinc-500">dec {v.decode_ms}ms</div>
                      <div className="text-zinc-400">{v.compression_ratio}× · {(v.estimated_accuracy*100).toFixed(1)}%</div>
                    </div>
                  ))}
                </div>
              </div>
            ) : <p className="text-xs text-zinc-600 mt-4">Click to run QINT2/4/8 benchmark.</p>}
          </Panel>

          <Panel icon={Layers} title="QI · NeuronBridge Layer Active" subtitle="Per-layer entropy · ψ coherence" testid="qi-panel">
            <Btn onClick={runQI} busy={busy.qi} testid="run-qi-btn">Sample all 12 layers</Btn>
            {qiLayers ? (
              <div className="mt-3">
                <div className="grid grid-cols-2 gap-2 mb-3 text-[11px]">
                  <Stat label="Active" value={`${qiLayers.active_layers}/${qiLayers.layers_total}`}/>
                  <Stat label="Avg ψ-Coherence" value={qiLayers.avg_coherence}/>
                  <Stat label="Split" value={qiLayers.split_mode}/>
                  <Stat label="Coherent" value={qiLayers.coherent ? "✓" : "✗"}/>
                </div>
                <div className="space-y-1 max-h-[200px] overflow-y-auto">
                  {qiLayers.layers.map(l => (
                    <div key={l.layer} className="flex items-center gap-2 text-[10px] font-mono">
                      <span className="text-zinc-500 w-6">L{l.layer.toString().padStart(2,'0')}</span>
                      <span className={`w-20 ${l.backend.includes('GPU')?'text-cyan-400':'text-amber-300'}`}>{l.backend}</span>
                      <div className="flex-1 h-1 bg-zinc-900 relative">
                        <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-amber-400 to-emerald-400"
                          style={{ width: `${l.coherence*100}%` }}/>
                      </div>
                      <span className="text-zinc-400 w-12 text-right">{l.coherence}</span>
                      <span className="text-zinc-600 w-12 text-right">H={l.entropy_bits}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : <p className="text-xs text-zinc-600 mt-4">Click to map 12 QI layers.</p>}
          </Panel>
        </div>

        {/* Deep SDK + Seismograph */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
          <Panel icon={Brain} title="Deep-Learn SDK · Dynamic Entropic Graph" subtitle="Forward pass · spectral · GELU" testid="deep-panel">
            <Btn onClick={runDeep} busy={busy.deep} testid="run-deep-btn">Forward 8 steps · 16 nodes</Btn>
            {deep ? (
              <div className="mt-3">
                <div className="grid grid-cols-2 gap-2 text-[11px] mb-3">
                  <Stat label="Nodes" value={deep.graph_nodes}/>
                  <Stat label="Edges" value={deep.edges_nonzero}/>
                  <Stat label="Spectral Radius" value={deep.spectral_radius}/>
                  <Stat label="Avg Entropy" value={`${deep.avg_entropy_bits} bpb`}/>
                </div>
                <div className="h-[180px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={deep.steps}>
                      <CartesianGrid stroke="#18181b" strokeDasharray="2 2"/>
                      <XAxis dataKey="step" tick={{ fill: "#71717a", fontSize: 9 }}/>
                      <YAxis tick={{ fill: "#71717a", fontSize: 9 }}/>
                      <Tooltip contentStyle={{ background: "#09090b", border: "1px solid #27272a", fontSize: 11 }}/>
                      <Line type="monotone" dataKey="entropy_bits" stroke="#a78bfa" strokeWidth={2} dot={{r:2}} name="Entropy"/>
                      <Line type="monotone" dataKey="l2_norm" stroke="#06b6d4" strokeWidth={1.5} dot={false} name="L2"/>
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ) : <p className="text-xs text-zinc-600 mt-4">Run forward pass.</p>}
          </Panel>

          <Panel icon={Waves} title="Elliptic Seismograph Wave" subtitle="Lissajous · SHA3 signature" testid="seismo-panel">
            <Btn onClick={runSeismo} busy={busy.seismo} testid="run-seismo-btn">Generate 200-sample wave (a=3, b=2)</Btn>
            {seismo ? (
              <div className="mt-3">
                <div className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart>
                      <CartesianGrid stroke="#18181b" strokeDasharray="2 2"/>
                      <XAxis type="number" dataKey="x" tick={{ fill: "#71717a", fontSize: 9 }} domain={[-1.2, 1.2]}/>
                      <YAxis type="number" dataKey="y" tick={{ fill: "#71717a", fontSize: 9 }} domain={[-1.2, 1.2]}/>
                      <Tooltip contentStyle={{ background: "#09090b", border: "1px solid #27272a", fontSize: 11 }}/>
                      <Scatter data={seismo.x.map((vx,i)=>({x:vx,y:seismo.y[i]}))} fill="#fbbf24" line={{ stroke: '#fbbf24', strokeWidth: 1 }} shape="circle"/>
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
                <div className="grid grid-cols-2 gap-2 mt-2 text-[11px]">
                  <Stat label="Energy" value={seismo.energy}/>
                  <Stat label="ZC X / Y" value={`${seismo.zero_crossings_x} / ${seismo.zero_crossings_y}`}/>
                </div>
                <div className="mt-2 text-[9px] font-mono text-zinc-500 break-all border-t border-zinc-900 pt-2">
                  sig sha3: {seismo.signature_sha3_256.substring(0,48)}…
                </div>
              </div>
            ) : <p className="text-xs text-zinc-600 mt-4">Generate elliptic waveform.</p>}
          </Panel>
        </div>

        {/* Hard Compression + ZTDS Deep */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
          <Panel icon={Package} title="HARD Compression · XOR Prefetch Hash Chain" subtitle="RLE → XOR → DEFLATE → BLAKE2b chain" testid="hard-panel">
            <Btn onClick={runHard} busy={busy.hard} testid="run-hard-btn">Roundtrip compress + tamper hash</Btn>
            {hardR ? (
              <div className="mt-3">
                <Stat label="Original" value={`${hardR.original_bytes} B`}/>
                <Stat label="RLE" value={`${hardR.rle_bytes} B`}/>
                <Stat label="XOR Prefetch" value={`${hardR.xored_bytes} B`}/>
                <Stat label="DEFLATE" value={`${hardR.compressed_bytes} B`}/>
                <Stat label="Ratio" value={`${hardR.compression_ratio}×`}/>
                <Stat label="Hash Chain Blocks" value={hardR.hash_chain_blocks}/>
                <Stat label="Roundtrip" value={hardR.roundtrip_match ? "✓ match" : "✗ FAIL"}/>
                <div className="mt-2 text-[9px] font-mono text-zinc-500 break-all border-t border-zinc-900 pt-2">
                  blake2b root: {hardR.hash_chain_root?.substring(0, 48)}…
                </div>
              </div>
            ) : <p className="text-xs text-zinc-600 mt-4">Run hard compression roundtrip.</p>}
          </Panel>

          <Panel icon={ShieldCheck} title="ZTDS · Deep Mode" subtitle="Multi-round rotating-key encrypt" testid="ztdsdeep-panel">
            <Btn onClick={runZtdsDeep} busy={busy.ztdsd} testid="run-ztdsdeep-btn">Deep encrypt × 4 rounds (current msg)</Btn>
            {ztdsDeep ? (
              <div className="mt-3">
                <Stat label="Rounds" value={ztdsDeep.rounds}/>
                <Stat label="Match" value={ztdsDeep.match ? "✓" : "✗"}/>
                <Stat label="PT Entropy" value={`${ztdsDeep.plaintext_entropy_bits} bpb`}/>
                <Stat label="CT Entropy" value={`${ztdsDeep.ciphertext_entropy_bits} bpb`}/>
                <div className="mt-2 text-[10px] font-mono text-zinc-500">
                  key chain: {ztdsDeep.key_chain_preview?.join(" → ")}
                </div>
                <div className="mt-2 text-[9px] font-mono text-zinc-500 break-all border-t border-zinc-900 pt-2 max-h-16 overflow-y-auto">
                  {ztdsDeep.ciphertext_hex}
                </div>
              </div>
            ) : <p className="text-xs text-zinc-600 mt-4">Run deep ZTDS encryption.</p>}
          </Panel>
        </div>

        {/* PCIe CUDA Engine v2 */}
        <Panel
          icon={Cpu}
          title="FXION PCIe Engine v2 · CUDA Kernel"
          subtitle="12L × 12B · UCB1 √2 · IQ2_XS primary · OBTERON9 QLOGIC entropy-epoch solver"
          testid="pcie-panel"
        >
          <div className="flex justify-between items-center mb-3">
            <p className="text-[11px] text-zinc-500 font-mono">
              3 CUDA kernels (ucb1_score / obteron9_qlogic / update_reward). CPU-mirror runs here · GPU build via <span className="text-amber-300">nvcc -arch=sm_52 -O3</span>.
            </p>
            <div className="flex gap-2">
              <Btn onClick={runPcie} busy={busy.pcie} testid="run-pcie-btn">Run 256 epochs · 144 bridges</Btn>
              <Btn onClick={() => setShowSrc(s => !s)} variant="ghost" testid="toggle-src-btn">{showSrc ? "Hide" : "Show"} .cu source</Btn>
            </div>
          </div>

          {pcie ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Stats */}
              <div className="space-y-1 border border-zinc-800 p-3">
                <div className="text-[11px] uppercase tracking-widest text-amber-300 font-mono mb-2">Solver Output</div>
                <Stat label="Kernel" value="v2 mirror"/>
                <Stat label="Topology" value={pcie.topology}/>
                <Stat label="UCB1 C" value={pcie.ucb1_c.toFixed(4)}/>
                <Stat label="ε threshold" value={pcie.epsilon}/>
                <Stat label="Epochs run" value={`${pcie.epochs_converged} / ${pcie.epochs_target}`}/>
                <Stat label="Converged" value={pcie.converged ? "✓ early stop" : "— max reached"}/>
                <Stat label="Wall time" value={`${pcie.wall_ms} ms`}/>
                <Stat label="Throughput" value={`${pcie.throughput_bridges_per_s.toLocaleString()} bridges/s`}/>
                <Stat label="Best (vote)" value={pcie.best_quant}/>
                <Stat label="IQ2_XS share" value={`${(pcie.iq2_xs_share*100).toFixed(1)}%`}/>
              </div>

              {/* Entropy curve */}
              <div className="border border-zinc-800 p-3">
                <div className="text-[11px] uppercase tracking-widest text-amber-300 font-mono mb-2">Σ Entropy curve · OBTERON9</div>
                <div className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={pcie.entropy_curve.map((v, i) => ({ t: i, H: v }))}>
                      <CartesianGrid stroke="#18181b" strokeDasharray="2 2"/>
                      <XAxis dataKey="t" tick={{ fill: "#71717a", fontSize: 9 }}/>
                      <YAxis tick={{ fill: "#71717a", fontSize: 9 }}/>
                      <Tooltip contentStyle={{ background: "#09090b", border: "1px solid #27272a", fontSize: 11 }}/>
                      <Line type="monotone" dataKey="H" stroke="#fbbf24" strokeWidth={2} dot={false}/>
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="grid grid-cols-2 mt-2 gap-2 text-[10px] font-mono text-zinc-500">
                  <span>H₀: <span className="text-zinc-300">{pcie.global_entropy_initial}</span></span>
                  <span>H_final: <span className="text-zinc-300">{pcie.global_entropy_final}</span></span>
                </div>
              </div>

              {/* Vote histogram */}
              <div className="border border-zinc-800 p-3">
                <div className="text-[11px] uppercase tracking-widest text-amber-300 font-mono mb-2">Vote distribution · 144 bridges</div>
                <div className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={Object.entries(pcie.votes).map(([q, c]) => ({ quant: q, count: c }))}>
                      <CartesianGrid stroke="#18181b" strokeDasharray="2 2"/>
                      <XAxis dataKey="quant" tick={{ fill: "#71717a", fontSize: 9, fontFamily: "monospace" }} angle={-30} textAnchor="end" height={50}/>
                      <YAxis tick={{ fill: "#71717a", fontSize: 9 }}/>
                      <Tooltip contentStyle={{ background: "#09090b", border: "1px solid #27272a", fontSize: 11 }}/>
                      <Bar dataKey="count" radius={[2, 2, 0, 0]}>
                        {Object.entries(pcie.votes).map(([q], i) => (
                          <Cell key={i} fill={QUANT_COLORS[q] || "#a1a1aa"}/>
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Per-layer breakdown */}
              <div className="lg:col-span-3 border-t border-zinc-900 pt-3">
                <div className="text-[11px] uppercase tracking-widest text-amber-300 font-mono mb-2">Per-Layer Result (12L · PHANTOM_SPLIT)</div>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
                  {pcie.per_layer.map(l => (
                    <div key={l.layer} className={`border p-2 text-[10px] font-mono ${l.backend.includes('GPU') ? 'border-cyan-500/30' : 'border-amber-500/30'}`}>
                      <div className="flex justify-between mb-1">
                        <span className="text-zinc-500">L{String(l.layer).padStart(2,'0')}</span>
                        <span className={l.backend.includes('GPU') ? "text-cyan-400" : "text-amber-300"}>
                          {l.backend.includes('GPU') ? "GPU" : "CPU"}
                        </span>
                      </div>
                      <div className="text-zinc-200" style={{color: QUANT_COLORS[l.best] || "#fbbf24"}}>{l.best}</div>
                      <div className="text-zinc-600">IQ2_XS: {l.iq2_xs_count}/12</div>
                      <div className="text-zinc-600">H̄: {l.entropy_mean}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Source viewer */}
              {showSrc && pcieSrc && (
                <div className="lg:col-span-3 border-t border-zinc-900 pt-3">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-[11px] uppercase tracking-widest text-amber-300 font-mono">
                      {pcieSrc.file} · {pcieSrc.lines} lines · kernels: {pcieSrc.kernels.join(", ")}
                    </span>
                    <span className="text-[10px] text-zinc-500 font-mono">{pcieSrc.build_command}</span>
                  </div>
                  <pre className="bg-zinc-950 border border-zinc-900 p-3 text-[10px] font-mono text-zinc-300 max-h-[280px] overflow-auto leading-relaxed">{pcieSrc.source_preview}</pre>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-zinc-600 mt-4">
              Click Run to execute the OBTERON9 QLOGIC entropy-epoch solver. Each epoch evaluates 144 bridges in parallel using vectorised numpy (mirror of the CUDA kernels).
            </p>
          )}
        </Panel>

        {/* HYPERLEARN · XOR-on-Success */}
        <Panel
          icon={Brain}
          title="HyperLearn Epoch · XOR-on-Success"
          subtitle="AVX512 ⚡ vs Cortex-A72 · XOR-mix when reward > 0.72"
          testid="hyperlearn-panel"
        >
          <div className="flex justify-between items-center mb-3">
            <p className="text-[11px] text-zinc-500 font-mono">
              Each epoch trains weights toward target; on success, INT8-quantized weights are XOR-mixed with mask 0x5A and damped 5% back.
            </p>
            <Btn onClick={runHyperCompare} busy={busy.hyper} testid="run-hyper-btn">Run 40 epochs · both backends</Btn>
          </div>

          {hyperAVX && hyperARM ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-2">
              {/* AVX512 column */}
              <div className="border border-emerald-500/20 bg-emerald-500/5 p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] uppercase tracking-widest text-emerald-300 font-mono">AVX512</span>
                  <span className="text-[10px] text-zinc-500">{hyperAVX.backend_label}</span>
                </div>
                <div className="text-[10px] font-mono space-y-1">
                  <div className="flex justify-between"><span className="text-zinc-500">vector</span><span>{hyperAVX.backend_profile.vector_width}-bit</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">fp16</span><span>{hyperAVX.backend_profile.fp16_tflops} TFLOPs</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">int8</span><span>{hyperAVX.backend_profile.int8_tops} TOPs</span></div>
                  <div className="flex justify-between border-t border-zinc-900 pt-1 mt-1"><span className="text-zinc-500">success</span><span className="text-emerald-300">{hyperAVX.successes}/{hyperAVX.epochs} · {(hyperAVX.success_rate*100).toFixed(0)}%</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">xor applied</span><span className="text-amber-300">{hyperAVX.xor_applied}</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">best reward</span><span>{hyperAVX.best_reward}</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">sim total</span><span>{hyperAVX.sim_total_ms} ms</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">throughput</span><span>{hyperAVX.throughput_epochs_per_s} ep/s</span></div>
                </div>
                <div className="text-[9px] font-mono text-zinc-600 mt-2 break-all border-t border-zinc-900 pt-1">
                  fp: {hyperAVX.weight_fingerprint_blake2b_128}
                </div>
              </div>

              {/* Chart middle */}
              <div className="border border-zinc-800 p-3">
                <div className="text-[11px] uppercase tracking-widest text-amber-300 font-mono mb-2">Reward Curve · XOR markers</div>
                <div className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart>
                      <CartesianGrid stroke="#18181b" strokeDasharray="2 2"/>
                      <XAxis dataKey="epoch" type="number" domain={[0, hyperAVX.epochs - 1]} tick={{ fill: "#71717a", fontSize: 9 }} allowDuplicatedCategory={false}/>
                      <YAxis domain={[0, 1]} tick={{ fill: "#71717a", fontSize: 9 }}/>
                      <Tooltip contentStyle={{ background: "#09090b", border: "1px solid #27272a", fontSize: 11 }}/>
                      <Line type="monotone" dataKey="reward" data={hyperAVX.trace} stroke="#10b981" strokeWidth={2} dot={false} name="AVX512"/>
                      <Line type="monotone" dataKey="reward" data={hyperARM.trace} stroke="#06b6d4" strokeWidth={2} dot={false} strokeDasharray="4 2" name="Cortex A72"/>
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-2 flex justify-between text-[10px] font-mono text-zinc-500">
                  <span>━ AVX512</span>
                  <span className="text-cyan-400">┄ Cortex A72</span>
                  <span>threshold ψ {hyperAVX.success_threshold}</span>
                </div>
              </div>

              {/* ARM column */}
              <div className="border border-cyan-500/20 bg-cyan-500/5 p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] uppercase tracking-widest text-cyan-300 font-mono">CORTEX A72</span>
                  <span className="text-[10px] text-zinc-500">{hyperARM.backend_label}</span>
                </div>
                <div className="text-[10px] font-mono space-y-1">
                  <div className="flex justify-between"><span className="text-zinc-500">vector</span><span>{hyperARM.backend_profile.vector_width}-bit NEON</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">fp16</span><span>{hyperARM.backend_profile.fp16_tflops} TFLOPs</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">int8</span><span>{hyperARM.backend_profile.int8_tops} TOPs</span></div>
                  <div className="flex justify-between border-t border-zinc-900 pt-1 mt-1"><span className="text-zinc-500">success</span><span className="text-cyan-300">{hyperARM.successes}/{hyperARM.epochs} · {(hyperARM.success_rate*100).toFixed(0)}%</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">xor applied</span><span className="text-amber-300">{hyperARM.xor_applied}</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">best reward</span><span>{hyperARM.best_reward}</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">sim total</span><span>{hyperARM.sim_total_ms} ms</span></div>
                  <div className="flex justify-between"><span className="text-zinc-500">throughput</span><span>{hyperARM.throughput_epochs_per_s} ep/s</span></div>
                </div>
                <div className="text-[9px] font-mono text-zinc-600 mt-2 break-all border-t border-zinc-900 pt-1">
                  fp: {hyperARM.weight_fingerprint_blake2b_128}
                </div>
              </div>

              {hyperCompare && (
                <div className="lg:col-span-3 border-t border-zinc-900 pt-3 mt-1 flex justify-between text-[11px] font-mono">
                  <span className="text-zinc-500">▶ AVX512 speedup vs A72</span>
                  <span className="text-amber-300 text-base">{hyperCompare.speedup_vs_arm}×</span>
                  <span className="text-zinc-500">Δ success rate</span>
                  <span>{(hyperCompare.delta_success_rate*100).toFixed(2)}%</span>
                  <span className="text-zinc-500">Δ best reward</span>
                  <span>{hyperCompare.delta_best_reward}</span>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-zinc-600 mt-4">
              Click to run 40 epochs on both backends. Successful epochs trigger XOR-mix on INT8-quantized weights (mask 0x5A).
            </p>
          )}
        </Panel>

        {/* SNAPSHOTS */}
        <Panel icon={KeySquare} title="Reel Snapshots · MongoDB persisted" subtitle={`${snapshots.length} captured · click to restore dashboard state`} testid="snapshots-panel">
          {snapshots.length === 0 ? (
            <p className="text-xs text-zinc-600">No snapshots yet. Press 📸 SNAPSHOT in the header to capture all 14 modules.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
              {snapshots.map(s => (
                <button
                  key={s.id}
                  data-testid={`snapshot-${s.id.substring(0,8)}`}
                  onClick={() => loadSnapshot(s.id)}
                  className="text-left border border-zinc-800 hover:border-amber-400/60 bg-zinc-950/50 p-3 transition-all"
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-amber-300 text-[11px] font-mono">{s.id.substring(0, 8)}</span>
                    <span className="text-zinc-500 text-[10px]">{(s.ts || "").substring(11, 19)} UTC</span>
                  </div>
                  <div className="flex justify-between text-[10px] font-mono text-zinc-500">
                    <span>best <span className="text-zinc-300">{s.best_quant}</span></span>
                    <span>{s.modules_count} modules</span>
                    <span>{s.elapsed_s}s</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </Panel>

        <footer className="mt-10 pt-6 border-t border-zinc-900 text-[10px] tracking-[0.3em] uppercase text-zinc-600 font-mono flex justify-between">
          <span>FXION-ONYX · OMNITECH Q8 · NeuronBridge 8.712 · Quantum Genesis</span>
          <span>Modules: {connectedCount}/{modulesConnected.length} online · {live ? "LIVE" : "static"} · UCB1 · Q8_0 prior +0.12</span>
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
