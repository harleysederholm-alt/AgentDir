import { Footer } from "@/components/Footer";
import { HarnessSpec } from "@/components/HarnessSpec";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { KnowledgeHub } from "@/components/KnowledgeHub";
import { MicDrop } from "@/components/MicDrop";
import { SoulOfAchii } from "@/components/SoulOfAchii";
import { VideoShowcase } from "@/components/VideoShowcase";

export default function Page() {
  return (
    <>
      <Header />
      <main className="relative">
        <Hero />
        <VideoShowcase />
        <SoulOfAchii />
        <HarnessSpec />
        <KnowledgeHub />
        <MicDrop />
      </main>
      <Footer />
    </>
  );
}
