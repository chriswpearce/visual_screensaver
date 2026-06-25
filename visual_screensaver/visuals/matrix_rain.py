from __future__ import annotations

import random
from dataclasses import dataclass

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter

from .base import BaseVisual, quality_scale, random_between


GLYPHS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-*/=<>{}[]()#$%&"


@dataclass
class Column:
    x: int
    head: float
    speed: float
    length: int
    glyphs: list[str]


class MatrixRainVisual(BaseVisual):
    name = "matrix_rain"
    description = "Falling glyph rain with configurable palettes."

    def setup(self, rect: QRect, settings, screen_index: int) -> None:
        super().setup(rect, settings, screen_index)
        self.font_size = 18 if settings.visual_quality != "low" else 22
        self.columns: list[Column] = []
        self._build_columns()

    def _build_columns(self) -> None:
        font = QFont("Consolas", self.font_size)
        metrics = QFontMetrics(font)
        column_width = max(12, metrics.horizontalAdvance("W") + 4)
        count = max(1, self.rect.width() // column_width)
        scale = quality_scale(self.settings)
        self.columns = []
        for index in range(count):
            if random.random() > 0.72 + scale * 0.24:
                continue
            length = random.randint(8, 34)
            self.columns.append(
                Column(
                    x=index * column_width,
                    head=random_between(-self.rect.height(), self.rect.height()),
                    speed=random_between(55, 185) * (0.75 + scale * 0.45),
                    length=length,
                    glyphs=[random.choice(GLYPHS) for _ in range(length)],
                )
            )
        self.column_width = column_width

    def update(self, delta_time: float) -> None:
        super().update(delta_time)
        for column in self.columns:
            column.head += column.speed * delta_time
            if column.head - column.length * self.font_size > self.rect.height() + 80:
                column.head = random_between(-self.rect.height() * 0.8, -40)
                column.speed = random_between(55, 185)
                column.length = random.randint(8, 34)
                column.glyphs = [random.choice(GLYPHS) for _ in range(column.length)]
            if random.random() < 0.02:
                column.glyphs[random.randrange(len(column.glyphs))] = random.choice(GLYPHS)

    def paint(self, painter: QPainter, rect: QRect) -> None:
        painter.fillRect(rect, QColor(self.palette.background.red(), self.palette.background.green(), self.palette.background.blue(), 70))
        painter.setFont(QFont("Consolas", self.font_size, QFont.Weight.Medium))
        for column in self.columns:
            for offset, glyph in enumerate(column.glyphs):
                y = column.head - offset * self.font_size
                if y < -self.font_size or y > rect.height() + self.font_size:
                    continue
                if offset == 0:
                    color = QColor(self.palette.accent)
                    color.setAlpha(240)
                else:
                    color = QColor(self.palette.primary if offset < 6 else self.palette.secondary)
                    color.setAlpha(max(18, 210 - offset * 8))
                painter.setPen(color)
                painter.drawText(column.x, int(y), self.column_width, self.font_size, Qt.AlignmentFlag.AlignCenter, glyph)

    def handle_resize(self, rect: QRect) -> None:
        super().handle_resize(rect)
        self._build_columns()
