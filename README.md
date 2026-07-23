<div align="center">

<img src="docs/logo.png" width="140" alt="Nūs statue logo" />

# nus teardown // cluely

**The complete Cluely, free.** An AI copilot that floats over your screen,
sees what you see, hears both sides of your meetings, and stays out of your
screen shares.

Bring your own AI key: OpenAI, Anthropic, Google Gemini, or Nvidia.

</div>

---

> [!IMPORTANT]
> **Honesty up front.** The invisibility is **best-effort, not a guarantee.**
> It relies on an OS window flag that capture tools can choose to respect. On
> macOS 15.4+ some of them don't, Zoom only respects it with one specific
> capture setting (see [Setup](#setup)), and no software flag stops someone
> pointing a phone at your screen. Running a hidden assistant in a **proctored
> exam, job interview, or recorded call** can break platform rules and, in
> some places, consent laws. This is built for your own notes, studying,
> accessibility, and practice. **How you use it is on you.**

---

## Replicated by an agent

This repo is benchmark output. [Nūs // Teardown](https://github.com/potlakai/nus-teardown)
analyzed Cluely end to end, mapped its one real differentiator and every
subsystem underneath, replicated the complete product on a public foundation,
then hardened it. [`REPLICATION.md`](./REPLICATION.md) is the full report: the
subsystem map, what was preserved, what was improved, and what is still missing.

## What it is

A small glass panel that sits above everything on your screen. It works from
**three inputs kept strictly separate:** your screen, your microphone ("You"),
and your meeting's audio ("Them"). So the AI always knows what it is looking
at and *who* said what.

- **In a meeting:** ask *"what should I say?"*, get follow-up questions, or
  recap the whole conversation with one button.
- **On a coding problem:** one hotkey screenshots the problem and returns the
  approach, full code, and time/space complexity.
- **Anytime:** hit the Assist key about whatever is on your screen, or type a
  question into the box.

A **Smart** toggle in the input box switches between a fast, cheap model and a
smarter, slower one. The panel is transparent and click-through, so it never
blocks what is behind it.

## Quick start (from source)

You need [Node.js](https://nodejs.org) 18 or newer. Nothing else.

```bash
git clone https://github.com/potlakai/nus-teardown-cluely.git
cd nus-teardown-cluely
npm install
npm start
```

On first launch the app asks for permissions and an AI key. See
[Setup](#setup) below. That is the whole install.

## Get the prebuilt app

Prefer a download? Grab the latest zip from [**Releases**](../../releases),
unzip, and drag the app into Applications.

The build is intentionally unsigned (no paid Apple certificate), so on first
open: **right-click the app, choose Open, then Open again.** If macOS says the
app is *"damaged and can't be opened,"* clear the quarantine flag once, then
reopen:

```bash
xattr -cr /Applications/Nūs.app
```

### Build your own release

```bash
npm run dist        # macOS .zip in dist/
npm run dist:win    # Windows build in dist/
npm run pack        # unpacked app in dist/ (for quick local testing)
```

One quirk worth knowing: ad-hoc builds change the app's identity, so **macOS
permissions reset every time you rebuild.** Grant them once and keep that build.

## Setup

Three things, all one-time.

### 1. Permissions

- **macOS:** grant **Microphone** and **Screen Recording** on first use (or
  under System Settings, Privacy & Security). The single Screen Recording grant
  covers both screenshots *and* meeting audio. Let the app restart if macOS
  asks.
- **Windows:** nothing to grant. Screen capture and the mic work out of the box.

### 2. Your AI key

Open Settings (the `...` button, or `⌘` `,`) and paste a key. Keys are stored
**only on your machine, encrypted with your OS keychain,** and sent only to the
provider you picked. There is no server and nothing is collected.

| Provider | Get a key | Worth knowing |
|---|---|---|
| **OpenAI** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | Does everything. *Listening* needs a key with **Whisper/audio** access; chat-only restricted keys return 403 on transcription. |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com) | Strong on screen and coding help. No speech-to-text, so pair it with OpenAI or Gemini for listening. |
| **Google Gemini** | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | One key covers chat and transcription. |
| **Nvidia** | [build.nvidia.com](https://build.nvidia.com) | Vision-capable Llama models. |

**For listening you need a transcription-capable key** (OpenAI with Whisper, or
Gemini). Anthropic and Nvidia alone cannot transcribe.

### 3. Zoom capture mode (macOS Zoom only)

Google Meet, Microsoft Teams, and QuickTime need no changes. **Zoom on macOS**
has one capture setting that decides whether it honors the invisibility flag:

1. Open Zoom and click your profile picture, then **Settings** (or press `⌘` `,`).
2. Select **Share Screen** in the left sidebar.
3. Scroll to the bottom of that panel and click **Advanced**.
4. Under **Screen capture mode**, choose **Advanced capture with window
   filtering**.
5. Restart any share already in progress so the change takes effect.

<img src="docs/zoom-capture-mode.png" width="560" alt="Zoom Settings, Share Screen, Advanced, with Screen capture mode set to Advanced capture with window filtering" />

**Why this matters:** "with window filtering" lets Zoom drop protected windows
from the share. The other options (**"without window filtering"** and the
legacy modes) capture the raw screen and **will** show the overlay.

> **Windows users:** there is no equivalent setting. Zoom on Windows honors the
> flag out of the box, so skip this step.

## Controls

| Key | Action |
|---|---|
| `⌘` `↵` | **Assist.** The do-the-smart-thing key (rebindable in Settings). |
| `⌘` `H` | Solve the coding problem on screen. |
| `▢` button | Start/stop listening to the meeting (green dot means live). |
| Type + `↵` | Ask anything about your screen or the conversation. |
| `⌘` `⇧` `X` | Quit. |

**Hide** collapses the panel to the top bar. Drag it by the pill. Click the
**statue logo** anytime to reopen the first-run guide.

## What's inside

An [Electron](https://www.electronjs.org/) app. Everything is local except the
calls to your chosen AI provider.

- **Screen:** full-resolution captures via `desktopCapturer`, taken only when a
  feature asks for one. Held in memory, never written to disk.
- **You:** mic audio, downsampled to 16 kHz, streamed to transcription.
- **Them:** system-output loopback capture on its own channel, so speaker
  attribution stays clean.

Both audio channels transcribe (OpenAI Whisper or Gemini) and flow, with an
optional screenshot, into your model. Answers **stream** into the panel.

**The invisibility everyone talks about** is one window flag,
`setContentProtection(true)`: `WDA_EXCLUDEFROMCAPTURE` on Windows,
`NSWindowSharingNone` on macOS. It is the same mechanism DRM players and Zoom's
own toolbar use, not a GPU trick, and best-effort per the disclaimer above. The
standalone proof of just this mechanic lives in
[`nus-teardown/examples/cluely`](https://github.com/potlakai/nus-teardown/tree/main/examples/cluely).

```
main process ──┬─ overlay window (frameless, transparent, always-on-top, content-protected)
               ├─ screenshot capture (desktopCapturer)
               ├─ speech-to-text (Whisper / Gemini)      ── "You" + "Them" channels
               └─ LLM streaming (OpenAI / Anthropic / Gemini / Nvidia)
renderer ──────┴─ the glass UI + mic capture + system-audio loopback
```

## Troubleshooting

**Permissions look granted but the app disagrees.** You approved an older build.
Ad-hoc signing changes the app's identity on rebuild, so toggle the permission
off and on, or remove and re-add the app, in System Settings.

**"403" or "no access to model."** Your key is restricted. The classic case: an
OpenAI project key limited to chat models works for screen help but 403s on
Whisper. Enable audio on the key, use an unrestricted one, or add a Gemini key
(it is the automatic transcription fallback).

**Listening produces no transcript.** Confirm you have a transcription-capable
key (OpenAI with Whisper, or Gemini) in Settings, and that Screen Recording is
granted (meeting audio needs it).

**It shows up in a Zoom share.** The Zoom setting above is wrong, or you are on
a capture mode that ignores the flag. Best-effort, per the disclaimer.

**"Damaged and can't be opened."** Run the `xattr -cr` one-liner from
[Get the prebuilt app](#get-the-prebuilt-app).

## Privacy

- No accounts, no servers, no telemetry. The app collects nothing.
- API keys live in one local file, encrypted with your OS keychain (DPAPI on
  Windows, Keychain on macOS), and go only to the provider you chose.
- Screenshots and audio leave the machine only when you run a feature, and only
  to your provider. The transcript lives in memory and dies when you quit.

## Contributing

Issues and PRs welcome. The code is deliberately small and readable: `main.js`
(app, capture, AI), `renderer/` (UI), `src/` (providers and pipeline). Plain
HTML/CSS/JS, no build step for the source. `npm test` runs the suite offline.

**Platform support:** macOS ✅ · Windows ✅ · Linux (untested)

**Open for contribution:** lower-latency streaming audio pipeline · optional
Deepgram transcription.

## Credits & license

Built as an open-source study of how tools like **Cluely** and **Interview
Coder** work. Modeled on the open-source clones `pickle-com/glass` and
`sohzm/cheating-daddy`.

**License: [GPL-3.0-or-later](LICENSE).**
