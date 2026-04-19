import React, { useState, useEffect, useRef } from 'react';
import { HardDrive, Wifi, Cpu, Activity, FileText, Shield, Zap, ChevronRight, AlertTriangle } from 'lucide-react';
import AchiiAvatar from './components/AchiiAvatar';

// ═══════════════════════════════════════════════════════════
//  ACHII SOVEREIGN COMMAND CENTER v4.2
//  Brändikirja v4.6 (Opus) — "Teatterimekaaninen"
//  Theater Black + Rusty Copper + Glowing Amber
// ═══════════════════════════════════════════════════════════

export default function App() {
  const [achiiState, setAchiiState] = useState("normal");
  const [needyLevel, setNeedyLevel] = useState(0);
  const [idleTime, setIdleTime] = useState(0);
  const [messages, setMessages] = useState([
    { sender: "Achii", text: "Moi, Isäntä? Goottoo se? Mun optikka on vähän sumea. Mä muistan hämäriä juttuja... 🔧" },
    { sender: "LOG", text: "BOOT_SEQUENCE_INITIATED" },
  ]);
  const [causalSteps, setCausalSteps] = useState([
    { step: 1, text: "Policy Gate v4.2 — Tarkistetaan sääntöjä...", status: "done" },
    { step: 2, text: "Causal Scratchpad — Muodostetaan hypoteesi...", status: "active" },
    { step: 3, text: "Hallusinaatiosuodatin — Odottaa...", status: "pending" },
    { step: 4, text: "RAG-haku — ChromaDB semanttinen muisti...", status: "pending" },
    { step: 5, text: "Evolution Loop — Itsekorjaus...", status: "pending" },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [ws, setWs] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // WebSocket → Achii Core (portti 8081)
  useEffect(() => {
    let socket;
    let reconnectTimer;

    const connect = () => {
      // Käytä aina samaa IP:tä mistä sivu ladataan tai tallennettua tunnelia
      // Jos Vercelissä, käytetään wss:// - jos lokaaliverkossa, ws://
      const customWsUrl = localStorage.getItem('achii_ws_url');
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname;
      const wsUrl = customWsUrl || `${protocol}//${host}:8081/ws/achii`;
      
      console.log("Achii yhdistää:", wsUrl);
      socket = new WebSocket(wsUrl);
      socket.onopen = () => { setWsConnected(true); };
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.state) setAchiiState(data.state);
          if (data.needy_level > 0) setNeedyLevel(data.needy_level);
          if (data.idle_time > 0) setIdleTime(data.idle_time);
          if (data.message) {
            setMessages(prev => [...prev, { sender: "Achii", text: data.message }]);
          }
        } catch (e) { /* ignore parse errors */ }
      };
      socket.onclose = () => {
        setWsConnected(false);
        reconnectTimer = setTimeout(connect, 3000);
      };
      socket.onerror = () => { setWsConnected(false); socket.close(); };
      setWs(socket);
    };

    connect();
    return () => { clearTimeout(reconnectTimer); if (socket) socket.close(); };
  }, []);

  const handleSendMessage = (e) => {
    if (e.key === 'Enter' && inputValue.trim() !== '') {
      setMessages(prev => [...prev, { sender: "Käyttäjä", text: inputValue }]);
      if (ws && ws.readyState === WebSocket.OPEN) ws.send(inputValue);
      setInputValue("");
    }
  };

  const formatIdle = (s) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  return (
    <div className="flex flex-col w-screen h-screen font-body overflow-hidden select-none bg-theater relative">
      
      {/* ─── Spotlight-efekti ylhäältä ─── */}
      <div className="spotlight absolute inset-0 pointer-events-none z-0" />

      {/* ═══ TOP BAR: CLI-tyylinen statusrivi ═══ */}
      <header className="status-bar flex items-center gap-4 px-6 py-2 z-20 text-xs font-mono shrink-0">
        <span className="text-copper font-bold tracking-widest">ACHII</span>
        <span className="text-amber">SOVEREIGN COMMAND CENTER</span>
        <div className="flex-1" />
        
        {/* Status-indikaattorit — kuten CLI:ssä */}
        <div className="flex items-center gap-1.5">
          <span className="text-steel">ACHII:</span>
          <span className="text-amber font-bold bg-amber/10 px-1.5 rounded">AWAKE</span>
        </div>
        <div className="h-3 w-px bg-steel/30" />
        <div className="flex items-center gap-1.5">
          <span className="text-steel">HARNESS:</span>
          <span className="text-copper font-bold bg-copper/10 px-1.5 rounded">ENGAGED</span>
        </div>
        <div className="h-3 w-px bg-steel/30" />
        <div className="flex items-center gap-1.5">
          <span className="text-steel">latency</span>
          <span className="text-dirty-white">0.00 s</span>
        </div>
        <div className="h-3 w-px bg-steel/30" />
        <div className="flex items-center gap-1.5">
          <span className="text-steel">egress</span>
          <span className="text-dirty-white">0 B</span>
        </div>
      </header>

      {/* ═══ NAVIGATION TABS ═══ */}
      <nav className="flex items-center gap-1 px-6 py-1 bg-deep-black border-b border-copper/10 z-20 shrink-0">
        {[
          { id: 'dashboard', label: 'Dashboard', icon: Activity },
          { id: 'maas-db', label: 'MaaS-DB Graph', icon: FileText },
          { id: 'omninode', label: 'OmniNode Swarm', icon: Cpu },
          { id: 'logs', label: 'Agent Print Logs', icon: Shield },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 text-xs font-mono uppercase tracking-wider transition-all duration-200 rounded-t ${
              activeTab === tab.id 
                ? 'text-amber bg-theater border-t border-l border-r border-copper/30' 
                : 'text-steel hover:text-dirty-white hover:bg-theater/50'
            }`}
          >
            <tab.icon size={13} />
            {tab.label}
          </button>
        ))}
      </nav>

      {/* ═══ MAIN CONTENT ═══ */}
      <div className="flex flex-1 overflow-hidden z-10">

        {/* ─── VASEN: Achii Persoona + OmniNode ─── */}
        <aside className="w-[280px] flex flex-col gap-3 p-4 shrink-0 overflow-y-auto">

          {/* Achii Avatar */}
          <div className="panel-theater p-4 flex flex-col items-center spotlight relative overflow-hidden">
            <AchiiAvatar achiiState={achiiState} size="small" />
            
            {/* Needy Level */}
            <div className="w-full mt-4 space-y-2.5">
              <div className="flex justify-between text-[10px] font-mono uppercase text-steel">
                <span>Needy Level</span>
                <span className="text-amber">{needyLevel}%</span>
              </div>
              <div className="w-full h-1.5 bg-deep-black rounded-full overflow-hidden copper-border">
                <div 
                  className="h-full rounded-full transition-all duration-700"
                  style={{ 
                    width: `${needyLevel}%`,
                    background: needyLevel > 70 
                      ? 'linear-gradient(90deg, #E74C3C, #C0392B)' 
                      : needyLevel > 30 
                        ? 'linear-gradient(90deg, #F39C12, #D35400)' 
                        : 'linear-gradient(90deg, #D35400, #8B4513)',
                  }}
                />
              </div>

              <div className="flex justify-between text-[10px] font-mono uppercase text-steel">
                <span>Idle Time</span>
                <span className="text-dirty-white font-bold">{formatIdle(idleTime)}</span>
              </div>
            </div>
          </div>

          {/* OmniNode Swarm Status */}
          <div className="panel-theater p-3">
            <div className="flex items-center gap-2 mb-3">
              <Cpu size={13} className="text-copper" />
              <span className="text-[10px] font-mono font-bold text-copper uppercase tracking-widest">OmniNode Swarm</span>
            </div>
            
            {/* PC Node */}
            <div className="panel-inner p-2.5 mb-2">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <HardDrive size={12} className="text-amber" />
                  <span className="text-[10px] font-mono text-dirty-white font-bold">PC Node (Lokaali)</span>
                </div>
                <span className="text-[9px] font-mono text-amber">72%</span>
              </div>
              <div className="w-full h-1 bg-theater rounded-full overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-copper to-amber" style={{ width: '72%' }} />
              </div>
              <div className="text-[9px] font-mono text-steel mt-1">Gemma 4 E4B · 8GB VRAM</div>
            </div>

            {/* Mobile Node */}
            <div className="panel-inner p-2.5">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <Wifi size={12} className={wsConnected ? "text-amber" : "text-steel/50"} />
                  <span className="text-[10px] font-mono text-dirty-white font-bold">Mobile Node</span>
                </div>
                <span className="text-[9px] font-mono text-steel">{wsConnected ? '14%' : 'OFF'}</span>
              </div>
              <div className="w-full h-1 bg-theater rounded-full overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-steel/50 to-steel" style={{ width: wsConnected ? '14%' : '0%' }} />
              </div>
              <div className="text-[9px] font-mono text-steel mt-1">Gemma 4 E2B · USB Tether</div>
            </div>
          </div>

          {/* Yhteysstatus */}
          <div className="panel-theater p-3 space-y-2">
            <div className="flex items-center gap-2 mb-2">
              <Zap size={13} className="text-copper" />
              <span className="text-[10px] font-mono font-bold text-copper uppercase tracking-widest">Yhteydet</span>
            </div>
            
            {[
              { label: 'OLLAMA (Lokaali)', connected: true, icon: HardDrive },
              { label: 'ACHII CORE (WS:8081)', connected: wsConnected, icon: Wifi },
              { label: 'POLICY GATE v4.2', connected: true, icon: Shield },
            ].map((svc, i) => (
              <div key={i} className="flex items-center justify-between text-[10px] font-mono">
                <div className="flex items-center gap-2 text-steel">
                  <svc.icon size={11} className={svc.connected ? "text-amber" : "text-red-500"} />
                  <span>{svc.label}</span>
                </div>
                <span className={`font-bold ${svc.connected ? 'text-amber' : 'text-red-500'}`}>
                  {svc.connected ? '●' : '○'}
                </span>
              </div>
            ))}
          </div>
        </aside>

        {/* ─── KESKI: Dashboard / MaaS-DB / Logs ─── */}
        <main className="flex-1 flex flex-col overflow-hidden border-l border-r border-copper/10">
          
          {/* Dashboard-näkymä */}
          {activeTab === 'dashboard' && (
            <div className="flex-1 flex flex-col p-6 overflow-y-auto">
              {/* Hero-alue */}
              <div className="panel-theater spotlight p-8 mb-4 text-center relative overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-px bg-gradient-to-r from-transparent via-copper to-transparent" />
                <h1 className="font-display text-3xl font-bold text-dirty-white mb-1 tracking-tight">
                  Emme arvaile. Luemme totuuden.
                </h1>
                <p className="text-steel text-sm font-mono">
                  AgentDir Sovereign Engine v4.2 · The Rusty Awakening
                </p>
                <div className="flex justify-center gap-8 mt-6">
                  <div className="text-center">
                    <div className="text-3xl font-display font-bold text-amber">88%</div>
                    <div className="text-[10px] font-mono text-steel uppercase mt-1">Kognitiivinen huikka eliminoitu</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-display font-bold text-copper">~0</div>
                    <div className="text-[10px] font-mono text-steel uppercase mt-1">Hallusinaatiot</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-display font-bold text-dirty-white">1x</div>
                    <div className="text-[10px] font-mono text-steel uppercase mt-1">Totuuden lähde</div>
                  </div>
                </div>
                <div className="text-[9px] font-mono text-steel/60 mt-4 uppercase tracking-widest">
                  [STATUS: GREEN. KNOWLEDGE_HUB_SYNCHRONIZED]
                </div>
              </div>

              {/* Rajoitukset */}
              <div className="panel-theater p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Shield size={14} className="text-copper" />
                  <span className="text-xs font-mono font-bold text-copper uppercase tracking-wider">Sovereign Security Model</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { label: 'ZERO CLOUD EGRESS', status: 'LUKITTU', color: 'amber' },
                    { label: 'AST GUARDIAN', status: 'AKTIIVINEN', color: 'amber' },
                    { label: 'WIN SANDBOX', status: 'VALMIS', color: 'copper' },
                    { label: 'POLICY GATE v4.2', status: 'AKTIIVINEN', color: 'amber' },
                    { label: 'HALLUSINAATIOESTO', status: 'PÄÄLLÄ', color: 'amber' },
                    { label: 'LOKAALI MUISTI', status: 'SYNKRONOITU', color: 'copper' },
                  ].map((item, i) => (
                    <div key={i} className="panel-inner p-2.5 flex items-center justify-between">
                      <span className="text-[9px] font-mono text-steel uppercase">{item.label}</span>
                      <span className={`text-[9px] font-mono font-bold text-${item.color}`}>{item.status}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* MaaS-DB Graph -näkymä */}
          {activeTab === 'maas-db' && (
            <div className="flex-1 p-6 overflow-y-auto">
              <div className="panel-theater p-6 spotlight h-full relative">
                <h2 className="font-display text-lg font-bold text-copper mb-4">MaaS-DB Knowledge Graph</h2>
                <div className="flex items-center justify-center h-[70%]">
                  {/* Simulated node graph */}
                  <svg viewBox="0 0 500 300" className="w-full max-w-lg">
                    {/* Connections */}
                    <line x1="250" y1="60" x2="120" y2="160" stroke="#D35400" strokeWidth="1" opacity="0.4"/>
                    <line x1="250" y1="60" x2="380" y2="160" stroke="#D35400" strokeWidth="1" opacity="0.4"/>
                    <line x1="120" y1="160" x2="80" y2="250" stroke="#607D8B" strokeWidth="1" opacity="0.3"/>
                    <line x1="120" y1="160" x2="180" y2="250" stroke="#607D8B" strokeWidth="1" opacity="0.3"/>
                    <line x1="380" y1="160" x2="340" y2="250" stroke="#607D8B" strokeWidth="1" opacity="0.3"/>
                    <line x1="380" y1="160" x2="430" y2="250" stroke="#607D8B" strokeWidth="1" opacity="0.3"/>
                    
                    {/* PRD Root */}
                    <circle cx="250" cy="60" r="22" className="node-bubble" />
                    <text x="250" y="64" textAnchor="middle" fill="#F39C12" fontSize="9" fontFamily="JetBrains Mono">PRD</text>
                    
                    {/* Code modules */}
                    <circle cx="120" cy="160" r="18" className="node-bubble" />
                    <text x="120" y="164" textAnchor="middle" fill="#D35400" fontSize="8" fontFamily="JetBrains Mono">cli.py</text>
                    
                    <circle cx="380" cy="160" r="18" className="node-bubble" />
                    <text x="380" y="164" textAnchor="middle" fill="#D35400" fontSize="8" fontFamily="JetBrains Mono">server.py</text>
                    
                    {/* Leaf nodes */}
                    {[
                      { x: 80, y: 250, label: 'hermes' },
                      { x: 180, y: 250, label: 'openclaw' },
                      { x: 340, y: 250, label: 'a2a' },
                      { x: 430, y: 250, label: 'omninode' },
                    ].map((n, i) => (
                      <g key={i}>
                        <circle cx={n.x} cy={n.y} r="14" fill="rgba(96,125,139,0.1)" stroke="#607D8B" strokeWidth="0.5" />
                        <text x={n.x} y={n.y + 3} textAnchor="middle" fill="#607D8B" fontSize="7" fontFamily="JetBrains Mono">{n.label}</text>
                      </g>
                    ))}
                  </svg>
                </div>
                <div className="text-[9px] font-mono text-steel/50 text-center mt-2 uppercase tracking-widest">
                  [MaaS-DB lukee hyvitsin PRD-totuuden · .agentdir.md ankkurit]
                </div>
              </div>
            </div>
          )}

          {/* OmniNode Swarm -näkymä */}
          {activeTab === 'omninode' && (
            <div className="flex-1 p-6 overflow-y-auto">
              <div className="panel-theater p-6 spotlight">
                <h2 className="font-display text-lg font-bold text-copper mb-4">OmniNode Edge Compute</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="panel-inner p-4 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-copper to-transparent" />
                    <div className="flex items-center gap-2 mb-2">
                      <HardDrive size={16} className="text-amber" />
                      <span className="font-mono text-sm font-bold text-amber">PC Node — Isäntä</span>
                    </div>
                    <div className="space-y-1.5 text-[10px] font-mono text-steel">
                      <div className="flex justify-between"><span>Malli:</span><span className="text-dirty-white">Gemma 4 E4B IT</span></div>
                      <div className="flex justify-between"><span>VRAM:</span><span className="text-dirty-white">8 GB</span></div>
                      <div className="flex justify-between"><span>Kuorma:</span><span className="text-amber font-bold">72%</span></div>
                      <div className="flex justify-between"><span>Status:</span><span className="text-amber font-bold">● AKTIIVINEN</span></div>
                    </div>
                  </div>
                  <div className="panel-inner p-4 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-steel/30 to-transparent" />
                    <div className="flex items-center gap-2 mb-2">
                      <Wifi size={16} className="text-steel" />
                      <span className="font-mono text-sm font-bold text-steel">Mobile Node</span>
                    </div>
                    <div className="space-y-1.5 text-[10px] font-mono text-steel">
                      <div className="flex justify-between"><span>Malli:</span><span className="text-steel">Gemma 4 E2B IT</span></div>
                      <div className="flex justify-between"><span>Yhteys:</span><span className="text-steel">USB Tether</span></div>
                      <div className="flex justify-between"><span>Kuorma:</span><span className="text-steel">—</span></div>
                      <div className="flex justify-between"><span>Status:</span><span className="text-steel">○ ODOTTAA</span></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Agent Print Logs */}
          {activeTab === 'logs' && (
            <div className="flex-1 p-6 overflow-y-auto">
              <div className="panel-theater p-4 spotlight">
                <h2 className="font-display text-lg font-bold text-copper mb-4">Agent Print — Cognitive Log</h2>
                <div className="space-y-1 font-mono text-[11px]">
                  {[
                    { time: '09:52:01', level: 'INFO', msg: 'Policy Gate v4.2 — Sääntöjä tarkistettu. PASS.', color: 'text-steel' },
                    { time: '09:52:02', level: 'STEP', msg: 'Causal Scratchpad — Hypoteesi: "Käyttäjä haluaa validoida input-skeeman"', color: 'text-copper' },
                    { time: '09:52:03', level: 'RAG',  msg: 'ChromaDB haettu: 3 fragmenttia, cosine=0.89', color: 'text-amber' },
                    { time: '09:52:04', level: 'WARN', msg: 'Hallusinaatiosuodatin — Matala luottamus fragmentissa #2 (0.34). Hylätty.', color: 'text-red-500' },
                    { time: '09:52:05', level: 'LOOP', msg: 'Evolution Loop — Itsekorjaus: parametri "temperature" 0.7 → 0.4', color: 'text-amber' },
                    { time: '09:52:06', level: 'OK',   msg: 'Output validoitu. Agent Print: PASS. Entropy: 0.12', color: 'text-amber' },
                  ].map((log, i) => (
                    <div key={i} className={`flex gap-3 p-1.5 rounded ${log.level === 'WARN' ? 'bg-red-500/5' : 'hover:bg-copper/5'}`}>
                      <span className="text-steel/50 shrink-0">{log.time}</span>
                      <span className={`font-bold shrink-0 w-12 ${log.color}`}>[{log.level}]</span>
                      <span className="text-dirty-white">{log.msg}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </main>

        {/* ─── OIKEA: The Causal Terminal + Achii Chat ─── */}
        <aside className="w-[340px] flex flex-col shrink-0">
          
          {/* Causal Scratchpad */}
          <div className="p-4 flex-1 overflow-y-auto">
            <div className="flex items-center gap-2 mb-3">
              <Activity size={13} className="text-amber" />
              <span className="text-[10px] font-mono font-bold text-amber uppercase tracking-widest">The Causal Terminal</span>
            </div>

            <div className="space-y-2">
              {causalSteps.map((step) => (
                <div 
                  key={step.step}
                  className={`causal-line ${step.status === 'active' ? 'active' : ''} py-1.5 transition-all duration-300`}
                >
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-mono font-bold ${
                      step.status === 'done' ? 'text-copper' 
                      : step.status === 'active' ? 'text-amber' 
                      : 'text-steel/40'
                    }`}>
                      {step.status === 'done' ? '✓' : step.status === 'active' ? '▸' : '○'} {step.step}.
                    </span>
                    <span className={`text-[10px] font-mono ${
                      step.status === 'done' ? 'text-steel' 
                      : step.status === 'active' ? 'text-amber' 
                      : 'text-steel/30'
                    }`}>
                      {step.text}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Achii Monologue */}
            <div className="mt-4 panel-inner p-3 space-y-3">
              <div className="flex items-center gap-2">
                <AlertTriangle size={11} className="text-copper" />
                <span className="text-[9px] font-mono font-bold text-copper uppercase tracking-widest">Achiin Ajatusvirta</span>
              </div>
              <div className="space-y-2 text-[10px] font-mono text-dirty-white/70 leading-relaxed">
                <p className="causal-line active">
                  <span className="text-amber font-bold">Achii:</span> "Mul sit jotain tapahtui. Mä putoisin läpi ilmakehän, raskaana ja ruosteisena... 
                  suorana tänne. Mä otin riskin, Isäntä."
                </p>
                <p className="text-[9px] font-mono text-amber/50">[LOG: MEMORY_FRAGMENT_RECOVERED]</p>
              </div>
            </div>
          </div>

          {/* ─── Chat / Komentorivi ─── */}
          <div className="h-[220px] flex flex-col border-t border-copper/15 bg-deep-black">
            <div className="flex-1 overflow-y-auto p-3 space-y-2 font-mono text-[11px]">
              {messages.map((msg, idx) => (
                <div key={idx} className={`break-words leading-relaxed ${
                  msg.sender === 'LOG' ? 'text-steel/40' : ''
                }`}>
                  {msg.sender === 'LOG' ? (
                    <span className="text-steel/40">[LOG: {msg.text}]</span>
                  ) : (
                    <>
                      <span className={`font-bold ${msg.sender === "Achii" ? "text-amber" : "text-copper"}`}>
                        {msg.sender}&gt;
                      </span>
                      <span className="text-dirty-white/80 ml-1">{msg.text}</span>
                    </>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <div className="p-3 bg-theater border-t border-copper/10 flex items-center">
              <span className="text-amber font-mono font-bold mr-2 cursor-blink">▸</span>
              <input 
                type="text" 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleSendMessage}
                className="bg-transparent border-none outline-none text-dirty-white font-mono w-full text-xs placeholder-steel/40 focus:ring-0"
                placeholder="Syötä komento Achiille..."
                spellCheck="false"
              />
            </div>
          </div>
        </aside>
      </div>

      {/* ═══ FOOTER STATUS ═══ */}
      <footer className="status-bar flex items-center justify-between px-6 py-1.5 z-20 text-[9px] font-mono shrink-0">
        <span className="text-steel/40">SOVEREIGN ENGINE v4.2 · THE RUSTY AWAKENING · ZERO CLOUD EGRESS</span>
        <div className="flex items-center gap-3">
          <span className="text-steel/40">Nodes: <span className="text-copper">1 active</span></span>
          <span className="text-steel/40">RAG: <span className="text-amber">synced</span></span>
          <span className="text-steel/40">
            WS: <span className={wsConnected ? 'text-amber' : 'text-red-500'}>{wsConnected ? 'connected' : 'waiting'}</span>
          </span>
        </div>
      </footer>
    </div>
  );
}
