# High-DPI UI and Capture Design

## Status
Implementation in progress; implementation direction approved by the user.

## Context
The target setup is a 3840x2160 Windows desktop with War Thunder running in a 2560x1440 borderless window. The application currently uses fixed Tk font sizes and a 199x70 scale dialog. Minimap screenshot coordinates are absolute desktop coordinates, while the existing resolution profile for 2560x1440 describes coordinates relative to that game image. The results overlay also uses absolute desktop coordinates. On a 4K desktop, the game's client area can be offset from the desktop origin and Windows may apply display scaling.

## Goals
- Keep Settings, Scale, and results UI readable at the monitor's effective DPI.
- Capture the minimap from the actual War Thunder client area, including when its 1440p window is moved on the 4K desktop.
- Keep detector input dimensions and pixel-coordinate math consistent with the selected game-resolution profile.
- Keep the results overlay positioned relative to the game window.
- Fail clearly rather than run detection against an incorrect crop when the game window or resolution cannot be validated.

## Non-goals
- Change the detector model, class selection, or distance/azimuth calculations.
- Add support for arbitrary game resolutions without corresponding minimap profiles.
- Change the user's Windows display resolution or game graphics settings.

## Decision
Use a shared Windows DPI helper and game-window-relative coordinates rather than a UI-only scale factor or a hard-coded 4K offset.

### DPI setup
Add a small helper under `code/` that enables per-monitor DPI awareness before Tkinter or PyAutoGUI initializes in each relevant process. Prefer Per-Monitor V2 where available, with a compatible Windows fallback. Read the effective DPI for each Tk window so text and pixel-sized geometry follow the Windows display-scale setting. Tk point-based fonts should use Tk scaling; explicit pixel spacing and placement in the fixed Scale window should use the same DPI factor. Center the Settings window using its measured requested size instead of a fixed 665x510 estimate.

### Game capture
Use the existing 2560x1440 resolution profile as offsets within the War Thunder client area. Locate the game window, obtain its client rectangle in physical screen pixels, and translate the profile crop origin to desktop coordinates. Confirm that the client dimensions match the selected profile before capture. If the window is missing or dimensions do not match, skip inference and report a clear error through the existing UI/logging path.

### Overlay placement and configuration
Position the results overlay at the game client origin plus the configured `print_x` and `print_y` offsets. Keep the existing INI keys and numeric values, but define them as offsets from the game client rather than absolute desktop coordinates. This lets the overlay stay over the game when the window moves.

### Startup ordering
Enable DPI awareness before importing or invoking APIs that may cache virtualized screen dimensions. Apply this in the main distance-finder process, Settings, the Scale dialog, and the results-overlay process. The helper must tolerate an already-configured process without preventing startup.

## Error handling
- No matching War Thunder window: do not capture or infer; show a concise unavailable-window message.
- Client size differs from selected profile: do not use a guessed crop; show a resolution-mismatch message.
- DPI API unavailable: use the documented fallback and retain functional startup; report the effective scaling mode in diagnostics.

## Verification
- Unit-check profile-to-desktop crop translation for a 2560x1440 client at the desktop origin and at a nonzero 4K desktop offset.
- Unit-check that a missing window or mismatched client dimensions rejects capture.
- Check DPI-to-Tk scaling and fixed Scale-window geometry calculations at 96, 144, and 192 DPI.
- Run warning-as-error syntax checks for project-owned Python files.
- Manually verify on a 3840x2160 desktop with a 2560x1440 borderless game window, including moving the game window and confirming the crop and overlay follow it.

## Expected implementation surface
- New shared DPI helper in `code/`.
- Startup ordering in `miniKarta.py`, `settings.pyw`, `code/scale.py`, and `code/printResults.py`.
- Window-relative crop calculation and validation in `code/distanceFinder.py`.
- Game-relative overlay placement and a clear mismatch state in `code/printResults.py` and its caller.

## References
- [Microsoft: SetProcessDpiAwarenessContext](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setprocessdpiawarenesscontext)
- [Microsoft: GetDpiForWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getdpiforwindow)
- [Microsoft: GetClientRect](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getclientrect)
- [Microsoft: ClientToScreen](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-clienttoscreen)
- [Tcl/Tk 8.6: tk scaling](https://www.tcl-lang.org/man/tcl8.6/TkCmd/tk.htm)
