from __future__ import annotations

import math

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QRadialGradient

from .base import BaseVisual


class PlasmaVisual(BaseVisual):
    name = "plasma"
    description = "Ambient lava-lamp gradients with slow colour drift."

    def paint(self, painter: QPainter, rect: QRect) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(rect, self.palette.background)
        width = max(1, rect.width())
        height = max(1, rect.height())
        points = [
            (0.5 + 0.36 * math.sin(self.elapsed * 0.31), 0.5 + 0.36 * math.cos(self.elapsed * 0.23), self.palette.primary),
            (0.5 + 0.34 * math.cos(self.elapsed * 0.19 + 1.4), 0.5 + 0.34 * math.sin(self.elapsed * 0.29), self.palette.secondary),
            (0.5 + 0.42 * math.sin(self.elapsed * 0.17 + 2.2), 0.5 + 0.28 * math.cos(self.elapsed * 0.37), self.palette.accent),
        ]
        background = QLinearGradient(0, 0, width, height)
        background.setColorAt(0, self.palette.background)
        background.setColorAt(0.45, self.palette.soft)
        background.setColorAt(1, self.palette.background)
        painter.fillRect(rect, background)
        for x_ratio, y_ratio, base_color in points:
            gradient = QRadialGradient(width * x_ratio, height * y_ratio, max(width, height) * 0.55)
            color = QColor(base_color)
            color.setAlpha(150)
            transparent = QColor(base_color)
            transparent.setAlpha(0)
            gradient.setColorAt(0, color)
            gradient.setColorAt(0.45, QColor(color.red(), color.green(), color.blue(), 56))
            gradient.setColorAt(1, transparent)
            painter.fillRect(rect, gradient)
        painter.setPen(Qt.PenStyle.NoPen)
