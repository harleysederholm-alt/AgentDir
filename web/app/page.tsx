import { BuildersChallenge } from "@/components/BuildersChallenge";
import { Footer } from "@/components/Footer";
import { HarnessSpec } from "@/components/HarnessSpec";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { KnowledgeHub } from "@/components/KnowledgeHub";
import { MicDrop } from "@/components/MicDrop";
import { Philosophy } from "@/components/Philosophy";
import { SoulOfAchii } from "@/components/SoulOfAchii";
import { VideoShowcase } from "@/components/VideoShowcase";

export default function Page() {
  return (
    <>
      <Header />
      <main className="relative">
        <Hero />
        <Philosophy />
        <VideoShowcase />
        <SoulOfAchii />
        <HarnessSpec />
        <KnowledgeHub />
        <BuildersChallenge />
        <MicDrop />
      </main>
      <Footer />
    </>
  );
}
