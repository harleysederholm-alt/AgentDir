"use client";

import { useCallback, useEffect, useState } from "react";
import { NexusChat } from "@/components/NexusChat";
import { OriginStory } from "@/components/OriginStory";
import { STORY_SEEN_KEY } from "@/lib/origin_story";

type Phase = "boot" | "onboarding" | "nexus";

/**
 * Achii PWA surface. Mirrors the mobile/ Vite bundle so the whole flow
 * (origin story → gate → NexusChat) ships from the same Vercel deploy
 * as the landing page. Everything is wrapped in `.achii-pwa` so its
 * scoped component styles never leak into the marketing site.
 */
export default function AppPage() {
  const [phase, setPhase] = useState<Phase>("boot");

  useEffect(() => {
    try {
      const seen = window.localStorage.getItem(STORY_SEEN_KEY);
      setPhase(seen === "1" ? "nexus" : "onboarding");
    } catch {
      setPhase("onboarding");
    }
  }, []);

  const handleEngage = useCallback(() => {
    try {
      window.localStorage.setItem(STORY_SEEN_KEY, "1");
    } catch {
      /* private mode — fall through */
    }
    setPhase("nexus");
  }, []);

  if (phase === "boot") {
    // Avoid hydration flash of the wrong phase — render nothing on first paint.
    return <div className="achii-pwa" />;
  }

  return (
    <div className="achii-pwa">
      {phase === "onboarding" ? (
        <OriginStory onEngage={handleEngage} />
      ) : (
        <NexusChat />
      )}
    </div>
  );
}
