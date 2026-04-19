import React, { useState } from 'react';

/**
 * ScippyUI - Front-end interface for AgentDir Sovereign Engine v4.0.
 * Design style: "Light Minimalist Classy"
 * Background: Paper White (#F9FAFB)
 * Accent: Muted Teal (#00C2A8)
 */
export default function ScippyUI() {
  const [pipelineLogs, setPipelineLogs] = useState([
    "> Järjestelmä alustettu. MaaS-DB kytköksessä.",
    "> OmniNode Router aktiivinen (Mobiili-Ingest tila valmiustilassa).",
    "> Achii Beacon odottaa syötettä..."
  ]);
  const [inputValue, setInputValue] = useState("");

  const handleSimulateMission = (e) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      setPipelineLogs(prev => [
        ...prev, 
        `> Suoritetaan tehtävää: ${inputValue}`,
        "> [Vaihe 1/10] Policy Gate läpäisty.",
        "> [Vaihe 4/10] MaaS-DB Query... V-Index verifioitu."
      ]);
      setInputValue("");
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#F9FAFB] text-gray-800 font-sans antialiased">
      
      {/* Sivuvalikko */}
      <aside className="w-72 bg-white border-r border-gray-100 flex flex-col p-6 shadow-sm z-10 transition-all duration-300">
        <div className="mb-10">
          <h1 className="text-2xl font-semibold tracking-tight text-[#00C2A8]">
            AgentDir <span className="font-light text-gray-400">v4.0</span>
          </h1>
          <p className="text-xs text-gray-400 mt-1 uppercase tracking-widest font-semibold">Sovereign Engine</p>
        </div>
        
        <nav className="flex-1 space-y-3">
          <button className="w-full text-left px-5 py-3 font-medium bg-[#00C2A8] text-white rounded-lg shadow-sm shadow-[#00C2A8]/30 transition-transform active:scale-95">
            Mission Terminal
          </button>
          <button className="w-full text-left px-5 py-3 font-medium text-gray-500 hover:bg-gray-50 hover:text-gray-800 rounded-lg transition-colors">
            Knowledge Web (V-Index)
          </button>
          <button className="w-full text-left px-5 py-3 font-medium text-gray-500 hover:bg-gray-50 hover:text-gray-800 rounded-lg transition-colors">
            OmniNode Router
          </button>
        </nav>
        
        <div className="mt-auto px-2">
          <div className="flex items-center space-x-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00C2A8] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#00C2A8]"></span>
            </span>
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">MaaS-DB Online</span>
          </div>
        </div>
      </aside>

      {/* Pääosio */}
      <main className="flex-1 flex flex-col p-10 overflow-hidden relative">
        
        {/* Achii Beacon (Geo Assistant) */}
        <section className="flex items-center justify-between mb-8 bg-white p-6 rounded-2xl shadow-sm border border-gray-100/60 backdrop-blur-sm z-10">
          <div className="flex flex-col">
            <h2 className="text-xl font-bold text-gray-800 tracking-tight">Achii Beacon</h2>
            <p className="text-sm text-gray-500 mt-1">Proactive Cognitive Assistant valvoo putkea.</p>
          </div>
          
          <div className="w-16 h-16 relative flex items-center justify-center">
            <div className={`absolute w-full h-full border-2 border-[#00C2A8] rounded-full animate-ping opacity-20`}></div>
            <div className={`absolute w-12 h-12 border border-[#00C2A8] rounded-full animate-spin-slow opacity-40`}></div>
            <div className={`w-6 h-6 bg-[#00C2A8] rotate-45 transform shadow-lg shadow-[#00C2A8]/50 rounded-sm`}></div>
          </div>
        </section>

        {/* Mission Status Terminal */}
        <section className="flex-1 bg-[#111827] rounded-2xl p-6 shadow-2xl flex flex-col border border-gray-800 relative overflow-hidden group">
          <div className="flex items-center mb-6 border-b border-gray-800 pb-4">
            <div className="flex space-x-2 mr-6">
              <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
            </div>
            <span className="text-gray-400 text-xs font-mono tracking-widest uppercase opacity-70">
              Terminal // 10-Step Cognitive Pipeline
            </span>
          </div>
          
          <div className="flex-1 overflow-y-auto space-y-3 font-mono text-[13px] text-gray-300 scrollbar-hide">
            {pipelineLogs.map((log, index) => (
              <div key={index} className="opacity-90 hover:opacity-100 hover:text-white transition-opacity">
                {log}
              </div>
            ))}
          </div>
          
          <div className="mt-4 flex items-center border-t border-gray-800 pt-5 relative">
            <span className="text-[#00C2A8] font-mono mr-3 text-lg">❯</span>
            <input 
              type="text" 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleSimulateMission}
              className="bg-transparent border-none outline-none text-gray-200 font-mono w-full placeholder-gray-600 focus:ring-0"
              placeholder="Anna tehtävä laukaistaksesi pipelinen (paina Enter)..."
              spellCheck="false"
            />
          </div>
        </section>
        
      </main>
    </div>
  );
}
