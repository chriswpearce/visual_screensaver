from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QGuiApplication, QScreen
from PySide6.QtCore import QRect


@dataclass(frozen=True)
class MonitorInfo:
    screen: QScreen
    name: str
    geometry: QRect
    available_geometry: QRect
    device_pixel_ratio: float
    is_primary: bool
    index: int


class MonitorManager:
    def __init__(self, app: QGuiApplication) -> None:
        self.app = app

    def monitors(self) -> list[MonitorInfo]:
        primary = self.app.primaryScreen()
        monitors: list[MonitorInfo] = []
        for index, screen in enumerate(self.app.screens()):
            monitors.append(
                MonitorInfo(
                    screen=screen,
                    name=screen.name() or f"Screen {index + 1}",
                    geometry=screen.geometry(),
                    available_geometry=screen.availableGeometry(),
                    device_pixel_ratio=screen.devicePixelRatio(),
                    is_primary=screen is primary,
                    index=index,
                )
            )
        return monitors
