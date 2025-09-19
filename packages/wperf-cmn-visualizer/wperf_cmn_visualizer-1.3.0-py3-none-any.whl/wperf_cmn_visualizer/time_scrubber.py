# BSD 3-Clause License
#
# Copyright (c) 2025, Arm Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Time Line Scrubbing Module.

Instantiate a TimeScrubber widget which broadcasts a time scrubbing event.
Show Global data as a time line graph and present media buttons.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox, QToolButton, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QColor, QIcon, QPalette
import numpy as np
from typing import Any

from wperf_cmn_visualizer.canvas import Canvas
from wperf_cmn_visualizer.cmn_metrics import CMNMetrics
from wperf_cmn_visualizer.config import Config


class _GlobalTimelineSyncSignal(QObject):
    """Global signal object for synchronizing all timeline canvas instances."""
    time_changed = Signal(int)
_global_timeline_sync = _GlobalTimelineSyncSignal()


class TimelineCanvas(Canvas):
    """Widget for drawing the timeline graph and handling scrubbing."""

    def __init__(self, master: QWidget, time_stamps: np.ndarray,
                 values: np.ndarray, min_val: float, max_val: float, **kwargs):
        """
        Initialize the timeline canvas.
        Args:
            master: Parent widget
            time_stamps: Array of time values for x-axis
            values: Array of values for y-axis (line graph data)
            min_val: Minimum value for normalization
            max_val: Maximum value for normalization
            **kwargs: Additional widget configuration options
        """
        super().__init__(master, **kwargs)

        self.time_stamps = time_stamps
        self.values = values
        self.min_val = min_val
        self.max_val = max_val

        # state tracking
        self.current_time_index = 0
        self.handle_x = 0.0
        self.is_dragging = False
        self.is_hovering = False

        # text display tracking.
        self.show_text = False
        self.text_content = ""
        self.text_line_count = 0

        self.base_height = self.height()

        self.view.installEventFilter(self)
        self.view.viewport().installEventFilter(self)
        self.view.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        _global_timeline_sync.time_changed.connect(self._on_global_time_changed)

    def set_text_display(self, text: str, text_color: QColor, font_size: int, line_count: int):
        """
        Enable text display below the timeline.
        Args:
            text: Text to display (use \n for multiple lines)
            text_color: Color for the text
            font_size: Font size for the text
            line_count: Number of lines in the text
        """
        self.show_text = bool(text.strip())
        self.text_content = text
        self.text_color = text_color
        self.font_size = font_size
        self.text_line_count = line_count

        if self.show_text:
            text_height = self.get_text_height(font_size, line_count)
            self.setMinimumHeight(int(self.base_height + text_height))
        else:
            self.setMinimumHeight(int(self.base_height))

        self._draw_timeline()

    def clear_text_display(self):
        """Remove text display and return to original size."""
        self.show_text = False
        self.text_content = ""
        self.setMinimumHeight(int(self.base_height))
        self._draw_timeline()

    def _draw_timeline(self):
        """Draw the complete timeline using Canvas methods."""
        self.scene.clear()

        width = self.width()
        height = self.height()

        if width <= 1 or height <= 1 or len(self.values) == 0:
            return

        # Calculate timeline area, reserve space for text if needed
        timeline_height = height
        if self.show_text:
            text_height = self.get_text_height(self.font_size, self.text_line_count)
            timeline_height = height - text_height

        self._draw_graph_line_canvas(width, int(timeline_height))
        self._draw_scrubbing_handle_canvas(width, int(timeline_height))

        if self.show_text:
            self._draw_text_area(width, height, int(timeline_height))

    def _draw_text_area(self, width: int, height: int, timeline_height: int):
        """Draw text below the timeline."""
        text_height = self.get_text_height(self.font_size, self.text_line_count)
        text_start_y = timeline_height + (text_height / 2)  # Center vertically in text area
        self.draw_text(width / 2, text_start_y, self.text_content,
                    self.text_color, self.font_size)

    def _draw_graph_line_canvas(self, width: int, height: int) -> None:
        """Draw the graph line using Canvas drawing methods."""

        def show_no_data_avail_message():
            self.draw_text(
                width / 2,
                height / 2,
                "No data available",
                self.palette().color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text),
                Config.TOOLTIP_FONT_SIZE
            )

        if len(self.values) == 0:
            return
        values = np.array(self.values, dtype=float)

        # if all values are NaN, show no data message
        if np.all(np.isnan(values)):
            show_no_data_avail_message()
            return

        # Interpolate NaNs for plotting
        nans = np.isnan(values)
        if np.any(nans):
            x_idx = np.arange(len(values))
            values[nans] = np.interp(x_idx[nans], x_idx[~nans], values[~nans])

        # If self.min_val / self.max_val are NaN, fall back to calculated values
        min_val = self.min_val if not np.isnan(self.min_val) else np.nanmin(self.values)
        max_val = self.max_val if not np.isnan(self.max_val) else np.nanmax(self.values)

        if self.max_val <= self.min_val:
            show_no_data_avail_message()
            return

        # Normalise values
        normalized_y = (values - min_val) / (max_val - min_val)
        y_coords = (1.0 - normalized_y) * (height - 10) + 5

        # Normalise timestamps
        if len(self.time_stamps) > 0:
            max_time = np.nanmax(self.time_stamps)
            if max_time > 0:
                normalized_x = self.time_stamps / max_time
            else:
                normalized_x = np.linspace(0, 1, len(values))
        else:
            normalized_x = np.linspace(0, 1, len(values))

        x_coords = normalized_x * (width - 10) + 5
        for i in range(len(x_coords) - 1):
            # If either endpoint was originally NaN, mark the segment as interpolated
            is_interpolated = np.isnan(self.values[i]) or np.isnan(self.values[i+1])
            # draw interpollated segments in greyed out dashed line.
            if is_interpolated:
                line_color = self.palette().color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text)
                self._pen.setStyle(Qt.PenStyle.DotLine)
            else:
                line_color = QColor(70, 130, 180)
                self._pen.setStyle(Qt.PenStyle.SolidLine)

            self.draw_line(
                x_coords[i], y_coords[i], x_coords[i+1], y_coords[i+1],
                line_color, 2.0, scale_rate=0.0
            )

        self._pen.setStyle(Qt.PenStyle.SolidLine)

    def _draw_scrubbing_handle_canvas(self, width: int, height: int) -> None:
        """Draw the scrubbing handle using Canvas drawing methods."""
        if len(self.time_stamps) == 0:
            return

        max_time = np.max(self.time_stamps) if len(self.time_stamps) > 0 else 1
        current_time = self.time_stamps[self.current_time_index] if self.current_time_index < len(self.time_stamps) else 0
        self.handle_x = (current_time / max_time) * (width - 10) + 5

        if self.is_dragging or self.is_hovering:
            colour = QColor(220, 20, 60, 100)
            thickness = 8.0
        else:
            colour = QColor(220, 20, 60)
            thickness = 4.0
        self._pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.draw_line(self.handle_x, 7, self.handle_x, height-7,
                      colour, thickness, scale_rate=0.0)

    def update_data(self, time_stamps: np.ndarray, values: np.ndarray,
                   min_val: float, max_val: float):
        """Update the timeline data and refresh the display."""
        self.time_stamps = time_stamps
        self.values = values
        self.min_val = min_val
        self.max_val = max_val

        if self.current_time_index >= len(self.time_stamps):
            self.current_time_index = max(0, len(self.time_stamps) - 1)

        self._draw_timeline()

    def eventFilter(self, source, event):
        """Handle mouse and keyboard events from the graphics view."""
        if source in (self.view, self.view.viewport()):
            if event.type() == event.Type.KeyPress:
                if event.key() == Qt.Key.Key_Left:
                    self._scrub_previous()
                    return True
                elif event.key() == Qt.Key.Key_Right:
                    self._scrub_next()
                    return True

        if source is self.view.viewport():
            if event.type() == event.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    # Always scrub to clicked position, not just when near handle
                    x = event.position().x()
                    x = max(5, min(x, self.width() - 5))  # Clamp to valid range
                    new_index = self._get_nearest_time_index(x)
                    if new_index != self.current_time_index:
                        self.current_time_index = new_index
                        self._update_tooltip()
                        self._draw_timeline()
                        QTimer.singleShot(0, lambda: _global_timeline_sync.time_changed.emit(self.current_time_index))

                    # Start dragging from the new position
                    self.is_dragging = True
                    return True

            elif event.type() == event.Type.MouseMove:
                x = event.position().x()
                if self.is_dragging:
                    x = max(5, min(x, self.width() - 5))
                    new_index = self._get_nearest_time_index(x)
                    if new_index != self.current_time_index:
                        self.current_time_index = new_index
                        self._update_tooltip()
                        self._draw_timeline()
                        QTimer.singleShot(0, lambda: _global_timeline_sync.time_changed.emit(self.current_time_index))
                else:
                    was_hovering = self.is_hovering
                    self.is_hovering = self._is_near_handle(x)
                    if self.is_hovering != was_hovering:
                        self.setCursor(Qt.CursorShape.SizeHorCursor if self.is_hovering else Qt.CursorShape.ArrowCursor)
                        if self.is_hovering:
                            self._update_tooltip()
                        self._draw_timeline()
                return True

            elif event.type() == event.Type.MouseButtonRelease:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.is_dragging = False
                    self._draw_timeline()
                    return True

            elif event.type() == event.Type.Leave:
                if not self.is_dragging:
                    self.is_hovering = False
                    self.setCursor(Qt.CursorShape.ArrowCursor)
                    self.setToolTip("")
                    self._draw_timeline()
                return True

        return super().eventFilter(source, event)

    def _scrub_previous(self) -> None:
        """Move to the previous time index."""
        if self.current_time_index > 0:
            self.current_time_index -= 1
            self._update_tooltip()
            self._draw_timeline()
            QTimer.singleShot(0, lambda: _global_timeline_sync.time_changed.emit(self.current_time_index))

    def _scrub_next(self) -> None:
        """Move to the next time index."""
        if self.current_time_index < len(self.time_stamps) - 1:
            self.current_time_index += 1
            self._update_tooltip()
            self._draw_timeline()
            QTimer.singleShot(0, lambda: _global_timeline_sync.time_changed.emit(self.current_time_index))

    def set_time_index(self, index: int) -> None:
        """Set the current time index and update display."""
        if 0 <= index < len(self.time_stamps):
            self.current_time_index = index
            self._update_tooltip()
            self._draw_timeline()

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        self._draw_timeline()

    def _get_nearest_time_index(self, x: float) -> int:
        """
        Find the nearest time index for a given x coordinate.
        Args:
            x: X coordinate on the canvas.
        Returns:
            Closest index in time_stamps.
        """
        if len(self.time_stamps) == 0:
            return 0

        width = self.width()
        max_time = np.max(self.time_stamps)
        normalized_time = (x - 5) / (width - 10)
        target_time = normalized_time * max_time

        distances = np.abs(self.time_stamps - target_time)
        return int(np.argmin(distances))

    def _is_near_handle(self, x: float, tolerance: int = 10) -> bool:
        """
        Check if mouse is near the scrubbing handle.
        Args:
            x: Mouse x coordinate.
            tolerance: Pixel tolerance for proximity.
        Returns:
            True if mouse is near the handle, else False.
        """
        return abs(x - self.handle_x) <= tolerance

    def _update_tooltip(self) -> None:
        """Update tooltip with current timestamp value."""
        if 0 <= self.current_time_index < len(self.time_stamps) and self.is_hovering:
            time_value = self.time_stamps[self.current_time_index]
            self.setToolTip(f"Time: {time_value:.3f}(s)")
        else:
            self.setToolTip("")

    def _on_global_time_changed(self, time_index: int) -> None:
        """Handle time changes from the global sync signal."""
        if time_index != self.current_time_index:
            self.current_time_index = time_index
            self._update_tooltip()
            self._draw_timeline()


class TimeScrubber(QWidget):
    """Status bar widget with media playback controls and custom render area."""

    def __init__(self, master: QWidget, cmn_metrics: CMNMetrics, height: int,
                 metric_idx: int = 0, mesh_idx: int = 0, **kwargs: Any) -> None:
        """
        Initialize the time scrubber.
        Args:
            master: Parent widget
            cmn_metrics: Metrics data source
            height: Desired height of the widget
            metric_idx: Index of the metric to display (default: 0)
            mesh_idx: Index of the mesh to display (default: 0)
            **kwargs: Additional configuration options
        """
        super().__init__(master)
        self.master = master
        self.cmn_metrics = cmn_metrics
        self.desired_height = height
        self.metric_idx = metric_idx
        self.mesh_idx = mesh_idx

        # Playback state
        self.is_playing = False
        self.playback_speed = 1.0
        self.current_time_index = 0

        # Timer for playback
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self._play_next_frame)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setFixedHeight(self.desired_height)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 2, 5, 2)
        self._create_media_controls(main_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setLineWidth(1)
        main_layout.addWidget(separator)

        # Extract data from CMNMetrics for the new interface
        time_stamps = self.cmn_metrics.time_stamps
        values = self.cmn_metrics.global_data[:, self.metric_idx, self.mesh_idx]
        min_val = np.min(values) if len(values) > 0 else 0
        max_val = np.max(values) if len(values) > 0 else 1

        # Connect to global sync signal to stay synchronized
        _global_timeline_sync.time_changed.connect(self._on_global_time_changed)

        self.timeline_canvas = TimelineCanvas(
            self.master,
            time_stamps=time_stamps,
            values=values,
            min_val=min_val,
            max_val=max_val
        )
        main_layout.addWidget(self.timeline_canvas, 1)

    def _on_global_time_changed(self, time_index: int) -> None:
        """Handle time changes from the global sync signal."""
        if time_index != self.current_time_index:
            self.current_time_index = time_index

    def _create_media_controls(self, parent_layout: QHBoxLayout) -> None:
        """Create playback control buttons."""

        def create_button(icon_name: str, tooltip: str, callback):
            btn = QToolButton()
            btn.setIcon(QIcon.fromTheme(icon_name))
            btn.setToolTip(tooltip)
            btn.setAutoRaise(True)
            btn.setFixedSize(30, 30)
            btn.clicked.connect(callback)
            parent_layout.addWidget(btn)
            return btn

        self.play_button = create_button("media-playback-start", "Play/Pause", self._on_play_pause)
        self.stop_button = create_button("media-playback-stop", "Stop", self._on_stop)
        self.prev_button = create_button("media-skip-backward", "Previous", self._on_previous)
        self.next_button = create_button("media-skip-forward", "Next", self._on_next)

        # Speed combobox remains unchanged
        self.speed_combobox = QComboBox()
        self.speed_values = ["0.25x", "0.5x", "1x", "1.5x", "2x", "4x", "16x", "64x"]
        self.speed_combobox.addItems(self.speed_values)
        self.speed_combobox.setCurrentText("1x")
        self.speed_combobox.setFixedHeight(30)
        self.speed_combobox.currentTextChanged.connect(self._on_speed_change)
        parent_layout.addWidget(self.speed_combobox)

    def _on_play_pause(self) -> None:
        """Toggle playback state and update play button icon."""
        self.is_playing = not self.is_playing
        icon_name = "media-playback-pause" if self.is_playing else "media-playback-start"
        self.play_button.setIcon(QIcon.fromTheme(icon_name))
        if self.is_playing:
            self._start_playback()
        else:
            self.playback_timer.stop()

    def _start_playback(self) -> None:
        """Start playback from current position."""
        if self.current_time_index < len(self.cmn_metrics.time_stamps) - 1:
            self._schedule_next_frame()
        else:
            self.is_playing = False
            self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))

    def _schedule_next_frame(self) -> None:
        """Schedule the next frame based on time delta."""
        if not self.is_playing or self.current_time_index >= len(self.cmn_metrics.time_stamps) - 1:
            return
        t_current = self.cmn_metrics.time_stamps[self.current_time_index]
        t_next = self.cmn_metrics.time_stamps[self.current_time_index + 1]
        delay = max(1, int(((t_next - t_current) * 1000) / self.playback_speed))
        self.playback_timer.start(delay)

    def _play_next_frame(self) -> None:
        """Advance playback by one frame."""
        self.playback_timer.stop()
        if not self.is_playing:
            return
        if self.current_time_index < len(self.cmn_metrics.time_stamps) - 1:
            self.current_time_index += 1
            self.timeline_canvas.set_time_index(self.current_time_index)
            _global_timeline_sync.time_changed.emit(self.current_time_index)

            if self.current_time_index < len(self.cmn_metrics.time_stamps) - 1:
                self._schedule_next_frame()
            else:
                self.is_playing = False
                self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))
        else:
            self.is_playing = False
            self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))

    def _on_stop(self) -> None:
        """Stop playback, reset time index and update UI."""
        self.is_playing = False
        self.playback_timer.stop()
        self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.current_time_index = 0
        self.timeline_canvas.set_time_index(self.current_time_index)
        _global_timeline_sync.time_changed.emit(self.current_time_index)

    def _on_previous(self) -> None:
        """Go to previous time index if possible."""
        if self.current_time_index > 0:
            self.current_time_index -= 1
            self.timeline_canvas.set_time_index(self.current_time_index)
            _global_timeline_sync.time_changed.emit(self.current_time_index)

    def _on_next(self) -> None:
        """Go to next time index if possible."""
        if self.current_time_index < len(self.cmn_metrics.time_stamps) - 1:
            self.current_time_index += 1
            self.timeline_canvas.set_time_index(self.current_time_index)
            _global_timeline_sync.time_changed.emit(self.current_time_index)

    def _on_speed_change(self, speed_text: str) -> None:
        """Update playback speed based on combobox selection."""
        try:
            speed = float(speed_text.replace("x", ""))
            # catch case with NaN. In python NaN != NaN
            if speed != speed or speed <= 0:
                raise ValueError("Invalid speed")
            self.playback_speed = speed

            if self.is_playing:
                self.playback_timer.stop()
                self._schedule_next_frame()

        except ValueError:
            self.playback_speed = 1.0  # fallback
