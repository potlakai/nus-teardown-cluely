# Cluely, torn down

The full teardown is in [`TEARDOWN.md`](./TEARDOWN.md). Short version: the one
thing that makes Cluely special is a window your screen-share cannot see, and that
is a single OS call. Here is that call, rebuilt, running, free.

## Run it

```bash
python invisible_overlay.py
```

An overlay appears top-right: "You can see this. Your screen-share can't." Start a
screen-share or a screen recording. It is not there. Drag it anywhere, press Esc to
quit.

Prove the mechanism without opening a window (what CI runs):

```bash
python invisible_overlay.py --selftest
# OK: capture protection applied (mode=excluded, hwnd=...).
```

## Requirements
- Windows 10 version 2004 (build 19041) or newer for full invisibility. Older
  Windows falls back to showing a black block in captures.
- Python 3, standard library only. Nothing to install.
- macOS: the same effect is `NSWindow.sharingType = .none`. Not implemented here.

## The point
Cluely charges a subscription for the assistant wrapped around this trick. The
trick itself is free and public. That is what the teardown agent does for any app:
find the one part that is actually the moat, and hand you a runnable copy of it.

This is a reimplementation of a public technique for education and commentary. It
does not include any of Cluely's code, assets, or branding.
