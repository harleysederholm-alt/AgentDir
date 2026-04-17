/**
 * Local inference adapter.
 *
 * At pitch time this file will be swapped for a native MediaPipe LLM or
 * MLC LLM binding (Gemma 2B on NPU). For now we expose the minimal async
 * contract the UI binds against — a single `runLocalHarness` function
 * that returns the YAML-shaped summary.
 *
 * The implementation intentionally does not stream — the UI state machine
 * assumes an all-or-nothing resolution so the haptic feedback lines up
 * with a single "done" event.
 */

export interface InferenceResult {
  summary: string;
  ms: number;
  model: string;
}

const DEMO_DELAY_MS = 2500;

const DEMO_SUMMARY = `- Tekoälyn hallusinaatiot johtuvat liiallisesta vapaudesta.
- AgentDir × Achii erottaa logiikan (.yaml) ja kontekstin (.md).
- Sovereign Engine toimii lokaalisti ja pitää pilvimallit kurissa.`;

export async function runLocalHarness(input: string): Promise<InferenceResult> {
  const start = Date.now();
  if (!input.trim()) {
    throw new Error("Syöte on tyhjä — anna Achiille tekstiä pureksittavaksi.");
  }

  // Deterministic demo latency. Replace with a real MediaPipe call later —
  // the UI contract does not change.
  await new Promise((resolve) => setTimeout(resolve, DEMO_DELAY_MS));

  return {
    summary: DEMO_SUMMARY,
    ms: Date.now() - start,
    model: "gemma-2b · stub",
  };
}
