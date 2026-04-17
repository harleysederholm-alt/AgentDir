import { useCallback, useState } from "react";
import { NexusChat } from "@/components/NexusChat";
import { OriginStory } from "@/components/OriginStory";
import { STORY_SEEN_KEY } from "@/origin_story";

type Phase = "onboarding" | "nexus";

function readSeen(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return window.localStorage.getItem(STORY_SEEN_KEY) === "1";
  } catch {
    return false;
  }
}

function writeSeen(): void {
  try {
    window.localStorage.setItem(STORY_SEEN_KEY, "1");
  } catch {
    /* private mode / storage disabled — skip silently */
  }
}

export default function App() {
  // Lazy initializer — read localStorage synchronously on first render so the
  // returning user never sees a flash of the onboarding shell.
  const [phase, setPhase] = useState<Phase>(() =>
    readSeen() ? "nexus" : "onboarding",
  );

  const handleEngage = useCallback(() => {
    writeSeen();
    setPhase("nexus");
  }, []);

  if (phase === "onboarding") {
    return <OriginStory onEngage={handleEngage} />;
  }

  return <NexusChat />;
}
