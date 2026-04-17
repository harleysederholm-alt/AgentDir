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
  icons: {
    icon: [
      { url: "/achii-wrench.png", type: "image/png" },
    ],
    apple: [{ url: "/achii-wrench.png" }],
    shortcut: ["/achii-wrench.png"],
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
      <body className="min-h-screen bg-base_bg font-body text-ink_soft antialiased">
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
