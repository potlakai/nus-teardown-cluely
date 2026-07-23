# Replication report — Cluely (benchmark #1)

This document is the evidence artifact for the first Nūs // Teardown benchmark.
The pipeline: **analyze the application → identify the differentiator and every
major subsystem → select a public foundation → replicate the complete product,
hardened and verified.** This file records what the analysis found, what the
replication preserves, and what it improved.

## The differentiator

Cluely's visible magic is an overlay window that screen-shares and recordings
cannot see. That is one OS-level call per platform — Electron exposes it as
`setContentProtection(true)` (`WDA_EXCLUDEFROMCAPTURE` on Windows,
`NSWindowSharingNone` on macOS). The standalone mechanic proof lives in
[`nus-teardown/examples/cluely`](https://github.com/potlakai/nus-teardown/tree/main/examples/cluely).

But the mechanic is not the product. The product is the composition of the
subsystems below — which is why this benchmark replicates all of them.

## Subsystem map

| # | Subsystem | What it does | Where |
|---|---|---|---|
| 1 | Invisible overlay | Frameless, transparent, always-on-top window; content protection; click-through empty regions; global shortcuts (`Assist`, `Solve`, quit) | `main.js` |
| 2 | Screen capture | Full-resolution screenshots via `desktopCapturer`, taken only when a feature needs one; held in memory, never written to disk | `src/screen.js` |
| 3 | Audio pipeline | Two isolated channels: mic (`getUserMedia` → 16 kHz PCM) and system-output loopback (`getDisplayMedia`); in-memory WAV wrap; streaming transcription (OpenAI Whisper / Gemini) with per-speaker attribution ("You" / "Them") | `renderer/pcm-processor.js`, `src/wav.js`, `src/stt.js`, `main.js` |
| 4 | LLM answer layer | Provider abstraction over OpenAI, Anthropic, Gemini, Nvidia; streaming responses; prompt library per feature (Assist, What-should-I-say, Follow-ups, Recap, Ask, Solve); optional résumé grounding with prompt-injection guardrails | `src/llm.js`, `src/prompts.js`, `src/profile-context.js` |
| 5 | Settings & key store | Local JSON settings; provider auto-switch; API keys stored encrypted with the OS keychain (DPAPI / Keychain) via `safeStorage` | `src/store.js` |
| 6 | Interface | Glass panel UI, first-run tutorial, settings screen, streaming markdown render, click-through drag regions | `renderer/` |
| 7 | Build & release | `electron-builder` packaging (mac zip / Windows NSIS), tag-triggered matrix CI publishing GitHub Releases | `.github/workflows/release.yml`, `package.json` |

**How they interact:** the audio and screen subsystems feed a rolling
conversation state; feature triggers (hotkeys/buttons) package that state into
provider-specific prompts; responses stream back into the overlay panel.
Invisibility is a property of the window subsystem alone — remove it and the
rest still works, which is exactly what makes it the differentiator and
everything else the commodity 90%.

## What the replication preserves

All seven subsystems, full functionality: three-input capture (screen, mic,
system audio), six AI features with streaming, four LLM providers, onboarding,
settings, global shortcuts, cross-platform window behavior, and the build
pipeline.

## What the replication improved

Hardening applied on top of the foundation:

- **API keys encrypted at rest** with the OS keychain via Electron `safeStorage`
  (the foundation stored them as plaintext JSON), with automatic migration of
  legacy settings files.
- **Renderer sandboxed** (`sandbox: true` alongside the existing
  `contextIsolation` + no `nodeIntegration`).
- **External links validated** — `shell.openExternal` only accepts the macOS
  settings scheme and `https:`; new windows and navigation are denied outright.
- **Electron 33 → 39.8.10**, clearing six high-severity CVEs; **`tar` pinned to
  a patched release** via npm overrides (critical build-chain advisory);
  CI installs with `npm ci` for lockfile integrity.
- Dead configuration removed (unused transcription provider key, stale ignore
  rules).

## Known gaps (kept honest)

- Linux is untested (macOS and Windows supported).
- Builds are unsigned/ad-hoc — first-open workarounds are documented in the
  README.
- Transcription requires an OpenAI key with Whisper access or a Gemini key;
  all AI features are bring-your-own-key.
- Invisibility is best-effort: macOS 15.4+ lets some capture tools ignore
  content protection, and no software flag stops a phone camera.

## Verification

- `npm test` — 3/3 passing (offline, no keys required).
- Boot smoke on Windows 11 with Electron 39.8.10: app launches, overlay
  renders, no errors.
- Fresh-clone install verified end-to-end from the README alone
  (`git clone` → `npm ci` → `npm test` → `npm start`).
