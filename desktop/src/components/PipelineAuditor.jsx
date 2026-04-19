import React, { useState, useEffect } from 'react';
import { CheckCircle, Circle, ArrowDown, Shield, FileText, Play, RotateCcw } from 'lucide-react';

const PIPELINE_STEPS = [
  { id: 1, title: 'POLICY GATE: Validointi !_SOVEREIGN.md', desc: 'Achii lukee Zero Cloud Egress -säännöt' },
  { id: 2, title: 'PRD INGESTION: Aegis-vaatimusten luku', desc: 'Ladataan demo_anchor_v1.md vaatimukset muistiin' },
  { id: 3, title: 'CAUSAL HYPOTHESIS: Scratchpad-kirjaus', desc: 'Skenaarion mallinnus: "Miten sanitoin 50,000 riviä vaarantamatta PII-dataa?"' },
  { id: 4, title: 'CONTEXT GATHERING: .agentdir.md ankkurit', desc: 'Haetaan käyttöoikeudet ja lokaalin klusterin tiedot' },
  { id: 5, title: 'MaaS-DB QUERY: V-Index koodigraafi', desc: 'Etsitään aikaisemmat Regex-rutiinit semanttisesta muistista' },
  { id: 6, title: 'MODEL INFERENCE: Gemma 4 / Opus 4.7 reititys', desc: 'Päätös: Delegoidaan rutiinityöt Mobile Nodelle (2B), pidetään syvä konteksti PC Nodella (E4B)' },
  { id: 7, title: 'SEMANTIC GUARDRAIL: PII-tarkistus PRD:tä vasten', desc: 'Varmistetaan ettei datassa siirry mitään kiellettyä edes lähiverkon yli salaamattomana' },
  { id: 8, title: 'SAFE YOLO SANDBOX: Docker-eristetty sanitaatio', desc: 'Suoritetaan datan putsaus eristetyssä lokaalissa kontissa (Sovereign Shield)', icon: Shield },
  { id: 9, title: 'MEMMACHINE COMMIT: Tulosten tallennus', desc: 'Tallennetaan sanitoitu data paikalliseen kantaan' },
  { id: 10, title: 'AGENT PRINT: Auditointiraportin luonti', desc: 'Raportoidaan suorituskykysäästöt ja nollavuodot', icon: FileText },
  { id: 11, title: 'EVOLUTION LOOP: Suorituskyvyn KPI-päivitys', desc: 'Integroidaan uudet opit hermoverkkoon tehokkaampia tulevia ajoja varten' }
];

export default function PipelineAuditor() {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    let timer;
    if (isPlaying && currentStep < PIPELINE_STEPS.length) {
      timer = setTimeout(() => {
        setCurrentStep(s => s + 1);
      }, 1500); // 1.5s per step
    } else if (currentStep >= PIPELINE_STEPS.length) {
      setIsPlaying(false);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, currentStep]);

  const handleNext = () => {
    if (currentStep < PIPELINE_STEPS.length) setCurrentStep(s => s + 1);
  };

  const handleReset = () => {
    setCurrentStep(0);
    setIsPlaying(false);
  };

  const handlePlay = () => {
    if (currentStep >= PIPELINE_STEPS.length) setCurrentStep(0);
    setIsPlaying(true);
  };

  return (
    <div className="panel-theater spotlight p-6 relative overflow-hidden border border-copper/20 mt-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-display text-xl font-bold text-dirty-white flex items-center gap-2">
          <Shield className="text-copper" /> Sovereign Pipeline Auditor
        </h2>
        <div className="flex gap-3">
          <button 
            onClick={isPlaying ? () => setIsPlaying(false) : handlePlay}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-copper/30 text-copper text-[10px] font-mono hover:bg-copper/10 transition-colors uppercase font-bold"
          >
            <Play size={12} /> {isPlaying ? 'Tauko' : 'Automatisoi'}
          </button>
          <button 
            onClick={handleNext}
            disabled={currentStep >= PIPELINE_STEPS.length || isPlaying}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-steel/30 text-steel text-[10px] font-mono hover:bg-steel/10 transition-colors uppercase font-bold disabled:opacity-50"
          >
            Seuraava Vaihe
          </button>
          <button 
            onClick={handleReset}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-steel/30 text-steel text-[10px] font-mono hover:bg-steel/10 transition-colors uppercase font-bold"
          >
            <RotateCcw size={12} /> Nollaa Sykli
          </button>
        </div>
      </div>

      <div className="space-y-0 pl-4 py-2 border-l border-steel/20 ml-4 relative">
        {PIPELINE_STEPS.map((step, index) => {
          const isActive = index === currentStep;
          const isPast = index < currentStep;
          const Icon = step.icon || null;

          return (
            <div key={step.id} className="relative pl-6 pb-6 group">
              {/* Timeline Connector */}
              <div 
                className={`absolute left-[-5px] top-1.5 w-[9px] h-[9px] rounded-full transition-all duration-300 z-10 ${
                  isActive 
                    ? 'bg-amber shadow-[0_0_8px_#F39C12] border-2 border-amber' 
                    : isPast 
                      ? 'bg-copper border-2 border-copper' 
                      : 'bg-transparent border-2 border-steel/50'
                }`} 
              />
              {isPast && index < PIPELINE_STEPS.length - 1 && (
                <div className="absolute left-[-1px] top-3 w-[2px] h-full bg-copper z-0" />
              )}
              {isActive && index < PIPELINE_STEPS.length - 1 && (
                <div className="absolute left-[-1px] top-3 w-[2px] h-full bg-gradient-to-b from-amber to-transparent z-0" /> // Glowing connector
              )}

              <div className={`transition-all duration-300 ${isActive ? 'opacity-100' : isPast ? 'opacity-70' : 'opacity-40'}`}>
                <div className="flex items-center gap-2">
                  <span className={`font-mono text-xs font-bold uppercase ${isActive ? 'text-amber' : isPast ? 'text-copper' : 'text-steel'}`}>
                    Vaihe {step.id}: {step.title}
                  </span>
                  {Icon && isActive && <Icon size={14} className="text-amber animate-pulse" />}
                  {isPast && <CheckCircle size={14} className="text-copper" />}
                </div>
                
                {isActive && (
                  <div className="mt-2 text-[11px] font-mono text-dirty-white bg-black/40 p-3 rounded border border-amber/30 shadow-[0_0_10px_rgba(243,156,18,0.1)] slide-in-from-top-2 animate-in duration-300">
                    {step.desc}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
