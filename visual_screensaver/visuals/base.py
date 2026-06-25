from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QPainter

from visual_screensaver.settings import AppSettings


@dataclass(frozen=True)
class Palette:
    name: str
    background: QColor
    primary: QColor
    secondary: QColor
    accent: QColor
    soft: QColor


PALETTES: dict[str, Palette] = {
    "aurora": Palette("aurora", QColor(2, 7, 24), QColor(58, 255, 206), QColor(109, 93, 252), QColor(255, 96, 231), QColor(24, 45, 85)),
    "neon": Palette("neon", QColor(3, 3, 8), QColor(0, 255, 170), QColor(255, 0, 130), QColor(0, 145, 255), QColor(25, 25, 40)),
    "ocean": Palette("ocean", QColor(0, 13, 31), QColor(65, 201, 255), QColor(0, 111, 185), QColor(155, 245, 255), QColor(8, 38, 68)),
    "fire": Palette("fire", QColor(12, 3, 0), QColor(255, 183, 57), QColor(255, 70, 30), QColor(255, 245, 160), QColor(62, 18, 5)),
    "mono": Palette("mono", QColor(0, 0, 0), QColor(235, 235, 235), QColor(140, 140, 140), QColor(255, 255, 255), QColor(28, 28, 28)),
    "matrix": Palette("matrix", QColor(0, 0, 0), QColor(75, 255, 110), QColor(0, 130, 45), QColor(210, 255, 220), QColor(0, 30, 10)),
}


def get_palette(name: str) -> Palette:
    return PALETTES.get(name.lower(), PALETTES["aurora"])


def quality_scale(settings: AppSettings) -> float:
    return {"low": 0.45, "medium": 0.7, "high": 1.0}.get(settings.visual_quality.lower(), 1.0)


def random_between(low: float, high: float) -> float:
    return low + random.random() * (high - low)


class VisualRenderer(Protocol):
    name: str
    description: str

    def setup(self, rect: QRect, settings: AppSettings, screen_index: int) -> None:
        ...

    def update(self, delta_time: float) -> None:
        ...

    def paint(self, painter: QPainter, rect: QRect) -> None:
        ...

    def handle_resize(self, rect: QRect) -> None:
        ...

    def dispose(self) -> None:
        ...


class BaseVisual:
    name = "base"
    description = "Base visual"

    def __init__(self) -> None:
        self.rect = QRect()
        self.settings: AppSettings | None = None
        self.palette = get_palette("aurora")
        self.screen_index = 0
        self.elapsed = 0.0

    def setup(self, rect: QRect, settings: AppSettings, screen_index: int) -> None:
        self.rect = QRect(rect)
        self.settings = settings
        self.palette = get_palette(settings.palette)
        self.screen_index = screen_index

    def update(self, delta_time: float) -> None:
        self.elapsed += delta_time

    def paint(self, painter: QPainter, rect: QRect) -> None:
        painter.fillRect(rect, self.palette.background)

    def handle_resize(self, rect: QRect) -> None:
        self.rect = QRect(rect)

    def dispose(self) -> None:
        pass
