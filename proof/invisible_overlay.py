#!/usr/bin/env python3
"""
invisible_overlay.py

The ONE trick that makes Cluely "special", rebuilt in ~100 lines of standard
library Python. Nothing else. No LLM, no account, no subscription.

Cluely's core mechanic: a window you can see, but your screen-share and screen
recording cannot. On Windows that is a single documented OS call:

    SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)

Any app that captures your screen (Zoom, Teams, Google Meet, OBS, the Snipping
Tool, print-screen) renders this window as blank. You still see it on your own
monitor. That is the whole "undetectable" pitch.

Usage:
    python invisible_overlay.py              show the overlay (Esc to quit)
    python invisible_overlay.py --selftest   apply the flag, print result, exit

Requirements:
    Windows 10 version 2004 (build 19041) or newer, for full capture exclusion.
    Older Windows falls back to WDA_MONITOR (the window shows as a black block in
    captures instead of being fully omitted). Python standard library only.

macOS equivalent (for reference, not implemented here):
    Set NSWindow.sharingType = .none on the overlay window.
"""

import sys
import ctypes
from ctypes import wintypes

# Display-affinity flags (winuser.h)
WDA_NONE = 0x00000000
WDA_MONITOR = 0x00000001              # older: window shows as black in captures
WDA_EXCLUDEFROMCAPTURE = 0x00000011   # Win10 2004+: window omitted from captures

GA_ROOT = 2  # GetAncestor: walk up to the root (top-level) window

user32 = ctypes.windll.user32
user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
user32.SetWindowDisplayAffinity.restype = wintypes.BOOL
user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetAncestor.restype = wintypes.HWND


def toplevel_hwnd(tk_widget):
    """Get the real top-level HWND for a Tk window.

    Tk's winfo_id() often returns an inner content window; display affinity must
    be set on the top-level, so we walk up with GetAncestor(GA_ROOT).
    """
    tk_widget.update_idletasks()
    raw = tk_widget.winfo_id()
    root = user32.GetAncestor(raw, GA_ROOT)
    return root or raw


def hide_from_capture(hwnd):
    """Make the window invisible to screen capture. Returns the mode applied."""
    if user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE):
        return "excluded"   # fully omitted from capture (Win10 2004+)
    if user32.SetWindowDisplayAffinity(hwnd, WDA_MONITOR):
        return "monitor"    # shows as a black block in capture (older Windows)
    return None             # not supported on this OS


def selftest():
    """Prove the OS call works without opening a persistent window. For CI/verify."""
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # never shown
    hwnd = toplevel_hwnd(root)
    mode = hide_from_capture(hwnd)
    root.destroy()
    if mode is None:
        print("FAIL: SetWindowDisplayAffinity is not supported on this system.")
        return 1
    print(f"OK: capture protection applied (mode={mode}, hwnd={hwnd}).")
    print("A real overlay launched with this flag is invisible to screen-share.")
    return 0


def run_overlay():
    """Show the actual capture-proof overlay."""
    import tkinter as tk

    root = tk.Tk()
    root.title("nus // invisible")
    root.overrideredirect(True)          # borderless
    root.attributes("-topmost", True)    # always on top
    root.attributes("-alpha", 0.88)      # slight transparency
    root.configure(bg="#0a0a0a")

    # Position top-right of the primary screen.
    w, h = 380, 150
    sw = root.winfo_screenwidth()
    root.geometry(f"{w}x{h}+{sw - w - 24}+24")

    tk.Label(root, text="You can see this.", fg="#ffffff", bg="#0a0a0a",
             font=("Segoe UI", 18, "bold")).pack(pady=(20, 2))
    tk.Label(root, text="Your screen-share can't.", fg="#8b8b8b", bg="#0a0a0a",
             font=("Segoe UI", 13)).pack()
    tk.Label(root, text="nus teardown  //  cluely's one trick  //  Esc to quit",
             fg="#4a4a4a", bg="#0a0a0a", font=("Consolas", 8)).pack(side="bottom",
                                                                     pady=(0, 8))

    # Apply capture protection once mapped, and re-apply on every map event
    # (some Windows versions drop the flag when the window is re-shown).
    def apply(_=None):
        mode = hide_from_capture(toplevel_hwnd(root))
        if mode is None:
            root.title("nus // NOT protected (OS too old)")

    root.bind("<Map>", apply)
    root.after(50, apply)

    # Let the user drag the borderless window around.
    def start_drag(e):
        root._dx, root._dy = e.x, e.y

    def do_drag(e):
        root.geometry(f"+{e.x_root - root._dx}+{e.y_root - root._dy}")

    root.bind("<Button-1>", start_drag)
    root.bind("<B1-Motion>", do_drag)
    root.bind("<Escape>", lambda e: root.destroy())

    root.mainloop()


def main():
    if not sys.platform.startswith("win"):
        print("This proof uses a Windows-only API (SetWindowDisplayAffinity).")
        print("On macOS the equivalent is NSWindow.sharingType = .none.")
        return 2
    if "--selftest" in sys.argv:
        return selftest()
    run_overlay()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
