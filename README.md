# Visual Screensaver

Visual Screensaver is a decorative Windows screensaver-style app that displays animated generative visuals across all connected monitors without locking the computer or using the Windows `.scr` screensaver system.

It is designed for people who want a manual "away from keyboard" visual display while keeping the session awake with tools such as Caffeine.

## Highlights

- Covers every connected monitor with borderless full-screen windows.
- Does not lock Windows and does not alter power, display, or security settings.
- Ignores ordinary keypresses, mouse movement, and function-key activity so Caffeine does not close it.
- Shows a custom close button on the primary monitor.
- Provides keyboard shortcuts for quitting, switching visuals, switching palettes, and showing help.
- Includes five built-in generative visual modes.
- Can be run from Python source or packaged into a single Windows executable.

## Visual Modes

- `particle_flow` - organic particles drifting through a changing flow field.
- `starfield` - classic depth starfield with glowing trails.
- `plasma` - slow ambient lava-lamp style gradients.
- `matrix_rain` - falling terminal-style glyph rain.
- `lissajous` - elegant mathematical curves and orbiting points.

## Palettes

- `aurora`
- `neon`
- `ocean`
- `fire`
- `mono`
- `matrix`

## Controls

| Action | Shortcut |
|---|---|
| Quit | `Ctrl + Alt + Q` |
| Quit | Click the custom `X` on the primary monitor |
| Next visual | `Ctrl + Alt + Right` |
| Previous visual | `Ctrl + Alt + Left` |
| Next palette | `Ctrl + Alt + Up` |
| Previous palette | `Ctrl + Alt + Down` |
| Show/hide help | `Ctrl + Alt + H` |
| Tray menu | Right-click tray icon, if available |

The mouse cursor hides automatically after a short delay. Moving the mouse shows it again so you can navigate to the close button.

## Security Note

This app is decorative only. It does not secure your computer. If you need to protect your session, lock Windows with `Win + L`.

## Requirements

- Windows 10/11 recommended.
- Python 3.9+ for source usage.
- PySide6 for the desktop UI.
- PyInstaller for packaging.

## Run From Source

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run_screensaver.py --show-help
```

If PowerShell blocks virtual environment activation, run Python directly from `.venv\Scripts\python.exe` or use Command Prompt.

## Launch Options

```powershell
python run_screensaver.py --mode starfield
python run_screensaver.py --mode plasma --palette ocean --fps 30
python run_screensaver.py --mode matrix_rain --palette matrix --quality medium
python run_screensaver.py --show-help
```

## Configuration

Bundled defaults live in `config/default_settings.json`.

Runtime preferences are stored at:

```text
%APPDATA%\Visual Screensaver\settings.json
```

You can also launch with a custom config file:

```powershell
python run_screensaver.py --config C:\path\to\settings.json
```

## Build a Windows EXE

Run:

```powershell
.\packaging\build.ps1
```

The build script creates a single local executable at:

```text
VisualScreensaver.exe
```

Generated PyInstaller folders are cleaned after the final executable is copied.

## Recommended Test

1. Start Caffeine if you use it.
2. Launch `VisualScreensaver.exe` or run from source with `--show-help`.
3. Confirm every monitor is covered.
4. Move the mouse and confirm the cursor reappears.
5. Use `Ctrl + Alt + Up` and `Ctrl + Alt + Down` to change palettes.
6. Confirm Caffeine function-key activity does not close the app.
7. Exit with `Ctrl + Alt + Q` or the custom close button.

## Project Structure

```text
config/                 Default JSON settings
packaging/              Build script
visual_screensaver/     Application source code
run_screensaver.py      Source entry point
requirements.txt        Python dependencies
```
