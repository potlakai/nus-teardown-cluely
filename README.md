<div align="center">

<img src="docs/logo.png" width="140" alt="Nūs statue logo" />

# nus teardown // cluely

**The complete Cluely, free.** An AI copilot that floats over your screen,
sees what you see, hears both sides of your meetings, and stays out of your
screen shares.

Bring your own AI key — OpenAI · Anthropic · Google Gemini · Nvidia.

</div>

---

> [!IMPORTANT]
> **Honesty up front.** The invisibility is **best-effort, not a guarantee**.
> It relies on an OS window flag that capture tools can choose to respect —
> on macOS 15.4+ some of them don't, Zoom only respects it with one specific
> capture setting (see Setup), and no software flag stops someone pointing a
> phone at your screen. Running a hidden assistant in a **proctored exam, job
> interview, or recorded call** can break platform rules and, in some places,
> consent laws. This is built for your own notes, studying, accessibility, and
> practice. **How you use it is on you.**

---

## Replicated by an agent

This repo is benchmark output. [Nūs // Teardown](https://github.com/potlakai/nus-teardown)
analyzed Cluely end-to-end — its one real differentiator, every subsystem
underneath — and replicated the complete product on a public foundation, then
hardened it. [`REPLICATION.md`](./REPLICATION.md) is the full report: the
subsystem map, what was preserved, what was improved, and what's still missing.

## What it is

A small glass panel that sits above everything on your screen. It works from
**three inputs kept strictly separate** — your screen, your microphone ("You"),
and your meeting's audio ("Them") — so the AI always knows what it's looking
at and *who* said what.

**In a meeting:** ask *"what should I say?"*, get follow-up questions, or recap
the whole conversation with one button.
**On a coding problem:** one hotkey screenshots the problem and returns the
approach, full code, and time/space complexity.
**Anytime:** hit the Assist key about whatever is on your screen, or just type
a question into the box.

A **Smart** toggle in the input box switches between a fast/cheap model and a
smarter/slower one. The panel is transparent and click-through — it never
blocks what's behind it.

## Get it running

### Option A — download the app

Grab the latest zip from [**Releases**](../../releases), unzip, and drag the
app into Applications. The build is intentionally unsigned (no paid Apple
certificate), so on first open: **right-click → Open → Open**. If macOS calls
it *"damaged and can't be opened"*, run this once in Terminal, then open it
again:

```bash
xattr -cr /Applications/Nūs.app
```

### Option B — from source

You need [Node.js](https://nodejs.org) 18+. Nothing else.

```bash
git clone https://github.com/potlakai/nus-teardown-cluely.git
cd nus-teardown-cluely
npm install
npm start
```

Package your own copy with `npm run pack`. One quirk worth knowing: ad-hoc
builds change the app's identity, so **macOS permissions reset when you
rebuild** — grant them once, keep the build.

## Setup — the three things it needs

1. **Two macOS permissions**, granted on first use (or manually under
   System Settings → Privacy & Security): **Microphone**, and **Screen
   Recording** — that single Screen Recording grant covers both screenshots
   *and* meeting audio. Let the app restart if macOS asks.
   **On Windows there is nothing to grant** — screen capture and the mic work
   out of the box.
2. **Your own AI key** (Settings → the `...` button, or `⌘` `,`). Keys are
   stored **only on your machine, encrypted with your OS keychain**, and sent
   only to the provider you picked. There is no server and nothing is
   collected.

   | Provider | Where to get one | Worth knowing |
   |---|---|---|
   | **OpenAI** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | Does everything — but *listening* needs a key with **Whisper/audio** access; chat-only restricted keys 403 on transcription |
   | **Anthropic** | [console.anthropic.com](https://console.anthropic.com) | Strong on screen/coding help; no speech-to-text, so pair it with OpenAI or Gemini for listening |
   | **Google Gemini** | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | One key covers chat + transcription |
   | **Nvidia** | [build.nvidia.com](https://build.nvidia.com) | Vision-capable Llama models |

3. **One Zoom setting — only if you use Zoom.** Meet, Teams, and QuickTime
   need nothing. Zoom: **Settings → Share Screen → Advanced → Screen capture
   mode → "Advanced capture *with* window filtering."** The *"without window
   filtering"* modes grab the raw screen and **will** show the overlay.

   <img src="docs/zoom-capture-mode.png" width="520" alt="Zoom screen capture mode set to Advanced capture with window filtering" />

## Driving it

- **`⌘` `↵`** — Assist: the do-the-smart-thing key (rebindable in Settings).
- **`⌘` `H`** — solve the coding problem on screen.
- **The `▢` button** — start/stop listening to the meeting (green dot = live).
- **Type + `↵`** — ask anything about your screen or the conversation.
- **Hide** collapses to the top bar; drag by the pill; quit with **`⌘` `⇧` `X`**.
- Click the **statue logo** anytime to reopen the first-run guide.

## What's inside

An [Electron](https://www.electronjs.org/) app. Everything is local except the
calls to your chosen AI provider.

- **Screen** — full-resolution captures via `desktopCapturer`, taken only when
  a feature asks for one. Held in memory, never written to disk.
- **You** — mic audio, downsampled to 16 kHz, streamed to transcription.
- **Them** — system-output loopback capture on its own channel, so speaker
  attribution stays clean.

Both audio channels transcribe (OpenAI Whisper or Gemini) and flow, with an
optional screenshot, into your model. Answers **stream** into the panel.

**The invisibility everyone talks about** is one window flag:
`setContentProtection(true)` — `WDA_EXCLUDEFROMCAPTURE` on Windows,
`NSWindowSharingNone` on macOS. Same mechanism DRM players and Zoom's own
toolbar use; not a GPU trick, and best-effort per the disclaimer above. The
standalone proof of just this mechanic lives in
[`nus-teardown/examples/cluely`](https://github.com/potlakai/nus-teardown/tree/main/examples/cluely).

```
main process ──┬─ overlay window (frameless, transparent, always-on-top, content-protected)
               ├─ screenshot capture (desktopCapturer)
               ├─ speech-to-text (Whisper / Gemini)      ── "You" + "Them" channels
               └─ LLM streaming (OpenAI / Anthropic / Gemini / Nvidia)
renderer ──────┴─ the glass UI + mic capture + system-audio loopback
```

## When something doesn't work

**Permissions look granted but the app disagrees** — you approved an older
build. Ad-hoc signing changes the app's identity on rebuild, so toggle the
permission off and on, or remove and re-add the app, in System Settings.

**"403" or "no access to model"** — your key is restricted. The classic case:
an OpenAI project key limited to chat models works for screen help but 403s on
Whisper. Enable audio on the key, use an unrestricted one, or add a Gemini key
(it's the automatic transcription fallback).

**Listening produces no transcript** — confirm you have a transcription-capable
key (OpenAI-with-Whisper or Gemini) in Settings, and that Screen Recording is
granted (meeting audio needs it).

**It shows up in a Zoom share** — the Zoom setting above is wrong or you're on
a capture mode that ignores the flag. And per the disclaimer: best-effort.

**"Damaged and can't be opened"** — the `xattr -cr` one-liner in Option A.

## Privacy

- No accounts, no servers, no telemetry. The app collects nothing.
- API keys live in one local file, encrypted with your OS keychain (DPAPI on
  Windows, Keychain on macOS), and go only to the provider you chose.
- Screenshots and audio leave the machine only when you run a feature, and
  only to your provider. The transcript lives in memory and dies when you quit.

## Hacking on it

Issues and PRs welcome. Deliberately small and readable: `main.js` (app,
capture, AI), `renderer/` (UI), `src/` (providers and pipeline). Plain
HTML/CSS/JS, no build step for the source. `npm test` runs the suite offline.

**Platform support:** macOS ✅ · Windows ✅ · Linux (untested)

**Open for contribution:** lower-latency streaming audio pipeline · optional
Deepgram transcription.

## Credits & license

Built as an open-source study of how tools like **Cluely** and **Interview
Coder** work. Modeled on the open-source clones `pickle-com/glass` and
`sohzm/cheating-daddy`.

**License: [GPL-3.0-or-later](LICENSE).**
