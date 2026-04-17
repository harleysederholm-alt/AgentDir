# AgentDir × Achii — Mobile Edge AI Demo

React Native + Expo client for the Builder's Challenge pitch. Ships the
`AchiiMobileApp` with:

- Strict AgentDir design tokens (shared with the desktop shell).
- Haptic feedback playbook (`mechanicalClick` on press, `mechanicalDing`
  on inference success, `mechanicalError` on failure).
- Event-driven status indicator — no decorative loops. The pulse ring only
  runs while `status === "PROCESSING"`.
- Local inference adapter stub ready to be swapped for MediaPipe LLM /
  MLC LLM (Gemma 2B on NPU).

## Getting started

```bash
cd mobile
npm install
npm run start      # Expo dev server
npm run typecheck  # strict TS
```

## Architecture notes

- `src/lib/haptics.ts` uses Expo Haptics on native and falls back to
  `navigator.vibrate([10, 30, 10])` / `navigator.vibrate(50)` on web, which
  matches the pattern documented in the pitch context.
- `src/lib/localInference.ts` holds the swap-point for the real NPU model.
  The UI contract never changes — only the inside of `runLocalHarness`.
- `src/components/AchiiStatusIndicator.tsx` is the mobile analogue of the
  desktop `AchiiCanvas`; it carries the same "no infinite loops" rule and
  only animates while `PROCESSING`.
