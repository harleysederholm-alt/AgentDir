import type { Metadata, Viewport } from "next";

export const viewport: Viewport = {
  themeColor: "#0F0F0F",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

export const metadata: Metadata = {
  title: "Achii · Sovereign Engine",
  description:
    "Achiin paikallinen chat-kuori — Gemma 4B NPU:lla, ei pilviegressiä. Asenna puhelimen Add to Home Screen -toiminnolla.",
  manifest: "/manifest.webmanifest",
  appleWebApp: {
    capable: true,
    title: "Achii",
    statusBarStyle: "black-translucent",
  },
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
