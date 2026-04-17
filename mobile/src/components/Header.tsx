import { WrenchEye } from "@/components/WrenchEye";

export function Header() {
  return (
    <header className="sticky top-0 z-40">
      <div className="relative">
        <div className="header-banner" aria-hidden="true" />
        <div className="absolute inset-x-0 top-0 flex items-center justify-between px-5 pt-5">
          <div className="flex items-center gap-3">
            <div className="grid h-9 w-9 place-items-center rounded-lg border border-accent_amber/25 bg-base_bg/60 shadow-amber backdrop-blur-md">
              <WrenchEye className="h-6 w-6" />
            </div>
            <div className="leading-tight">
              <div className="font-mono text-[10.5px] uppercase tracking-[0.22em] text-accent_amber/85">
                AgentDir × Achii
              </div>
              <div className="font-mono text-[10px] tracking-[0.18em] text-ink_muted">
                sovereign engine · v1.0.4-beta
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-panel_line bg-base_bg/60 px-3 py-1.5 backdrop-blur-md">
            <span className="status-dot animate-pulse-amber" />
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink_soft">
              lokaali · valmis
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
