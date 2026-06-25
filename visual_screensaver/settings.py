from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import __app_name__


DEFAULT_SETTINGS: dict[str, Any] = {
    "default_mode": "particle_flow",
    "palette": "aurora",
    "exit_hotkey": "Ctrl+Alt+Q",
    "show_close_button": True,
    "close_button_screen": "primary",
    "ignore_function_keys": True,
    "hide_cursor_after_seconds": 3,
    "stay_on_top": True,
    "visual_quality": "high",
    "target_fps": 60,
    "monitor_mode": "independent",
    "allow_alt_f4": True,
    "show_help_on_start": False,
    "persist_last_mode": True,
}


@dataclass(frozen=True)
class AppSettings:
    default_mode: str = "particle_flow"
    palette: str = "aurora"
    exit_hotkey: str = "Ctrl+Alt+Q"
    show_close_button: bool = True
    close_button_screen: str = "primary"
    ignore_function_keys: bool = True
    hide_cursor_after_seconds: float = 3.0
    stay_on_top: bool = True
    visual_quality: str = "high"
    target_fps: int = 60
    monitor_mode: str = "independent"
    allow_alt_f4: bool = True
    show_help_on_start: bool = False
    persist_last_mode: bool = True
    active_mode: str = "particle_flow"
    config_path: Path | None = None
    user_config_path: Path | None = None
    raw: dict[str, Any] = field(default_factory=dict)


def app_data_dir() -> Path:
    root = os.environ.get("APPDATA")
    if root:
        return Path(root) / __app_name__
    return Path.home() / f".{__app_name__.lower().replace(' ', '_')}"


def bundled_config_path() -> Path:
    return Path(__file__).resolve().parents[1] / "config" / "default_settings.json"


def user_config_path() -> Path:
    return app_data_dir() / "settings.json"


def load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def merge_settings(*sources: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for source in sources:
        merged.update({key: value for key, value in source.items() if value is not None})
    return merged


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="visual-screensaver",
        description="Launch decorative Caffeine-safe fullscreen visuals across all connected monitors.",
    )
    parser.add_argument("--mode", help="Visual mode to start with.")
    parser.add_argument("--palette", help="Colour palette to use.")
    parser.add_argument("--fps", type=int, dest="target_fps", help="Target frames per second.")
    parser.add_argument("--quality", choices=["low", "medium", "high"], dest="visual_quality")
    parser.add_argument("--no-stay-on-top", action="store_false", dest="stay_on_top")
    parser.add_argument("--show-help", action="store_true", dest="show_help_on_start")
    parser.add_argument("--config", type=Path, help="Optional settings JSON path.")
    parser.set_defaults(stay_on_top=None, show_help_on_start=None)
    return parser.parse_args(argv)


def settings_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "default_mode": args.mode,
        "palette": args.palette,
        "target_fps": args.target_fps,
        "visual_quality": args.visual_quality,
        "stay_on_top": args.stay_on_top,
        "show_help_on_start": args.show_help_on_start,
    }


def normalize_settings(raw: dict[str, Any], config_path: Path | None, app_user_config_path: Path) -> AppSettings:
    fps = int(raw.get("target_fps", DEFAULT_SETTINGS["target_fps"]) or DEFAULT_SETTINGS["target_fps"])
    fps = min(max(fps, 10), 144)
    hide_cursor_after = float(raw.get("hide_cursor_after_seconds", 3) or 0)
    default_mode = str(raw.get("default_mode") or DEFAULT_SETTINGS["default_mode"])
    return AppSettings(
        default_mode=default_mode,
        palette=str(raw.get("palette") or DEFAULT_SETTINGS["palette"]),
        exit_hotkey=str(raw.get("exit_hotkey") or DEFAULT_SETTINGS["exit_hotkey"]),
        show_close_button=bool(raw.get("show_close_button", True)),
        close_button_screen=str(raw.get("close_button_screen") or "primary"),
        ignore_function_keys=bool(raw.get("ignore_function_keys", True)),
        hide_cursor_after_seconds=max(0.0, hide_cursor_after),
        stay_on_top=bool(raw.get("stay_on_top", True)),
        visual_quality=str(raw.get("visual_quality") or "high"),
        target_fps=fps,
        monitor_mode=str(raw.get("monitor_mode") or "independent"),
        allow_alt_f4=bool(raw.get("allow_alt_f4", True)),
        show_help_on_start=bool(raw.get("show_help_on_start", False)),
        persist_last_mode=bool(raw.get("persist_last_mode", True)),
        active_mode=default_mode,
        config_path=config_path,
        user_config_path=app_user_config_path,
        raw=dict(raw),
    )


def load_settings(argv: list[str] | None = None) -> AppSettings:
    args = parse_args(argv)
    base_config = bundled_config_path()
    chosen_config = args.config or base_config
    app_user_config = user_config_path()
    raw = merge_settings(
        DEFAULT_SETTINGS,
        load_json_file(base_config),
        load_json_file(app_user_config),
        load_json_file(chosen_config) if args.config else {},
        settings_from_args(args),
    )
    return normalize_settings(raw, chosen_config, app_user_config)


def save_last_mode(settings: AppSettings, mode: str) -> None:
    if not settings.persist_last_mode or settings.user_config_path is None:
        return
    path = settings.user_config_path
    path.parent.mkdir(parents=True, exist_ok=True)
    data = load_json_file(path)
    data["default_mode"] = mode
    data["palette"] = settings.palette
    try:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass
