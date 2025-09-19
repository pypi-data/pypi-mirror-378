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
Main Renderer module for rendering CMN to main body.
"""
from PySide6.QtWidgets import QWidget, QApplication, QGraphicsDropShadowEffect
from PySide6.QtGui import QPalette, QColor, QCursor
from PySide6.QtCore import Qt, QTimer
import numpy as np
from typing import Optional, Tuple, List
from enum import IntEnum
from math import log10, floor, ceil

from wperf_cmn_visualizer.canvas import Canvas, ZoomPanCanvas
from wperf_cmn_visualizer.hit_test import HitTest
from wperf_cmn_visualizer.cmn import CMN
from wperf_cmn_visualizer.cmn_metrics import CMNMetrics
from wperf_cmn_visualizer.config import Config
from wperf_cmn_visualizer.time_scrubber import TimelineCanvas


class CMNRenderer:
    """
    Handles the rendering of a CMN onto a ZoomPanCanvas widget.
    Viewport-culling optimisation.
    Handles level of detail using zoom scale (more detail for higher zoom).
    Handles Mouse hover interaction.
    """
    dtc_color_map: List[QColor] = [
        QColor("#44AA99"),
        QColor("#549EC2"),
        QColor("#C5B45E"),
        QColor("#BE5D6D"),
        QColor("#117733"),
        QColor("#332288"),
        QColor("#B731A1"),
        QColor("#815911"),
    ]
    """
    Accessible Colour map for distinguishing DTC domains.
    Reference: https://davidmathlogic.com/colorblind
    """

    class CMNNodeType(IntEnum):
        NONE = 0
        XP = 1
        PORT = 2
        DEVICE = 3

    CMNNodeTypeData = np.dtype([
        ('type', np.uint8),
        ('x', np.uint8),
        ('y', np.uint8),
        ('port', np.uint8),
        ('device', np.uint8),
    ])

    def __init__(self, master: QWidget, palette: QPalette, cmn: CMN, cmn_metrics: Optional[CMNMetrics]):
        """
        Args:
            root (Qwidget): The parent window.
            cmn (CMN): The computational mesh network object containing mesh data.
            cmn_metrics (Optional[CMNMetrics]): Optional metrics data for coloring.
            palette (QPalette): QPalette for consistent theming.
        """
        self.cmn_idx: int = 0
        self.cmn: CMN = cmn
        self.palette: QPalette = palette
        self._setup_theme_colors()

        self.has_been_seen: bool = False
        self.canvas: ZoomPanCanvas = ZoomPanCanvas(master, self._render_all, self._handle_hover)

        self._setup_colormap_overlay()
        self.canvas.resize_callback = lambda _: self._render_colormap_overlay()
        self.canvas.double_click_callback = lambda *_: self.canvas._home_position_and_render()

        self.hit_test: HitTest = HitTest(CMNRenderer.CMNNodeTypeData, 256)
        self._setup_tooltip()

        # cmn metrics initialisations
        self.cmn_metrics_time_idx: int = 0
        self.cmn_metrics_metric_id: int = 0
        self.cmn_metrics: Optional[CMNMetrics] = cmn_metrics

    def _setup_theme_colors(self) -> None:
        """Extract and setup theme colors from QPalette with proper dark/light mode handling."""
        window_color = self.palette.color(QPalette.ColorRole.Window)
        base_color = self.palette.color(QPalette.ColorRole.Base)
        text_color = self.palette.color(QPalette.ColorRole.Text)

        window_brightness = (window_color.red() + window_color.green() + window_color.blue()) / 3
        self.is_dark_mode = window_brightness < 128

        if self.is_dark_mode:
            self.grid_color = self.palette.color(QPalette.ColorRole.Light)
            self.outline_color = self.palette.color(QPalette.ColorRole.Light)
        else:
            self.grid_color = self.palette.color(QPalette.ColorRole.Dark)
            self.outline_color = self.palette.color(QPalette.ColorRole.Dark)

        self.text_color = text_color
        self.ui_bg_color = base_color
        self.black_color = QColor("black")
        self.white_color = QColor("white")

    def _setup_colormap_overlay(self):
        """Setup a simple floating colormap overlay."""
        self.colormap_canvas = Canvas(self.canvas)
        self.colormap_canvas.setContentsMargins(0, 0, 0, 0)
        self.colormap_canvas.raise_()

    def _setup_tooltip(self):
        """Initialise tooltip UI and state."""
        # Tool tips will appear on top level window.
        # Window is transparent and frameless
        self._tooltip_window = QWidget()
        self._tooltip_window.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint
        )
        self._tooltip_window.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self._tooltip_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._tooltip_window.hide()

        # Create canvas for the tooltip window
        self._tooltip_canvas = Canvas(self._tooltip_window)
        self._tooltip_canvas.setContentsMargins(0, 0, 0, 0)
        self._tooltip_canvas.setStyleSheet(f"""
            background-color: {self.palette.color(QPalette.ColorRole.ToolTipBase).name()};
            color: {self.palette.color(QPalette.ColorRole.ToolTipText).name()};
            border-radius: 6px;
        """)
        self._tooltip_canvas.hide()

        # Add drop shadow to the tooltip canvas
        shadow = QGraphicsDropShadowEffect(self._tooltip_canvas)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(2, 2)
        self._tooltip_canvas.setGraphicsEffect(shadow)

        # Create Timeline Canvas for showing timeline per device
        self._timeline_canvas = TimelineCanvas(
            self._tooltip_window, np.array([]), np.array([]), 0.0, 0.0
        )
        self._timeline_canvas.setContentsMargins(0, 0, 0, 0)
        self._timeline_canvas.setStyleSheet(f"""
            background-color: {self.palette.color(QPalette.ColorRole.ToolTipBase).name()};
            border-radius: 6px;
        """)
        self._timeline_canvas.hide()

        # Add drop shadow to timeline canvas
        timeline_shadow = QGraphicsDropShadowEffect(self._timeline_canvas)
        timeline_shadow.setBlurRadius(10)
        timeline_shadow.setColor(QColor(0, 0, 0, 150))
        timeline_shadow.setOffset(2, 2)
        self._timeline_canvas.setGraphicsEffect(timeline_shadow)

        self._tooltip_delay = QApplication.style().styleHint(
            QApplication.style().StyleHint.SH_ToolTip_WakeUpDelay
        )
        self._tooltip_data = None
        self._tooltip_active = False
        self._tooltip_timer = QTimer(singleShot=True)
        self._tooltip_timer.timeout.connect(self._on_tooltip_timeout)

        # Add state tracking for timeline mode
        self._timeline_mode: bool = False
        self._timeline_data = None

        self.canvas.right_click_callback = self._on_right_click
        self.canvas.left_click_callback = self._on_left_click

    @property
    def current_mesh(self) -> np.ndarray:
        """
        Returns:
            CMNMesh: The active mesh object from the CMN.
        """
        return self.cmn.meshes[self.cmn_idx]

    def _on_time_changed(self, time_idx: int):
        if self.cmn_metrics is None:
            return
        self.cmn_metrics_time_idx = time_idx
        self._render_all()

        # Update timeline text if in timeline mode
        if self._timeline_mode and self._timeline_data is not None:
            data = self._timeline_data
            current_base_idx = (time_idx, self.cmn_metrics_metric_id, self.cmn_idx, data["y"], data["x"])

            node_type = data["type"]
            if node_type == CMNRenderer.CMNNodeType.XP:
                arr = self.cmn_metrics.xp_data
                extra_idx = ()
            elif node_type == CMNRenderer.CMNNodeType.PORT:
                arr = self.cmn_metrics.port_data
                extra_idx = (data["port"],)
            elif node_type == CMNRenderer.CMNNodeType.DEVICE:
                arr = self.cmn_metrics.device_data
                extra_idx = (data["port"], data["device"])
            else:
                return

            current_value = arr[current_base_idx + extra_idx]
            unit = self.cmn_metrics.metric_units[self.cmn_metrics_metric_id]
            caption = f"{current_value:.6f} ({unit})" if not np.isnan(current_value) else "No Value"
            self._timeline_canvas.set_text_display(caption, self.text_color, Config.TOOLTIP_FONT_SIZE, 1)

    def grid_to_world(self, row: int, col: int) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates with dynamic cell size."""
        cell_size = self.canvas.get_dynamic_grid_cell_size()
        return (col * cell_size, (int(self.current_mesh["y_dim"]) - row) * cell_size)

    def world_to_grid(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates with dynamic cell size."""
        cell_size = self.canvas.get_dynamic_grid_cell_size()
        return (
            int(self.current_mesh["y_dim"]) - int(round(world_y / cell_size)),
            int(round(world_x / cell_size))
        )

    def get_visible_bounds(self) -> Tuple[int, int, int, int]:
        """
        Get the grid bounds of the currently visible viewport, with extra padding.
        Extra padding ensures elements near by are rendered and dont appear suddenly;
        This prevents any flickering (smoother zooming and panning experience)
        Returns:
            Tuple[int, int, int, int]: (min_row, max_row, min_col, max_col) bounds.
        """
        cell_size = self.canvas.get_dynamic_grid_cell_size()
        # Calculate visible bounds in world coordinates
        canvas_left = -self.canvas.offset_x / self.canvas.zoom_scale
        canvas_bottom = -self.canvas.offset_y / self.canvas.zoom_scale
        canvas_right = (self.canvas.view.viewport().width() - self.canvas.offset_x) / self.canvas.zoom_scale
        canvas_top = (self.canvas.view.viewport().height() - self.canvas.offset_y) / self.canvas.zoom_scale

        # Add padding as a factor of the canvas size
        padding = max(canvas_right - canvas_left, canvas_top - canvas_bottom) // 3

        # Convert to grid coordinates with bounds checking using dynamic cell size
        min_col = max(0, int((canvas_left - padding) / cell_size))
        max_col = min(int(self.current_mesh["x_dim"]) - 1, int((canvas_right + padding) / cell_size))
        max_row = min(
            int(self.current_mesh["y_dim"]) - 1,
            int(self.current_mesh["y_dim"]) - int((canvas_bottom - padding) / cell_size)
        )
        min_row = max(
            0,
            int(self.current_mesh["y_dim"]) - int((canvas_top + padding) / cell_size)
        )
        return min_row, max_row, min_col, max_col

    def _on_right_click(self, wx: float, wy: float) -> None:
        """
        Handle right click events.
        Hit test and show timeline for device.
        """
        if self.cmn_metrics is None:
            return

        hit_data = self.hit_test.hit_test(wx, wy)
        if hit_data:
            self._show_timeline(hit_data, wx, wy)

    def _on_left_click(self, wx: float, wy: float) -> None:
        """
        Handle left click events.
        Close Timeline window if open.
        """
        if self._timeline_mode:
            self._exit_timeline_mode()

    def _exit_timeline_mode(self) -> None:
        """Exit timeline mode and return to normal tooltip behavior."""
        self._timeline_mode = False
        self._timeline_data = None
        self._tooltip_window.hide()
        self._timeline_canvas.hide()
        self._timeline_canvas.clear_text_display()
        self._tooltip_canvas.show()

    def _handle_hover(self, wx: float, wy: float) -> None:
        """Process hover events with delayed show/hide logic."""
        # early exit if timeline window open.
        if self._timeline_mode:
            return

        new_data = self.hit_test.hit_test(wx, wy)

        if new_data == self._tooltip_data:
            return

        self._tooltip_data = new_data
        self._tooltip_timer.stop()

        if new_data:
            if self._tooltip_active:
                self._show_tooltip(new_data)
            else:
                self._tooltip_timer.start(self._tooltip_delay)
        else:
            if self._tooltip_active:
                self._tooltip_timer.start(self._tooltip_delay)
            else:
                self._tooltip_window.hide()

    def _on_tooltip_timeout(self):
        """Timer expiry — either show or hide tooltip."""
        if self._timeline_mode:
            return

        if self._tooltip_data:
            self._tooltip_active = True
            self._show_tooltip(self._tooltip_data)
        else:
            self._tooltip_active = False
            self._tooltip_window.hide()

    def _show_tooltip(self, data):
        """Render and position tooltip with centered text."""

        # early return if in timeline mode
        if self.cmn_metrics is None or self._timeline_mode:
            return

        base_idx = (self.cmn_metrics_time_idx,
                    self.cmn_metrics_metric_id,
                    self.cmn_idx,
                    data["y"], data["x"])
        node_type = data["type"]
        if node_type == CMNRenderer.CMNNodeType.XP:
            arr = self.cmn_metrics.xp_data
            extra_idx = ()
        elif node_type == CMNRenderer.CMNNodeType.PORT:
            arr = self.cmn_metrics.port_data
            extra_idx = (data["port"],)
        elif node_type == CMNRenderer.CMNNodeType.DEVICE:
            arr = self.cmn_metrics.device_data
            extra_idx = (data["port"], data["device"])
        else:
            self._tooltip_window.hide()
            return
        unit = self.cmn_metrics.metric_units[self.cmn_metrics_metric_id]
        value = arr[base_idx + extra_idx]
        text = f"{value:.6f} ({unit})" if not np.isnan(value) else "No Value"

        if not text:
            self._tooltip_window.hide()
            return

        # Show tooltip canvas, hide timeline canvas
        self._tooltip_canvas.show()
        self._timeline_canvas.hide()

        # Measure text and resize
        text_width = self._tooltip_canvas.get_text_width(text, Config.TOOLTIP_FONT_SIZE)
        text_height = self._tooltip_canvas.get_text_height(Config.TOOLTIP_FONT_SIZE)
        canvas_width = text_width + (Config.TOOLTIP_PADDING * 2)
        canvas_height = text_height + (Config.TOOLTIP_PADDING * 2)

        self._tooltip_canvas.resize(int(canvas_width), int(canvas_height))
        shadow_padding = 20
        self._tooltip_window.resize(int(canvas_width + shadow_padding), int(canvas_height + shadow_padding))
        self._tooltip_canvas.move(shadow_padding//2, shadow_padding//2)

        # Clear and draw
        self._tooltip_canvas.scene.clear()
        self._tooltip_canvas.draw_text(canvas_width / 2, canvas_height / 2, text, self.text_color, Config.TOOLTIP_FONT_SIZE)

        # Position at cursor with screen bounds checking
        cursor_pos = QCursor.pos()
        tooltip_x = cursor_pos.x() + 10
        tooltip_y = cursor_pos.y() - 10

        screen = QApplication.primaryScreen().availableGeometry()
        if tooltip_x + canvas_width > screen.right():
            tooltip_x = cursor_pos.x() - canvas_width - 10
        if tooltip_y + canvas_height > screen.bottom():
            tooltip_y = cursor_pos.y() - canvas_height - 10

        self._tooltip_window.move(int(tooltip_x), int(tooltip_y))
        self._tooltip_window.show()
        self._tooltip_window.raise_()

    def _show_timeline(self, data, wx: float, wy: float) -> None:
        """
        Show detailed timeline canvas within tooltip window.
        Grab device level data.
        """
        if self.cmn_metrics is None:
            return

        # Enter timeline mode
        self._timeline_mode = True
        self._timeline_data = data
        self._tooltip_active = False
        self._tooltip_timer.stop()

        base_idx = (slice(None), self.cmn_metrics_metric_id, self.cmn_idx, data["y"], data["x"])
        current_base_idx = (self.cmn_metrics_time_idx, self.cmn_metrics_metric_id, self.cmn_idx, data["y"], data["x"])

        node_type = data["type"]
        if node_type == CMNRenderer.CMNNodeType.XP:
            arr = self.cmn_metrics.xp_data
            extra_idx = ()
        elif node_type == CMNRenderer.CMNNodeType.PORT:
            arr = self.cmn_metrics.port_data
            extra_idx = (data["port"],)
        elif node_type == CMNRenderer.CMNNodeType.DEVICE:
            arr = self.cmn_metrics.device_data
            extra_idx = (data["port"], data["device"])
        else:
            return

        time_series_values = arr[base_idx + extra_idx]
        current_value = arr[current_base_idx + extra_idx]
        min_val, max_val = self.cmn_metrics.get_metric_min_max(self.cmn_metrics_metric_id, self.cmn_idx)

        # hide tooltip cnavas, show timeline canvas
        self._tooltip_canvas.hide()
        self._timeline_canvas.show()

        # Update timeline data
        self._timeline_canvas.update_data(
            self.cmn_metrics.time_stamps,
            time_series_values,
            min_val,
            max_val
        )

        # set timeline canvas text display.
        unit = self.cmn_metrics.metric_units[self.cmn_metrics_metric_id]
        caption = f"{current_value:.6f} ({unit})" if not np.isnan(current_value) else "No Value"
        self._timeline_canvas.set_text_display(caption, self.text_color, Config.TOOLTIP_FONT_SIZE, 1)

        # Size and position
        caption_width = self._timeline_canvas.get_text_width(caption, Config.TOOLTIP_FONT_SIZE) + Config.TOOLTIP_PADDING
        timeline_width = max(int(caption_width), Config.TIMELINE_BASE_WIDTH)
        shadow_padding = 20

        self._timeline_canvas.resize(timeline_width, Config.TIMELINE_HEIGHT)
        self._tooltip_window.resize(timeline_width + shadow_padding, Config.TIMELINE_HEIGHT + shadow_padding)
        self._timeline_canvas.move(shadow_padding//2, shadow_padding//2)

        cursor_pos = QCursor.pos()
        tooltip_x = cursor_pos.x() + 10
        tooltip_y = cursor_pos.y() - 10

        screen = QApplication.primaryScreen().availableGeometry()
        if tooltip_x + timeline_width > screen.right():
            tooltip_x = cursor_pos.x() - timeline_width - 10
        if tooltip_y + Config.TIMELINE_HEIGHT > screen.bottom():
            tooltip_y = cursor_pos.y() - Config.TIMELINE_HEIGHT - 10

        self._tooltip_window.move(int(tooltip_x), int(tooltip_y))
        self._tooltip_window.show()
        self._tooltip_window.raise_()

    def _render_colormap_overlay(self):
        """
        Render the gradient colormap vertically on the right.
        Add Unit string and formatted min max values.
        Unit string is only rendered if there is enough space for it.
        """
        if self.cmn_metrics is None:
            self.colormap_canvas.hide()
            return

        min_val, max_val = self.cmn_metrics.get_metric_min_max(self.cmn_metrics_metric_id, self.cmn_idx)

        # Calculate nice display range
        if min_val == max_val:
            display_min, display_max = min_val, max_val
        else:
            range_size = max_val - min_val

            # snap to zero if close, otherwise round down
            if min_val >= 0 and min_val < Config.CMAP_MIN_SNAP_THRESHOLD * range_size:
                display_min = 0
            else:
                magnitude = 10 ** floor(log10(abs(min_val)))
                display_min = floor(min_val / magnitude) * magnitude

            # round up to nice number
            magnitude = 10 ** floor(log10(abs(max_val)))
            display_max = ceil(max_val / magnitude) * magnitude

        # Format values nicely
        def format_val(val):
            if val == 0:
                return "0"
            abs_val = abs(val)
            if abs_val >= 1e6 or abs_val < 1e-3:
                return f"{val:.1e}"
            elif abs_val >= 1000:
                return f"{val:.0f}"
            elif abs_val >= 1:
                return f"{val:.3g}"
            else:
                return f"{val:.3g}"

        min_str = format_val(display_min)
        max_str = format_val(display_max)
        unit_str = self.cmn_metrics.metric_units[self.cmn_metrics_metric_id]

        # Calculate dimensions
        text_height = self.colormap_canvas.get_text_height(Config.CMAP_FONT_SIZE)
        width = int(text_height + Config.TOOLTIP_PADDING)

        parent_rect = self.canvas.rect()
        height = parent_rect.height() - (Config.CMAP_PADDING * 2)

        # Setup canvas
        self.colormap_canvas.resize(width, height)
        self.colormap_canvas.scene.clear()

        # Apply gradient styling
        window_bg = self.palette.color(QPalette.ColorRole.Window)
        self.colormap_canvas.setStyleSheet(f"""
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 rgba(255, 0, 0, {Config.CMAP_GRADIENT_ALPHA}),
                                    stop: 1 rgba({window_bg.red()}, {window_bg.green()}, {window_bg.blue()}, {Config.CMAP_GRADIENT_ALPHA}));
            border: 1px solid {self.grid_color.name()};
            border-radius: {width // Config.CMAP_BORDER_RADIUS_DIVISOR}px;
        """)

        # Draw text
        text_x = width / 2 - Config.CMAP_TEXT_OFFSET
        max_str_width = self.colormap_canvas.get_text_width(max_str, Config.CMAP_FONT_SIZE)
        min_str_width = self.colormap_canvas.get_text_width(min_str, Config.CMAP_FONT_SIZE)
        unit_str_width = self.colormap_canvas.get_text_width(unit_str, Config.CMAP_FONT_SIZE)

        self.colormap_canvas.draw_text(
            text_x, max_str_width / 2 + Config.TOOLTIP_PADDING,
            max_str,
            self.text_color, Config.CMAP_FONT_SIZE, angle=-90
        )
        self.colormap_canvas.draw_text(
            text_x, height - min_str_width / 2 - Config.TOOLTIP_PADDING,
            min_str,
            self.text_color, Config.CMAP_FONT_SIZE, angle=-90
        )

        if height > (max_str_width + min_str_width + unit_str_width + 4 * Config.CMAP_PADDING):
            self.colormap_canvas.draw_text(
                text_x, height / 2,
                unit_str,
                self.text_color, Config.CMAP_FONT_SIZE, angle=-90
            )

        # Position and show
        self.colormap_canvas.move(parent_rect.width() - width - Config.CMAP_PADDING, Config.CMAP_PADDING)
        self.colormap_canvas.show()

    def _render_all(self) -> None:
        """
        Render Callback Function.
        """
        if self.canvas.isVisible():
            if not self.has_been_seen:
                self.has_been_seen = True
                self.canvas._set_home_position()

            self.canvas.scene.clear()
            self.hit_test.clear()
            if not self._timeline_mode:
                self._tooltip_window.hide()
            self._render_grid_lines()
            self._render_nodes()

    def _render_grid_lines(self) -> None:
        """Render all grid lines (no viewport culling)."""
        min_row, max_row = 0, int(self.current_mesh["y_dim"]) - 1
        min_col, max_col = 0, int(self.current_mesh["x_dim"]) - 1

        # Render vertical lines
        for col in range(min_col, max_col + 1):
            x, _ = self.grid_to_world(0, col)
            _, y_start = self.grid_to_world(min_row, 0)
            _, y_end = self.grid_to_world(max_row, 0)

            self.canvas.draw_line(
                x, y_start, x, y_end,
                color=self.grid_color,
                thickness=Config.GRID_LINE_WIDTH,
            )

        # Render horizontal lines
        for row in range(min_row, max_row + 1):
            _, y = self.grid_to_world(row, 0)
            x_start, _ = self.grid_to_world(0, min_col)
            x_end, _ = self.grid_to_world(0, max_col)

            self.canvas.draw_line(
                x_start, y, x_end, y,
                color=self.grid_color,
                thickness=Config.GRID_LINE_WIDTH,
            )

    @staticmethod
    def darken_colour(hex_colour: str, factor: float = 1.2) -> str:
        """Darken a hex colour by dividing each RGB channel by `factor`."""
        hex_colour = hex_colour.lstrip("#")
        r = min(int(int(hex_colour[0:2], 16) / factor), 255)
        g = min(int(int(hex_colour[2:4], 16) / factor), 255)
        b = min(int(int(hex_colour[4:6], 16) / factor), 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def brighten_colour(hex_colour: str, factor: float = 1.3) -> str:
        """Brighten a hex colour by multiplying each RGB channel by `factor`."""
        hex_colour = hex_colour.lstrip("#")
        r = min(int(int(hex_colour[0:2], 16) * factor), 255)
        g = min(int(int(hex_colour[2:4], 16) * factor), 255)
        b = min(int(int(hex_colour[4:6], 16) * factor), 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _get_node_color(self, xp_x: int, xp_y: int, dtc: int) -> QColor:
        """Get the appropriate color for a node based on metrics or DTC domain."""
        if self.cmn_metrics is not None:
            return self.cmn_metrics.get_xp_colour(
                self.cmn_metrics_time_idx,
                self.cmn_metrics_metric_id,
                self.cmn_idx,
                xp_y,
                xp_x
            )
        else:
            return CMNRenderer.dtc_color_map[dtc % len(CMNRenderer.dtc_color_map)]

    def _get_port_color(self, xp_x: int, xp_y: int, port_index: int) -> QColor:
        """Get the appropriate color for a port based on metrics or default."""
        if self.cmn_metrics is not None:
            return self.cmn_metrics.get_port_colour(
                self.cmn_metrics_time_idx,
                self.cmn_metrics_metric_id,
                self.cmn_idx,
                xp_y,
                xp_x,
                port_index
            )
        else:
            return self.ui_bg_color

    def _get_device_color(self, xp_x: int, xp_y: int, port_index: int, device_index: int) -> QColor:
        """Get the appropriate color for a device based on metrics or default."""
        if self.cmn_metrics is not None:
            return self.cmn_metrics.get_device_colour(
                self.cmn_metrics_time_idx,
                self.cmn_metrics_metric_id,
                self.cmn_idx,
                xp_y,
                xp_x,
                port_index,
                device_index
            )
        else:
            return self.ui_bg_color

    # static rendering constants cache
    offsets = {
        0: (-1, 1),   # south west
        1: (1, -1),   # north east
        2: (1, 1),    # south east
        3: (-1, -1),  # north west
    }
    label_offsets = {
        0: (2.5, -2.0),
        1: (-2.5, 2.0),
        2: (-2.5, -2.0),
        3: (2.5, 2.0),
    }
    len_div_sqrt2 = Config.XP_PORT_LINE_LEN / np.sqrt(2)
    coord_str_font_size = 4  # used for coordinate box and nodeid

    def _render_nodes(self) -> None:
        """
        Render all visible nodes within the viewport. Includes:
        - Square XP node rendering with hover highlighting.
        - DTC-based colour assignment or heatmap colors.
        - Additional text annotations when zoomed in.
        """
        def draw_node(x, y, node_xp, isHovered):
            """
            +-------+
            |       |
            |     <- base_colour
            |       |
            +-------+ <- node
            """
            xp_x = node_xp["node_info"]["coord"]["x"]
            xp_y = node_xp["node_info"]["coord"]["y"]
            dtc = node_xp["dtc_domain"]
            node_colour = self._get_node_color(xp_x, xp_y, dtc)
            node_size_double = Config.XP_NODE_SQUARE_SIZE * 2
            self.canvas.draw_rectangle(
                x, y,
                node_size_double,
                node_size_double,
                node_colour,
                outline_color=self.outline_color,
                outline_thickness=Config.XP_OUTLINE_WIDTH,
            )
            self.hit_test.add_rect(x, y, node_size_double, node_size_double, (CMNRenderer.CMNNodeType.XP, xp_x, xp_y, 0, 0))

        def draw_coord_node_id_labels(x, y, node_xp):
            """
                     +-----+
            +--------|(0,0)| <- coord_string
            |        +-----+ <= coord_str box
            |           |
            |    XP     |
            |           |
            +-----------+
            Look through ports, find empty ports to draw
            either a box with coordinates or box with node-id.
            This is designed to remain persistent accross all zoom Levels so it uses slower scaling.
            """
            types = node_xp["ports"]["type"][:4]
            empty_ports = np.where(types == 0)

            if empty_ports[0].size > 0:
                port_index = empty_ports[0][0]
                dx, dy = CMNRenderer.offsets[port_index]
            else:
                dx = 0
                dy = 1

            coord_box_x = x + dx * Config.XP_NODE_SQUARE_SIZE
            coord_box_y = y + dy * Config.XP_NODE_SQUARE_SIZE
            coordx = node_xp["node_info"]["coord"]["x"]
            coordy = node_xp["node_info"]["coord"]["y"]
            coord_str = f"({coordx},{coordy})"
            width = self.canvas.get_text_width(coord_str, CMNRenderer.coord_str_font_size, scale_rate=0.5) + Config.XP_NODEID_COORD_PADDING
            height = self.canvas.get_text_height(CMNRenderer.coord_str_font_size, scale_rate=0.5) + Config.XP_NODEID_COORD_PADDING

            self.canvas.draw_rectangle(
                coord_box_x, coord_box_y,
                width, height,
                self.black_color,
                scale_rate=0.5,
            )
            self.canvas.draw_text(
                coord_box_x, coord_box_y,
                coord_str,
                self.white_color, CMNRenderer.coord_str_font_size,
                scale_rate=0.5,
            )

            if empty_ports[0].size > 1:
                second_port_index = empty_ports[0][1]
                dx2, dy2 = CMNRenderer.offsets[second_port_index]
            else:
                dx2 = 0
                dy2 = -1

            node_id_box_x = x + dx2 * Config.XP_NODE_SQUARE_SIZE
            node_id_box_y = y + dy2 * Config.XP_NODE_SQUARE_SIZE

            node_id = f'{node_xp["node_info"]["nodeid"]}'
            height2 = self.canvas.get_text_height(4, scale_rate=0.5) + Config.XP_NODEID_COORD_PADDING
            width2 = self.canvas.get_text_width(node_id, 4, scale_rate=0.5) + Config.XP_NODEID_COORD_PADDING
            radius = height2 / 2
            self.canvas.draw_rectangle(
                node_id_box_x, node_id_box_y,
                width2 + radius, height2,
                self.black_color,
                scale_rate=0.5,
                corner_radius=radius
            )
            self.canvas.draw_text(
                node_id_box_x, node_id_box_y,
                node_id,
                self.white_color, CMNRenderer.coord_str_font_size,
                scale_rate=0.5,
            )

        def draw_medium_zoom_labels(x, y, node_xp):
            """
            +---------+
            |         |
            |    XP   | <- XP_label
            |         |
            +---------+
            Draw XP label.
            """
            self.canvas.draw_text(
                x, y,
                "XP",
                self.text_color, Config.XP_LABEL_FONT_SIZE,
            )

        def draw_medium_zoom_ports(x, y, node_xp):
            """
                     +--------------+
                     |    port      | <- port_string_medium
                     +--------------+ <- port_box_medium
                    / <- port_line
            -------+
                 P1| <- port_label
                   |
            Draw additional port information for medium zoom level
            """
            for p, port in enumerate(node_xp["ports"]):
                if port["type"] == 0 or p not in CMNRenderer.offsets:
                    continue
                dx, dy = CMNRenderer.offsets[p]
                x0 = x + dx * Config.XP_NODE_SQUARE_SIZE
                y0 = y + dy * Config.XP_NODE_SQUARE_SIZE
                x1 = x0 + dx * CMNRenderer.len_div_sqrt2
                y1 = y0 + dy * CMNRenderer.len_div_sqrt2

                self.canvas.draw_line(
                    x0, y0, x1, y1,
                    color=self.grid_color,
                    thickness=Config.GRID_LINE_WIDTH,
                )

                lx = -Config.XP_UI_PADDING * dx
                ly = -Config.XP_UI_PADDING * dy
                self.canvas.draw_text(
                    x + lx + (dx * Config.XP_NODE_SQUARE_SIZE),
                    y + ly + (dy * Config.XP_NODE_SQUARE_SIZE),
                    f"P{p}", self.text_color, Config.XP_DETAILS_FONT_SIZE,
                )

                port_type_str = port["type_str"]
                box_width = self.canvas.get_text_width(port_type_str, Config.XP_DETAILS_FONT_SIZE) + Config.XP_UI_PADDING
                box_height = self.canvas.get_text_height(Config.XP_DETAILS_FONT_SIZE) + Config.XP_UI_PADDING
                box_center_x = x1 + (dx * box_width / 2)
                box_center_y = y1 + (dy * box_height / 2)

                xp_x = node_xp["node_info"]["coord"]["x"]
                xp_y = node_xp["node_info"]["coord"]["y"]
                port_color = self._get_port_color(xp_x, xp_y, p)
                self.canvas.draw_rectangle(
                    box_center_x, box_center_y,
                    box_width, box_height,
                    port_color,
                    outline_color=self.outline_color,
                    outline_thickness=Config.XP_OUTLINE_WIDTH,
                )
                self.hit_test.add_rect(box_center_x, box_center_y, box_width, box_height, (CMNRenderer.CMNNodeType.PORT, xp_x, xp_y, p, 0))
                self.canvas.draw_text(
                    box_center_x, box_center_y,
                    port_type_str, self.text_color, Config.XP_DETAILS_FONT_SIZE,
                )

        def draw_full_zoom_ports(x, y, node_xp):
            """Draw port details with devices grouped by nodeid, plus basic port info for ports without devices."""
            for p, port in enumerate(node_xp["ports"]):
                if port["type"] == 0 or p not in CMNRenderer.offsets:
                    continue

                dx, dy = CMNRenderer.offsets[p]
                x0 = x + dx * Config.XP_NODE_SQUARE_SIZE
                y0 = y + dy * Config.XP_NODE_SQUARE_SIZE
                x1 = x0 + dx * CMNRenderer.len_div_sqrt2
                y1 = y0 + dy * CMNRenderer.len_div_sqrt2

                # Always draw the port line
                self.canvas.draw_line(
                    x0, y0, x1, y1,
                    color=self.grid_color,
                    thickness=Config.GRID_LINE_WIDTH,
                )
                # draw the port label
                lx = -Config.XP_UI_PADDING * dx
                ly = -Config.XP_UI_PADDING * dy
                self.canvas.draw_text(
                    x + lx + (dx * Config.XP_NODE_SQUARE_SIZE),
                    y + ly + (dy * Config.XP_NODE_SQUARE_SIZE),
                    f"P{p}", self.text_color, Config.XP_DETAILS_FONT_SIZE,
                )

                devices = port["devices"][:port["num_devices"]]

                # if no devices, render as empty port
                if len(devices) == 0:
                    port_type_str = port["type_str"]
                    box_width = self.canvas.get_text_width(port_type_str, Config.XP_DETAILS_FONT_SIZE) + Config.XP_UI_PADDING
                    box_height = self.canvas.get_text_height(Config.XP_DETAILS_FONT_SIZE) + Config.XP_UI_PADDING
                    box_center_x = x1 + (dx * box_width / 2)
                    box_center_y = y1 + (dy * box_height / 2)

                    xp_x = node_xp["node_info"]["coord"]["x"]
                    xp_y = node_xp["node_info"]["coord"]["y"]
                    port_color = self._get_port_color(xp_x, xp_y, p)
                    self.canvas.draw_rectangle(
                        box_center_x, box_center_y,
                        box_width, box_height,
                        port_color,
                        outline_color=self.outline_color,
                        outline_thickness=Config.XP_OUTLINE_WIDTH,
                    )
                    self.hit_test.add_rect(box_center_x, box_center_y, box_width, box_height, (CMNRenderer.CMNNodeType.PORT, xp_x, xp_y, p, 0))
                    self.canvas.draw_text(
                        box_center_x, box_center_y,
                        port_type_str, self.text_color, Config.XP_DETAILS_FONT_SIZE,
                    )
                    continue

                # Full device rendering for ports with devices
                port_string = f"{'CAL - ' if port['cal'] else ''}{port['type_str']}"

                # Sort devices by nodeid once
                sorted_indices = np.argsort(devices["nodeid"])
                sorted_device_types = devices["type_str"][sorted_indices]
                sorted_nodeids = devices["nodeid"][sorted_indices]

                # Calculate dimensions
                base_text_height = self.canvas.get_text_height(Config.XP_DETAILS_FONT_SIZE)
                text_height = base_text_height + Config.XP_UI_PADDING
                port_col_width = text_height
                port_string_height = self.canvas.get_text_width(port_string, Config.XP_DETAILS_FONT_SIZE) + Config.XP_UI_PADDING
                device_str_widths = np.vectorize(self.canvas.get_text_width)(sorted_device_types, Config.XP_DETAILS_FONT_SIZE)
                device_col_width = np.max(device_str_widths) + (Config.XP_UI_DEVICE_STR_WIDTH_PADDING * 3) if len(device_str_widths) > 0 else 0

                # Calculate actual grouped heights
                _, group_sizes = np.unique(sorted_nodeids, return_counts=True)
                group_heights = np.array(
                    [
                        self.canvas.get_text_height(Config.XP_DETAILS_FONT_SIZE, size) + Config.XP_UI_PADDING
                        for size in group_sizes
                    ]
                )
                device_rows_height = np.sum(group_heights)

                total_width = port_col_width + device_col_width
                total_height = max(port_string_height, device_rows_height)

                box_center_x = x1 + (dx * total_width / 2)
                box_center_y = y1 + (dy * total_height / 2)

                if dx > 0:  # East: port left (narrow), devices right (wide)
                    port_col_center_x = box_center_x - (total_width / 2) + (port_col_width / 2)
                    device_col_center_x = box_center_x - (total_width / 2) + port_col_width + (device_col_width / 2)
                    divider_x = box_center_x - (total_width / 2) + port_col_width
                else:  # West: devices left (wide), port right (narrow)
                    device_col_center_x = box_center_x - (total_width / 2) + (device_col_width / 2)
                    port_col_center_x = box_center_x - (total_width / 2) + device_col_width + (port_col_width / 2)
                    divider_x = box_center_x - (total_width / 2) + device_col_width

                # Draw main container
                self.canvas.draw_rectangle(
                    box_center_x, box_center_y, total_width, total_height,
                    self.ui_bg_color, outline_color=self.outline_color,
                    outline_thickness=Config.XP_OUTLINE_WIDTH
                )
                # Draw vertical divider between columns
                self.canvas.draw_line(
                    divider_x, box_center_y - (total_height / 2),
                    divider_x, box_center_y + (total_height / 2),
                    color=self.outline_color, thickness=Config.XP_OUTLINE_WIDTH
                )
                # Draw port section
                xp_x = node_xp["node_info"]["coord"]["x"]
                xp_y = node_xp["node_info"]["coord"]["y"]
                port_color = self._get_port_color(xp_x, xp_y, p)
                self.canvas.draw_rectangle(
                    port_col_center_x, box_center_y, port_col_width, total_height,
                    port_color, outline_color=self.outline_color,
                    outline_thickness=Config.XP_OUTLINE_WIDTH
                )
                # Add port to hit test
                self.hit_test.add_rect(
                    port_col_center_x, box_center_y, port_col_width, total_height,
                    (CMNRenderer.CMNNodeType.PORT, xp_x, xp_y, p, 0)
                )
                # Draw vertical port text
                self.canvas.draw_text(
                    port_col_center_x, box_center_y, port_string,
                    self.text_color, Config.XP_DETAILS_FONT_SIZE, angle=-90
                )

                # render device grouped by nodeids
                current_y = box_center_y - (total_height / 2)
                group_start = 0
                for i in range(len(sorted_nodeids) + 1):
                    if i == len(sorted_nodeids) or (i > group_start and sorted_nodeids[i] != sorted_nodeids[group_start]):
                        # Process group from group_start to i-1
                        group_size = i - group_start
                        group_height = self.canvas.get_text_height(Config.XP_DETAILS_FONT_SIZE, group_size) + Config.XP_UI_PADDING
                        group_center_y = current_y + (group_height / 2)

                        # Create multiline text for this group
                        group_device_types = sorted_device_types[group_start:i]
                        multiline_text = '\n'.join(group_device_types)

                        first_device_idx = sorted_indices[group_start]
                        device_color = self._get_device_color(xp_x, xp_y, p, first_device_idx)
                        group_nodeid = sorted_nodeids[group_start]

                        # Draw group rectangle and text
                        self.canvas.draw_rectangle(
                            device_col_center_x, group_center_y, device_col_width, group_height,
                            device_color, outline_color=self.outline_color,
                            outline_thickness=Config.XP_OUTLINE_WIDTH
                        )
                        # Add hit test for group
                        self.hit_test.add_rect(
                            device_col_center_x, group_center_y, device_col_width, group_height,
                            (CMNRenderer.CMNNodeType.DEVICE, xp_x, xp_y, p, first_device_idx)
                        )

                        self.canvas.draw_text(
                            device_col_center_x, group_center_y, multiline_text,
                            self.text_color, Config.XP_DETAILS_FONT_SIZE
                        )

                        # Draw nodeid pill for this device group
                        nodeid_str = str(group_nodeid)
                        pill_height = self.canvas.get_text_height(CMNRenderer.coord_str_font_size, scale_rate=0.5) + Config.XP_NODEID_COORD_PADDING
                        pill_width = self.canvas.get_text_width(nodeid_str, CMNRenderer.coord_str_font_size, scale_rate=0.5) + Config.XP_NODEID_COORD_PADDING
                        pill_radius = pill_height / 2

                        if dx > 0:
                            pill_x = device_col_center_x + (device_col_width / 2)
                        else:
                            pill_x = device_col_center_x - (device_col_width / 2)

                        self.canvas.draw_rectangle(
                            pill_x, group_center_y,
                            pill_width + pill_radius, pill_height,
                            self.black_color,
                            scale_rate=0.5,
                            corner_radius=pill_radius
                        )
                        self.canvas.draw_text(
                            pill_x, group_center_y,
                            nodeid_str,
                            self.white_color, CMNRenderer.coord_str_font_size,
                            scale_rate=0.5,
                        )

                        current_y += group_height
                        group_start = i

        # main loop over visible XPs
        # only obtain visible section from the full cmn mesh
        min_row, max_row, min_col, max_col = self.get_visible_bounds()
        visible_mesh: np.ndarray = self.cmn.get_view(self.cmn_idx, min_row, max_row, min_col, max_col)

        # zoom mode
        zoom_scale = self.canvas.zoom_scale
        is_small_zoom = zoom_scale >= 2.50
        is_medium_zoom = zoom_scale >= 5.0
        is_full_zoom = zoom_scale >= 7.00

        # nested loop over visible mesh only
        for local_row in range(visible_mesh.shape[0]):
            for local_col in range(visible_mesh.shape[1]):
                row = min_row + local_row
                col = min_col + local_col
                if row >= self.current_mesh["y_dim"] or col >= self.current_mesh["x_dim"]:
                    continue

                node_xp = visible_mesh[local_row, local_col]
                x, y = self.grid_to_world(row, col)

                draw_node(x, y, node_xp, False)

                if is_small_zoom:
                    draw_coord_node_id_labels(x, y, node_xp)

                if is_medium_zoom:
                    draw_medium_zoom_labels(x, y, node_xp)
                    if not is_full_zoom:
                        draw_medium_zoom_ports(x, y, node_xp)

                if is_full_zoom:
                    draw_full_zoom_ports(x, y, node_xp)
