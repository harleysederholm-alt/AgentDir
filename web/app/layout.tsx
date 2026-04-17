import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono, Space_Grotesk } from "next/font/google";
import "./globals.css";

export const viewport: Viewport = {
  themeColor: "#0F0F0F",
  width: "device-width",
  initialScale: 1,
};

const display = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const body = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["400", "500", "600"],
  display: "swap",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  weight: ["400", "500", "600"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://agentdir.achii.dev"),
  title: {
    default: "AgentDir × Achii — Sovereign Engine",
    template: "%s · AgentDir × Achii",
  },
  description:
    "Sovereign Engine for deterministic agentic workflows. Paikallinen, ei-yappauttava kognitiivinen kerros, jossa .yaml on logiikka ja .md on konteksti — kaikki ajettu Gemma 4B:llä NPU:n päällä.",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/achii-wrench.png", type: "image/png", sizes: "512x512" },
      { url: "/icons/icon-192.png", type: "image/png", sizes: "192x192" },
      { url: "/icons/icon-512.png", type: "image/png", sizes: "512x512" },
    ],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180" }],
    shortcut: ["/favicon.ico"],
  },
  appleWebApp: {
    capable: true,
    title: "Achii",
    statusBarStyle: "black-translucent",
  },
  openGraph: {
    title: "AgentDir × Achii — Sovereign Engine",
    description:
      "Harness Engineering suurille kielimalleille: lokaali, deterministinen, ei-vuotava. Rakenna valjaat. Lopeta yappaus.",
    type: "website",
    locale: "fi_FI",
    images: [{ url: "/achii-wrench.png", width: 512, height: 512 }],
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="fi"
      className={`${display.variable} ${body.variable} ${mono.variable}`}
    >
      <head>
        {/* Explicit favicon link — some Vercel/Next combinations skip the
            metadata.icons entry on first paint, so we back it up inline. */}
        <link rel="icon" type="image/png" href="/achii-wrench.png" />
        <link rel="shortcut icon" href="/favicon.ico" />
        {/* Preload the theater-stage background so it renders on first paint
            instead of flashing a flat #0F0F0F panel. */}
        <link
          rel="preload"
          as="image"
          href="/achii-stage.jpg"
          // @ts-expect-error — fetchpriority is not yet in React DOM types.
          fetchpriority="high"
        />
      </head>
      <body className="min-h-screen bg-base_bg font-body text-ink_soft antialiased">
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
