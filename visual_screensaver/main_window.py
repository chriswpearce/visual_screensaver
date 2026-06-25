from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QColor, QCloseEvent, QPainter, QResizeEvent
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from .monitor_manager import MonitorInfo
from .settings import AppSettings
from .visuals import create_visual
from .visuals.base import BaseVisual


class VisualSurface(QWidget):
    def __init__(self, renderer: BaseVisual, activity_callback: Callable[[], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.renderer = renderer
        self.activity_callback = activity_callback
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAutoFillBackground(False)
        self.setMouseTracking(True)

    def set_renderer(self, renderer: BaseVisual) -> None:
        self.renderer.dispose()
        self.renderer = renderer
        self.update()

    def tick(self, delta_time: float) -> None:
        self.renderer.update(delta_time)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override name
        painter = QPainter(self)
        self.renderer.paint(painter, self.rect())
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802 - Qt override name
        self.renderer.handle_resize(self.rect())
        super().resizeEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt override name
        self.activity_callback()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override name
        self.activity_callback()
        super().mousePressEvent(event)


class ScreensaverWindow(QWidget):
    def __init__(
        self,
        monitor: MonitorInfo,
        settings: AppSettings,
        mode_name: str,
        request_quit: Callable[[], None],
        request_next_mode: Callable[[], None],
        request_previous_mode: Callable[[], None],
        primary_close_button: bool,
    ) -> None:
        super().__init__()
        self.monitor = monitor
        self.settings = settings
        self.mode_name = mode_name
        self.request_quit = request_quit
        self.request_next_mode = request_next_mode
        self.request_previous_mode = request_previous_mode
        self._allow_close = False
        self._cursor_hidden = False

        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if settings.stay_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setWindowTitle(f"Visual Screensaver - {monitor.name}")
        self.setGeometry(monitor.geometry)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        renderer = create_visual(mode_name)
        renderer.setup(QRect(0, 0, monitor.geometry.width(), monitor.geometry.height()), settings, monitor.index)
        self.surface = VisualSurface(renderer, self.show_cursor, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.surface)

        self.close_button = QPushButton("×", self)
        self.close_button.setObjectName("closeButton")
        self.close_button.setCursor(Qt.CursorShape.ArrowCursor)
        self.close_button.clicked.connect(self._request_close)
        self.close_button.setToolTip("Close Visual Screensaver")
        self.close_button.setVisible(settings.show_close_button and primary_close_button)
        self.close_button.setStyleSheet(
            "QPushButton#closeButton {"
            "background: rgba(10, 14, 28, 145); color: rgba(255,255,255,210);"
            "border: 1px solid rgba(255,255,255,80); border-radius: 15px;"
            "font-size: 22px; font-weight: 500; padding-bottom: 3px;"
            "}"
            "QPushButton#closeButton:hover {"
            "background: rgba(215, 55, 80, 220); color: white; border-color: rgba(255,255,255,180);"
            "}"
        )

        self.help_label = QLabel(self)
        self.help_label.setObjectName("helpOverlay")
        self.help_label.setText(
            "Visual Screensaver\n"
            "Ctrl + Alt + Q: quit\n"
            "Ctrl + Alt + Right/Left: switch visuals\n"
            "Ctrl + Alt + Up/Down: switch palettes\n"
            "Ctrl + Alt + H: show/hide help\n"
            "Function keys and normal input are ignored."
        )
        self.help_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.help_label.setStyleSheet(
            "QLabel#helpOverlay {"
            "background: rgba(5, 8, 16, 165); color: rgba(255,255,255,220);"
            "border: 1px solid rgba(255,255,255,70); border-radius: 12px;"
            "font-size: 15px; padding: 14px;"
            "}"
        )
        self.help_label.setVisible(settings.show_help_on_start and monitor.is_primary)

        self.cursor_timer = QTimer(self)
        self.cursor_timer.setInterval(max(250, int(settings.hide_cursor_after_seconds * 1000)))
        self.cursor_timer.timeout.connect(self.hide_cursor)
        if settings.hide_cursor_after_seconds > 0:
            self.cursor_timer.start()

        self._position_overlays()

    def launch(self) -> None:
        self.setGeometry(self.monitor.geometry)
        self.showFullScreen()
        self.raise_()
        self.activateWindow()

    def tick(self, delta_time: float) -> None:
        self.surface.tick(delta_time)

    def set_mode(self, mode_name: str) -> None:
        self.mode_name = mode_name
        renderer = create_visual(mode_name)
        renderer.setup(self.surface.rect(), self.settings, self.monitor.index)
        self.surface.set_renderer(renderer)

    def set_settings(self, settings: AppSettings) -> None:
        self.settings = settings
        self.set_mode(self.mode_name)

    def toggle_help(self) -> None:
        if self.monitor.is_primary:
            self.help_label.setVisible(not self.help_label.isVisible())

    def allow_close(self) -> None:
        self._allow_close = True

    def hide_cursor(self) -> None:
        if not self._cursor_hidden:
            self.setCursor(Qt.CursorShape.BlankCursor)
            self.surface.setCursor(Qt.CursorShape.BlankCursor)
            self._cursor_hidden = True

    def show_cursor(self) -> None:
        if self._cursor_hidden:
            self.unsetCursor()
            self.surface.unsetCursor()
            self._cursor_hidden = False
        if self.settings.hide_cursor_after_seconds > 0:
            self.cursor_timer.start()

    def _request_close(self) -> None:
        self.request_quit()

    def _position_overlays(self) -> None:
        margin = 18
        button_size = 32
        self.close_button.setGeometry(max(0, self.width() - button_size - margin), margin, button_size, button_size)
        self.help_label.adjustSize()
        help_width = min(460, max(320, self.help_label.sizeHint().width()))
        help_height = self.help_label.sizeHint().height()
        self.help_label.setGeometry(24, max(24, self.height() - help_height - 28), help_width, help_height)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802 - Qt override name
        self._position_overlays()
        super().resizeEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt override name
        self.show_cursor()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override name
        self.show_cursor()
        super().mousePressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 - Qt override name
        if self._allow_close or self.settings.allow_alt_f4:
            event.accept()
        else:
            event.ignore()
