"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AchiiLogo } from "./AchiiLogo";

const NAV = [
  { href: "#filosofia", label: "Mitä tämä on?" },
  { href: "#spec", label: "Harness Engineering" },
  { href: "#sielu", label: "Achiin sielu" },
  { href: "#tieto", label: "Dokumentaatio" },
  { href: "#areena", label: "Ota yhteyttä" },
] as const;

export function Header() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-colors duration-300 ${
        scrolled
          ? "border-b border-panel_line bg-base_bg/80 backdrop-blur-md"
          : "border-b border-transparent"
      }`}
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-6 py-4 md:px-10 lg:px-16 xl:px-20">
        <Link href="/" className="group flex items-center gap-3">
          <AchiiLogo size={32} className="transition-transform group-hover:rotate-[-6deg]" />
          <div className="hidden flex-col leading-none md:flex">
            <span className="font-display text-sm font-semibold tracking-[0.22em] text-ink_soft">
              AGENTDIR
            </span>
            <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-ink_muted">
              × achii · sovereign engine
            </span>
          </div>
        </Link>

        <ul className="hidden items-center gap-7 lg:flex">
          {NAV.map((item) => (
            <li key={item.href}>
              <a
                href={item.href}
                className="group relative font-display text-sm font-medium tracking-wide text-ink_soft/80 transition hover:text-ink_soft"
              >
                {item.label}
                <span className="absolute -bottom-1.5 left-0 h-[1.5px] w-0 bg-accent_amber transition-all duration-300 group-hover:w-full" />
              </a>
            </li>
          ))}
        </ul>

        <div className="hidden items-center gap-3 md:flex">
          <a
            href="/app/"
            className="ghost-cta"
            aria-label="Avaa Achii-chat-PWA"
          >
            Avaa Achii
          </a>
          <a href="#lataa" className="copper-cta">
            Asenna / lataa
          </a>
        </div>
      </nav>
    </header>
  );
}
