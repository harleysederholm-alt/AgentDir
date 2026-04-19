import React, { useState, useEffect } from 'react';
import { Shield, Zap, Cpu, Server, Smartphone, CheckCircle, Lock } from 'lucide-react';
import PipelineAuditor from './PipelineAuditor';

export default function AegisSimulator() {
  const [dataVolume, setDataVolume] = useState(1000);
  const [a2aEnabled, setA2aEnabled] = useState(false);
  const [status, setStatus] = useState('Odottaa käynnistystä');
  const [progress, setProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [timeSaved, setTimeSaved] = useState(0);

  useEffect(() => {
    let timer;
    if (isProcessing && progress < 100) {
      const baseSpeed = 10;
      const speedMultiplier = a2aEnabled ? 1.8 : 1.0;
      const step = (baseSpeed * speedMultiplier) / (dataVolume / 100);

      timer = setTimeout(() => {
        setProgress(p => Math.min(p + step, 100));
      }, 50);
    } else if (progress >= 100 && isProcessing) {
      setIsProcessing(false);
      setStatus('Valmis — PII-data sanitoitu');
      if (a2aEnabled) setTimeSaved(44); // Esimerkiksi 44% säästö
    }
    return () => clearTimeout(timer);
  }, [progress, isProcessing, a2aEnabled, dataVolume]);

  const handleStart = () => {
    setProgress(0);
    setTimeSaved(0);
    setIsProcessing(true);
    setStatus('Sanitoidaan lokaalisti...');
  };

  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <div className="panel-theater spotlight p-6 relative overflow-hidden border border-copper/20">
        
        {/* Sovereign Shield Indikaattori */}
        <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1 bg-amber/10 border border-amber/30 rounded-full">
          <Lock size={12} className="text-amber" />
          <span className="text-[10px] font-mono text-amber uppercase font-bold tracking-widest">Sovereign Shield Active</span>
        </div>

        <h2 className="font-display text-xl font-bold text-dirty-white mb-6 flex items-center gap-2">
          <Shield className="text-copper" /> Project Aegis — PII Sanitation
        </h2>

        {/* Kontrollit */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-mono text-steel uppercase mb-2">Datamäärä (Riviä): {dataVolume}</label>
              <input 
                type="range" 
                min="100" 
                max="5000" 
                step="100"
                value={dataVolume} 
                onChange={e => setDataVolume(Number(e.target.value))}
                disabled={isProcessing}
                className="w-full accent-copper"
              />
            </div>
            
            <div className="flex items-center gap-3 bg-black/40 p-3 rounded border border-steel/20">
              <input 
                type="checkbox" 
                id="a2aToggle"
                checked={a2aEnabled}
                onChange={e => setA2aEnabled(e.target.checked)}
                disabled={isProcessing}
                className="accent-copper w-4 h-4 cursor-pointer"
              />
              <label htmlFor="a2aToggle" className="text-sm font-mono text-dirty-white cursor-pointer flex-1">
                Aktivoi OmniNode Swarm (A2A)
              </label>
              {a2aEnabled && <Zap size={14} className="text-amber animate-pulse" />}
            </div>

            <button 
              onClick={handleStart}
              disabled={isProcessing}
              className={`w-full py-3 rounded font-mono font-bold text-xs uppercase tracking-widest transition-all ${
                isProcessing 
                  ? 'bg-steel/10 text-steel/50 cursor-not-allowed' 
                  : 'bg-copper/20 text-copper hover:bg-copper/30 border border-copper/50'
              }`}
            >
              {isProcessing ? 'Suoritetaan...' : 'Käynnistä Sanitaatio'}
            </button>
          </div>

          {/* Mittaristot */}
          <div className="flex flex-col justify-center space-y-4">
            <div className="bg-black/40 p-4 rounded border border-steel/20">
              <div className="text-xs font-mono text-steel uppercase mb-1">Status</div>
              <div className="text-sm font-mono text-dirty-white">{status}</div>
              
              {/* Edistymispalkki */}
              <div className="mt-3 w-full h-2 bg-steel/20 rounded overflow-hidden">
                <div 
                  className="h-full bg-copper transition-all duration-100 ease-linear shadow-[0_0_8px_#D35400]" 
                  style={{ width: `${progress}%` }} 
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-black/40 p-3 rounded border border-steel/20 flex flex-col items-center justify-center">
                <span className="text-[10px] font-mono text-steel uppercase mb-1">Aikaa Säästetty</span>
                <span className="text-xl font-bold font-mono text-amber">{timeSaved}%</span>
              </div>
              <div className="bg-black/40 p-3 rounded border border-steel/20 flex flex-col items-center justify-center">
                <span className="text-[10px] font-mono text-steel uppercase mb-1">Pilvivuodot</span>
                <span className="text-xl font-bold font-mono text-dirty-white">0 Tavua</span>
              </div>
            </div>
          </div>
        </div>

        {/* OmniNode Swarm Visualisointi */}
        <div className="relative pt-6 border-t border-steel/20">
          <h3 className="text-xs font-mono text-steel uppercase tracking-widest absolute -top-2 left-1/2 -translate-x-1/2 bg-[#111111] px-2">
            Compute Topology
          </h3>
          
          <div className="flex justify-between items-center px-12 mt-4">
            {/* PC Node */}
            <div className={`flex flex-col items-center p-4 rounded-xl border ${
              isProcessing ? 'border-amber/50 bg-amber/5' : 'border-steel/20 opacity-50'
            } transition-all duration-300 w-32`}>
              <Server size={32} className={isProcessing ? 'text-amber animate-pulse' : 'text-steel'} />
              <div className="mt-2 text-[10px] font-mono font-bold text-dirty-white">PC Node</div>
              <div className="text-[8px] font-mono text-steel">Gemma 4 E4B</div>
              <div className="text-[8px] font-mono text-copper mt-1">Kontekstuaalinen Sanitaatio</div>
            </div>

            {/* Virtaus putki */}
            <div className="flex-1 h-px bg-steel/30 relative mx-4">
              {isProcessing && a2aEnabled && (
                <div className="absolute top-1/2 left-0 w-full flex justify-center">
                   {/* Datan vilinä particles */}
                   <div className="w-full relative opacity-50 h-[2px]">
                      <div className="absolute left-0 top-0 h-full bg-amber w-[20%] animate-[slide_1s_linear_infinite]" />
                      <div className="absolute left-[40%] top-0 h-full bg-amber w-[15%] animate-[slide_1.5s_linear_infinite]" />
                   </div>
                </div>
              )}
            </div>

            {/* Mobile Node */}
            <div className={`flex flex-col items-center p-4 rounded-xl border ${
              (isProcessing && a2aEnabled) ? 'border-amber/50 bg-amber/5' : 'border-steel/20 opacity-30'
            } transition-all duration-300 w-32`}>
              <Smartphone size={32} className={(isProcessing && a2aEnabled) ? 'text-amber animate-pulse' : 'text-steel'} />
              <div className="mt-2 text-[10px] font-mono font-bold text-dirty-white">Mobile Node</div>
              <div className="text-[8px] font-mono text-steel">Gemma 4 2B (A2A)</div>
              <div className="text-[8px] font-mono text-copper mt-1">Regex Validointi</div>
            </div>
          </div>
        </div>

        {/* Agent Print */}
        {progress === 100 && (
          <div className="mt-6 p-4 rounded bg-copper/10 border border-copper/30 flex items-start gap-4 animate-in fade-in slide-in-from-bottom-2">
             <CheckCircle className="text-copper shrink-0 mt-0.5" />
             <div className="space-y-1">
               <div className="text-xs font-mono font-bold text-copper uppercase">Agent Print — Success</div>
               <div className="text-[10px] font-mono text-dirty-white leading-relaxed">
                 "[REPORT] Sanitaatio valmis. {dataVolume} tietuetta käsitelty.{' '}
                 {a2aEnabled 
                    ? 'A2A-delegaatio aktivoitu: Mobile Node suoritti 42% rutiiniajosta. Kuorman purku säästi 44% kokonaisajasta.' 
                    : 'Yksittäissolmuajo suoritettu PC:llä. Suurin kuormituspiikki 82% VRAM.'
                 } Nolla tavua siirretty avoimeen verkkoon. Sovereign State: Vihreä."
               </div>
             </div>
          </div>
        )}

      </div>
      
      {/* 11-step Pipeline Auditor */}
      <PipelineAuditor />
    </div>
  );
}
