from __future__ import annotations

import math
import random
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPen

from .base import BaseVisual, quality_scale, random_between


@dataclass
class Particle:
    x: float
    y: float
    previous_x: float
    previous_y: float
    speed: float
    age: float


class ParticleFlowVisual(BaseVisual):
    name = "particle_flow"
    description = "Organic particles drifting through a changing flow field."

    def setup(self, rect: QRect, settings, screen_index: int) -> None:
        super().setup(rect, settings, screen_index)
        self.particles: list[Particle] = []
        self._build_particles()

    def _build_particles(self) -> None:
        area = max(1, self.rect.width() * self.rect.height())
        count = int(min(1800, max(260, area / 2900 * quality_scale(self.settings))))
        self.particles = [self._new_particle() for _ in range(count)]

    def _new_particle(self) -> Particle:
        x = random_between(0, max(1, self.rect.width()))
        y = random_between(0, max(1, self.rect.height()))
        return Particle(x, y, x, y, random_between(28, 95), random_between(0, 8))

    def _field_angle(self, x: float, y: float, time_value: float) -> float:
        scale = 0.0045
        wave_a = math.sin(y * scale + time_value * 0.7)
        wave_b = math.cos(x * scale * 1.3 - time_value * 0.45)
        wave_c = math.sin((x + y) * scale * 0.55 + time_value * 0.32)
        return (wave_a + wave_b + wave_c) * math.pi

    def update(self, delta_time: float) -> None:
        super().update(delta_time)
        width = max(1, self.rect.width())
        height = max(1, self.rect.height())
        for index, particle in enumerate(self.particles):
            particle.previous_x = particle.x
            particle.previous_y = particle.y
            angle = self._field_angle(particle.x, particle.y, self.elapsed)
            particle.x += math.cos(angle) * particle.speed * delta_time
            particle.y += math.sin(angle) * particle.speed * delta_time
            particle.age += delta_time
            margin = 24
            if particle.x < -margin or particle.x > width + margin or particle.y < -margin or particle.y > height + margin or particle.age > 22:
                self.particles[index] = self._new_particle()

    def paint(self, painter: QPainter, rect: QRect) -> None:
        painter.fillRect(rect, QColor(self.palette.background.red(), self.palette.background.green(), self.palette.background.blue(), 42))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        for index, particle in enumerate(self.particles):
            ratio = (math.sin(self.elapsed * 0.7 + index * 0.037) + 1) / 2
            base = self.palette.primary if ratio < 0.5 else self.palette.accent
            color = QColor(base)
            color.setAlpha(130)
            width = 1.0 + 1.6 * ratio
            painter.setPen(QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPointF(particle.previous_x, particle.previous_y), QPointF(particle.x, particle.y))

    def handle_resize(self, rect: QRect) -> None:
        super().handle_resize(rect)
        self._build_particles()
