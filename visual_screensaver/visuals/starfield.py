from __future__ import annotations

import random
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPen

from .base import BaseVisual, quality_scale, random_between


@dataclass
class Star:
    x: float
    y: float
    z: float
    speed: float
    size: float


class StarfieldVisual(BaseVisual):
    name = "starfield"
    description = "Depth starfield with glowing motion trails."

    def setup(self, rect: QRect, settings, screen_index: int) -> None:
        super().setup(rect, settings, screen_index)
        self.stars: list[Star] = []
        self._build_stars()

    def _build_stars(self) -> None:
        area = max(1, self.rect.width() * self.rect.height())
        count = int(min(1200, max(180, area / 3800 * quality_scale(self.settings))))
        self.stars = [self._new_star(randomize_z=True) for _ in range(count)]

    def _new_star(self, randomize_z: bool = False) -> Star:
        return Star(
            x=random_between(-1.0, 1.0),
            y=random_between(-1.0, 1.0),
            z=random_between(0.08, 1.0) if randomize_z else 1.0,
            speed=random_between(0.18, 0.75),
            size=random_between(0.8, 2.4),
        )

    def update(self, delta_time: float) -> None:
        super().update(delta_time)
        for index, star in enumerate(self.stars):
            star.z -= star.speed * delta_time
            if star.z <= 0.03:
                self.stars[index] = self._new_star()

    def paint(self, painter: QPainter, rect: QRect) -> None:
        painter.fillRect(rect, self.palette.background)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        center_x = rect.width() / 2
        center_y = rect.height() / 2
        scale = min(rect.width(), rect.height()) * 0.56
        for star in self.stars:
            inv_z = 1.0 / star.z
            x = center_x + star.x * scale * inv_z
            y = center_y + star.y * scale * inv_z
            if x < 0 or x > rect.width() or y < 0 or y > rect.height():
                continue
            previous_z = min(1.0, star.z + 0.045)
            previous_inv = 1.0 / previous_z
            px = center_x + star.x * scale * previous_inv
            py = center_y + star.y * scale * previous_inv
            alpha = max(40, min(255, int((1.0 - star.z) * 280)))
            color = QColor(self.palette.primary)
            color.setAlpha(alpha)
            painter.setPen(QPen(color, max(1.0, star.size * inv_z * 0.22), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPointF(px, py), QPointF(x, y))
            glow = QColor(self.palette.accent)
            glow.setAlpha(alpha // 3)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow)
            radius = max(0.8, star.size * inv_z * 0.5)
            painter.drawEllipse(QPointF(x, y), radius, radius)

    def handle_resize(self, rect: QRect) -> None:
        super().handle_resize(rect)
        self._build_stars()
