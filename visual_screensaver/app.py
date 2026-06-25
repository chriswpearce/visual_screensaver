from __future__ import annotations

import sys
import time
from dataclasses import replace

from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtGui import QAction, QGuiApplication, QKeyEvent
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon

from . import __app_name__
from .main_window import ScreensaverWindow
from .monitor_manager import MonitorManager
from .settings import AppSettings, load_settings, save_last_mode
from .visuals import visual_names
from .visuals.base import PALETTES


class ScreensaverController(QObject):
    def __init__(self, app: QApplication, settings: AppSettings) -> None:
        super().__init__()
        self.app = app
        self.settings = settings
        self.monitor_manager = MonitorManager(app)
        self.modes = visual_names()
        self.mode_index = self._initial_mode_index(settings.active_mode)
        self.palettes = list(PALETTES.keys())
        self.palette_index = self._initial_palette_index(settings.palette)
        self.windows: list[ScreensaverWindow] = []
        self.last_frame_time = time.perf_counter()
        self.tray_icon: QSystemTrayIcon | None = None
        self.app.installEventFilter(self)
        self.timer = QTimer(self)
        self.timer.setInterval(max(7, int(1000 / settings.target_fps)))
        self.timer.timeout.connect(self.tick)
        self.rebuild_timer = QTimer(self)
        self.rebuild_timer.setSingleShot(True)
        self.rebuild_timer.timeout.connect(self.rebuild_windows)
        self.app.screenAdded.connect(self.schedule_rebuild)
        self.app.screenRemoved.connect(self.schedule_rebuild)

    @property
    def current_mode(self) -> str:
        return self.modes[self.mode_index]

    @property
    def current_palette(self) -> str:
        return self.palettes[self.palette_index]

    def start(self) -> None:
        self.create_tray_icon()
        self.rebuild_windows()
        self.timer.start()

    def _initial_mode_index(self, mode_name: str) -> int:
        normalized = mode_name.lower().strip()
        return self.modes.index(normalized) if normalized in self.modes else self.modes.index("particle_flow")

    def _initial_palette_index(self, palette_name: str) -> int:
        normalized = palette_name.lower().strip()
        return self.palettes.index(normalized) if normalized in self.palettes else self.palettes.index("aurora")

    def create_tray_icon(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        menu = QMenu()
        next_action = QAction("Next visual", menu)
        next_action.triggered.connect(self.next_mode)
        previous_action = QAction("Previous visual", menu)
        previous_action.triggered.connect(self.previous_mode)
        next_palette_action = QAction("Next palette", menu)
        next_palette_action.triggered.connect(self.next_palette)
        previous_palette_action = QAction("Previous palette", menu)
        previous_palette_action.triggered.connect(self.previous_palette)
        help_action = QAction("Show / hide help", menu)
        help_action.triggered.connect(self.toggle_help)
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self.quit)
        menu.addAction(next_action)
        menu.addAction(previous_action)
        menu.addAction(next_palette_action)
        menu.addAction(previous_palette_action)
        menu.addAction(help_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        self.tray_icon = QSystemTrayIcon(self.app.style().standardIcon(QStyle.StandardPixmap.SP_DesktopIcon), self)
        self.tray_icon.setToolTip(__app_name__)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def schedule_rebuild(self, *_args) -> None:
        self.rebuild_timer.start(350)

    def rebuild_windows(self) -> None:
        for window in self.windows:
            window.allow_close()
            window.close()
            window.deleteLater()
        self.windows = []
        monitors = self.monitor_manager.monitors()
        if not monitors:
            self.app.quit()
            return
        for monitor in monitors:
            primary_close_button = monitor.is_primary or len(monitors) == 1
            window = ScreensaverWindow(
                monitor=monitor,
                settings=self.settings,
                mode_name=self.current_mode,
                request_quit=self.quit,
                request_next_mode=self.next_mode,
                request_previous_mode=self.previous_mode,
                primary_close_button=primary_close_button,
            )
            self.windows.append(window)
            window.launch()

    def tick(self) -> None:
        now = time.perf_counter()
        delta_time = min(0.05, max(0.001, now - self.last_frame_time))
        self.last_frame_time = now
        for window in self.windows:
            window.tick(delta_time)

    def next_mode(self) -> None:
        self.mode_index = (self.mode_index + 1) % len(self.modes)
        self.apply_mode()

    def previous_mode(self) -> None:
        self.mode_index = (self.mode_index - 1) % len(self.modes)
        self.apply_mode()

    def next_palette(self) -> None:
        self.palette_index = (self.palette_index + 1) % len(self.palettes)
        self.apply_palette()

    def previous_palette(self) -> None:
        self.palette_index = (self.palette_index - 1) % len(self.palettes)
        self.apply_palette()

    def apply_mode(self) -> None:
        mode = self.current_mode
        for window in self.windows:
            window.set_mode(mode)
        save_last_mode(self.settings, mode)

    def apply_palette(self) -> None:
        self.settings = replace(self.settings, palette=self.current_palette)
        for window in self.windows:
            window.set_settings(self.settings)
        save_last_mode(self.settings, self.current_mode)

    def toggle_help(self) -> None:
        for window in self.windows:
            window.toggle_help()

    def quit(self) -> None:
        save_last_mode(self.settings, self.current_mode)
        self.timer.stop()
        if self.tray_icon is not None:
            self.tray_icon.hide()
        for window in self.windows:
            window.allow_close()
            window.close()
        self.app.quit()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802 - Qt override name
        if event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(watched, event)
        if not isinstance(event, QKeyEvent):
            return super().eventFilter(watched, event)
        key = event.key()
        modifiers = event.modifiers()
        has_control_alt = bool(modifiers & Qt.KeyboardModifier.ControlModifier) and bool(modifiers & Qt.KeyboardModifier.AltModifier)
        if has_control_alt and key == Qt.Key.Key_Q:
            self.quit()
            return True
        if has_control_alt and key == Qt.Key.Key_Right:
            self.next_mode()
            return True
        if has_control_alt and key == Qt.Key.Key_Left:
            self.previous_mode()
            return True
        if has_control_alt and key == Qt.Key.Key_Up:
            self.next_palette()
            return True
        if has_control_alt and key == Qt.Key.Key_Down:
            self.previous_palette()
            return True
        if has_control_alt and key == Qt.Key.Key_H:
            self.toggle_help()
            return True
        if self.settings.ignore_function_keys and Qt.Key.Key_F1 <= key <= Qt.Key.Key_F35:
            return True
        return True


def main(argv: list[str] | None = None) -> int:
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv if argv is None else [sys.argv[0], *argv])
    app.setApplicationName(__app_name__)
    app.setQuitOnLastWindowClosed(False)
    settings = load_settings(argv)
    controller = ScreensaverController(app, settings)
    controller.start()
    return app.exec()
