# Teardown: Cluely

> Example output of the `/teardown` relay, kept in the repo as the reference
> teardown. The runnable proof of the one special mechanic is
> [`invisible_overlay.py`](./invisible_overlay.py). Verified on Windows 11:
> the capture-exclusion call returns success in full `excluded` mode.

## Product
Cluely is a desktop AI assistant that listens to your meeting, interview, or call
and feeds you real-time answers on screen. Its whole marketing hook is that it is
"undetectable": the other side, and your screen-share, cannot see it. Reported at
around **$150/month** in the teardown that popularized it. **(Cluely has listed
other tiers elsewhere. Verify current pricing on cluely.com before repeating a
number as fact.)**

## The one special thing
**It draws a window you can see but that screen-share and screen recording cannot.**
Remove that, and Cluely is a floating chat box over a transcription plus an LLM.
The invisibility is the entire reason anyone talks about it.

## Why it is the moat
Everything else Cluely does is commodity in 2026: live transcription, an LLM
answering from context, an always-on-top overlay. Any competent builder ships that
in a weekend. The thing people cannot immediately reproduce, and the thing that
makes the demo feel like magic, is that you can be on a Zoom screen-share with the
assistant open and the viewer sees nothing. That single property is what the brand,
the virality, and the "how is this even allowed" reaction are built on.

## How it works
It is not clever. It is one operating-system call.

- **Windows:** `SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)`. On Windows
  10 version 2004 (build 19041) and newer, this omits the window from all screen
  capture (Zoom, Teams, Meet, OBS, Snipping Tool, print-screen) while it stays
  visible on your physical monitor. Older Windows supports `WDA_MONITOR`, which
  makes the window show as a black block in captures instead.
  Docs: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowdisplayaffinity
- **macOS:** set `NSWindow.sharingType = .none` on the window, which excludes it
  from screen sharing and recording.

Our proof implements the Windows path in ~100 lines of standard-library Python,
no dependencies, no account. Run it, share your screen, and it is gone from the
share while you still see it.

## Not worth copying (the generic 90 percent)
- The transcription pipeline (off-the-shelf speech-to-text).
- The LLM answer layer (this is the wrapper part, and it is the cheap part).
- The overlay UI, hotkeys, onboarding.
Skip all of it for the teardown. The story is the one flag.

## Confidence
**High** on the mechanism: the capture-exclusion APIs above are public, documented,
and the proof runs in full exclusion mode on current Windows. **Medium** on the
claim that Cluely uses exactly these calls versus a functionally identical method
(a virtual overlay device or a compositor trick); the observable behavior is the
same and is reproduced by the proof either way. Company facts (pricing, funding)
should be re-verified against primary sources before being repeated publicly.
