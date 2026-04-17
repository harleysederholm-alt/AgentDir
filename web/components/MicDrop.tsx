import Image from "next/image";
import QRCode from "qrcode";
import { Download, QrCode } from "lucide-react";

const PLATFORMS = [
  {
    platform: "Windows",
    artifact: "AgentDir-1.0.4-beta.msi",
    size: "118 MB",
    arch: "x64 · ARM64",
    note: "NPU-tuki: Snapdragon X Elite & Intel Core Ultra",
  },
  {
    platform: "macOS",
    artifact: "AgentDir-1.0.4-beta.dmg",
    size: "132 MB",
    arch: "Apple Silicon",
    note: "Metal Performance Shaders + Core ML NPU",
  },
  {
    platform: "Linux",
    artifact: "AgentDir-1.0.4-beta.AppImage",
    size: "124 MB",
    arch: "x86_64",
    note: "GTK3 · WebKit2GTK 4.1 · libsoup-3",
  },
  {
    platform: "iOS",
    artifact: "TestFlight build #217",
    size: "— OTA",
    arch: "A17 Pro+",
    note: "Kutsulinkki Builder's Challenge 2026 -arvioijille",
  },
  {
    platform: "Android",
    artifact: "AgentDir-1.0.4-beta.apk",
    size: "64 MB",
    arch: "ARM64 · NPU",
    note: "Tensor G3 / Snapdragon 8 Gen 3 suositus",
  },
];

const DOWNLOAD_URL = "https://agentdir.achii.dev/download";

const RELEASE_NOTES = [
  {
    title: "Harness Core 1.0",
    items: [
      ".yaml-valjaat tukevat meta.determinism: strict -oletusta",
      "JSON Schema -validointi pakollisena jokaiselle step-ulostulolle",
      "egress.allow: [] -oletus; eskalaatio vaatii eksplisiittisen escalate_on-säännön"
    ]
  },
  {
    title: "Gatekeeper Sanitizer",
    items: [
      "Rust-natiivi regex-taulukko 40 API-avainperheelle (AWS, GCP, Stripe, Twilio, …)",
      "VALIDATION_ERROR loggaa diffin ja estää pilvieskalaation auditoitavasti",
      "IPC-capability-taulukko rajaa Tauri-komennot /.achii-juureen"
    ]
  },
  {
    title: "Local Inference",
    items: [
      "Gemma 4B q4_K_M oletuksena, MediaPipe LLM (työpöytä) + MLC LLM (mobile)",
      "NPU-kiihdytys: Snapdragon X Elite, Intel Core Ultra, Apple Neural Engine, Tensor G3",
      "Keskilatenssi 2,5 s · muistikuorma 3,1 GB · akun kulutus 3 W @ mobile"
    ]
  }
];

const KNOWN_ISSUES = [
  "Windows on-ARM64 MSI vaatii WebView2 ≥ 131 (auto-päivitys sisältyy asennukseen)",
  "MLC LLM ei tue vielä GPU-takaisinkytkentää Tensor G3 -piirillä — lämpöleikkaus 46 °C",
  "iOS-testilentokutsut rajoittuvat Builder's Challenge 2026 -arvioijiin huhtikuusta alkaen"
];

async function buildQrSvg(url: string): Promise<string> {
  // Server-side QR generation at build time. No runtime network calls.
  return QRCode.toString(url, {
    type: "svg",
    margin: 0,
    errorCorrectionLevel: "M",
    color: {
      dark: "#0F0F0F",
      light: "#E6E6E6"
    }
  });
}

export async function MicDrop() {
  const qrSvg = await buildQrSvg(DOWNLOAD_URL);
  return (
    <section
      id="lataa"
      className="section-pad relative isolate overflow-hidden border-t border-panel_line py-28 md:py-36"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(70%_50%_at_50%_0%,rgba(211,84,0,0.12),transparent_70%)]"
      />

      <div className="mx-auto max-w-7xl">
        <div className="relative overflow-hidden rounded-2xl border border-panel_line shadow-panel">
          <div className="relative aspect-[21/9] w-full">
            <Image
              src="/images/achii-stage.jpg"
              alt="Builder's Challenge -areena: Achii seisoo ruostuneiden laitteiden keskellä ja valaistu kyltti ilmoittaa Turku, Finland // May 13th."
              fill
              className="object-cover"
              sizes="100vw"
            />
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-base_bg via-base_bg/50 to-transparent" />
          </div>
          <div className="absolute inset-0 flex flex-col justify-end p-8 md:p-14">
            <div className="eyebrow mb-3">{"//"} 07 · The Mic Drop</div>
            <h2 className="max-w-3xl font-display text-4xl font-bold leading-tight tracking-tight text-ink_soft md:text-5xl">
              Ota Achii taskuun.<br />
              <span className="text-accent_amber">Lataa Sovereign Engine v1.0.4-beta.</span>
            </h2>
          </div>
        </div>

        <div className="mt-14 grid gap-10 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="panel flex flex-col items-start gap-6 p-7">
            <div className="eyebrow flex items-center gap-2">
              <QrCode size={13} />
              Skannaa & asenna mobiilidemo
            </div>
            <div
              className="aspect-square w-full max-w-[280px] rounded-lg border border-panel_line bg-ink_soft p-4 [&_svg]:h-full [&_svg]:w-full"
              aria-label={`QR-koodi lataussivulle ${DOWNLOAD_URL}`}
              role="img"
              dangerouslySetInnerHTML={{ __html: qrSvg }}
            />
            <p className="font-body text-[14.5px] leading-relaxed text-ink_soft/70">
              QR vie Builder&apos;s Challenge -demosivulle: valitse TestFlight
              (iOS) tai APK (Android). Mobiili pyörii identtisellä paletilla
              ja samalla Gemma-4B-ytimellä, mutta MLC-runtimella NPU:n päällä.
            </p>
            <a href="/download" className="copper-cta">
              Avaa mobiililataus
              <Download size={16} />
            </a>
          </div>

          <div className="panel overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-panel_deep/60 text-ink_muted">
                <tr className="font-mono text-[11px] uppercase tracking-[0.2em]">
                  <th className="px-5 py-3">Alusta</th>
                  <th className="px-5 py-3">Paketti</th>
                  <th className="hidden px-5 py-3 md:table-cell">Arkki</th>
                  <th className="hidden px-5 py-3 lg:table-cell">Koko</th>
                  <th className="px-5 py-3 text-right">Lataa</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-panel_line">
                {PLATFORMS.map((row) => (
                  <tr
                    key={row.platform}
                    className="align-top transition hover:bg-panel_deep/40"
                  >
                    <td className="px-5 py-4">
                      <div className="font-display text-[15px] font-semibold text-ink_soft">
                        {row.platform}
                      </div>
                      <div className="mt-1 max-w-xs font-body text-[12.5px] leading-snug text-ink_soft/55">
                        {row.note}
                      </div>
                    </td>
                    <td className="px-5 py-4 font-mono text-[12.5px] text-ink_soft/75">
                      {row.artifact}
                    </td>
                    <td className="hidden px-5 py-4 font-mono text-[12.5px] text-ink_muted md:table-cell">
                      {row.arch}
                    </td>
                    <td className="hidden px-5 py-4 font-mono text-[12.5px] text-ink_muted lg:table-cell">
                      {row.size}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <a
                        href="/download"
                        className="inline-flex items-center gap-2 rounded-md border border-panel_line px-3 py-1.5 font-display text-[13px] font-semibold text-ink_soft transition hover:border-accent_amber/70 hover:text-accent_amber"
                      >
                        Lataa
                        <Download size={13} />
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <article className="panel overflow-hidden">
            <header className="flex items-center justify-between border-b border-panel_line bg-panel_deep/40 px-6 py-4">
              <div>
                <div className="eyebrow mb-1">Release notes</div>
                <h3 className="font-display text-lg font-semibold text-ink_soft">
                  v1.0.4-beta &mdash;{" "}
                  <span className="text-accent_amber">The Rusty Awakening</span>
                </h3>
              </div>
              <time
                dateTime="2026-04-17"
                className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted"
              >
                2026-04-17
              </time>
            </header>
            <div className="grid gap-6 p-6 md:grid-cols-3">
              {RELEASE_NOTES.map((block) => (
                <div key={block.title}>
                  <h4 className="font-display text-[13.5px] font-semibold text-accent_amber">
                    {block.title}
                  </h4>
                  <ul className="mt-3 space-y-2 font-body text-[13.5px] leading-relaxed text-ink_soft/75">
                    {block.items.map((item) => (
                      <li key={item} className="flex items-start gap-2">
                        <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-accent_copper" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </article>

          <article className="panel p-6">
            <div className="eyebrow mb-3">Known issues · 1.0.4-beta</div>
            <ul className="space-y-3 font-body text-[13.5px] leading-relaxed text-ink_soft/75">
              {KNOWN_ISSUES.map((issue) => (
                <li key={issue} className="flex items-start gap-2">
                  <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-accent_amber" />
                  <span>{issue}</span>
                </li>
              ))}
            </ul>
            <p className="mt-5 font-mono text-[11px] uppercase tracking-[0.22em] text-ink_muted">
              {"// audit-ketju: /.achii/audit/2026-04.jsonl"}
            </p>
          </article>
        </div>
      </div>
    </section>
  );
}
