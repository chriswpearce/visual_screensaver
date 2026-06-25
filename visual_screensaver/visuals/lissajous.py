from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen

from .base import BaseVisual


class LissajousVisual(BaseVisual):
    name = "lissajous"
    description = "Elegant mathematical curves and orbiting points."

    def paint(self, painter: QPainter, rect: QRect) -> None:
        painter.fillRect(rect, self.palette.background)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        center_x = rect.width() / 2
        center_y = rect.height() / 2
        radius_x = rect.width() * 0.36
        radius_y = rect.height() * 0.36
        for layer in range(5):
            path = QPainterPath()
            phase = self.elapsed * (0.38 + layer * 0.07) + layer * 0.9
            frequency_x = 3 + layer
            frequency_y = 2 + (layer % 3)
            points = 360
            for step in range(points + 1):
                t = step / points * math.tau
                x = center_x + math.sin(frequency_x * t + phase) * radius_x * (0.55 + layer * 0.08)
                y = center_y + math.sin(frequency_y * t + phase * 0.73) * radius_y * (0.55 + layer * 0.08)
                if step == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            color = QColor([self.palette.primary, self.palette.secondary, self.palette.accent][layer % 3])
            color.setAlpha(70 + layer * 25)
            painter.setPen(QPen(color, 1.5 + layer * 0.45, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPath(path)
        for dot in range(10):
            phase = self.elapsed * 0.55 + dot * math.tau / 10
            x = center_x + math.sin(phase * 2.1) * radius_x * 0.82
            y = center_y + math.cos(phase * 1.7) * radius_y * 0.82
            color = QColor(self.palette.accent if dot % 2 else self.palette.primary)
            color.setAlpha(190)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(QPointF(x, y), 3.5, 3.5)
