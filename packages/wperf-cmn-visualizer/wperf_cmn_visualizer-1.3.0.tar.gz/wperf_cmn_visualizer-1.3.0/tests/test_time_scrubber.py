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

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QPointF, QTimer, QEvent
from PySide6.QtGui import QMouseEvent, QKeyEvent, QColor, QIcon
import pytest
from unittest.mock import Mock, patch
import numpy as np
from typing import cast
from wperf_cmn_visualizer.time_scrubber import TimelineCanvas, TimeScrubber, _global_timeline_sync

from wperf_cmn_visualizer.cmn_metrics import CMNMetrics


def create_mock_cmn_metrics(num_timestamps=10) -> CMNMetrics:
    """Create a properly mocked CMNMetrics instance with deterministic data."""
    mock_metrics = Mock(spec=CMNMetrics)

    mock_metrics.time_stamps = np.linspace(0, 1.0, num_timestamps)
    time_normalized = np.linspace(0, 2 * np.pi, num_timestamps)
    # arbitary function: y = 10 + 10sin(2pix)
    sine_values = 10 + 10 * np.sin(time_normalized)
    mock_metrics.global_data = sine_values.reshape(num_timestamps, 1, 1)

    return cast(CMNMetrics, mock_metrics)


class TestTimelineCanvas:
    """Tests for TimelineCanvas widget."""

    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setup_method(self):
        self.parent = QWidget()
        self.mock_metrics = create_mock_cmn_metrics(num_timestamps=10)

        time_stamps = self.mock_metrics.time_stamps
        values = self.mock_metrics.global_data[:, 0, 0]
        min_val = np.min(values)
        max_val = np.max(values)

        self.canvas = TimelineCanvas(self.parent, time_stamps, values, min_val, max_val)
        self.canvas.resize(400, 100)
        self.parent.show()

    def teardown_method(self):
        self.canvas.deleteLater()
        self.parent.deleteLater()

    def test_initial_state(self):
        """Test initial state of TimelineCanvas."""
        assert self.canvas.current_time_index == 0
        assert not self.canvas.is_dragging
        assert not self.canvas.is_hovering

    def test_get_nearest_time_index_empty(self):
        """
        Test finding nearest time index returns gracefully
        for empty timestamps array.
        """
        empty_canvas = TimelineCanvas(self.parent, np.array([]), np.array([]), 0.0, 1.0)
        assert empty_canvas._get_nearest_time_index(100) == 0

    def test_get_nearest_time_index(self):
        """
        Test finding nearest time index for given x coordinate.
        Test with known data: 10 timestamps from 0 to 1.0, so
        x=5 -> index 0, x=395 -> index 9
        """
        assert self.canvas._get_nearest_time_index(5) == 0  # Near start
        assert 4 <= self.canvas._get_nearest_time_index(200) <= 5  # Near middle
        assert self.canvas._get_nearest_time_index(395) == 9  # Near end

    def test_is_near_handle(self):
        """Test handle proximity detection."""
        self.canvas.handle_x = 100

        # Test within tolerance
        # 5 pixels away when default tolerance is 10
        assert self.canvas._is_near_handle(95)
        assert self.canvas._is_near_handle(105)
        assert self.canvas._is_near_handle(100)

        # Test outside tolerance
        assert not self.canvas._is_near_handle(85)  # 15 pixels away
        assert not self.canvas._is_near_handle(115)

        # Test custom tolerance
        assert self.canvas._is_near_handle(85, tolerance=20)

    def test_mouse_press_starts_dragging(self):
        """
        Test that mouse press near handle starts dragging.
        Set handle position and simulate mouse press near it using eventFilter.
        """
        self.canvas.handle_x = 100.0
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(105, 50),  # Near handle
            QPointF(105, 50),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        # Use eventFilter instead of direct method call
        result = self.canvas.eventFilter(self.canvas.view.viewport(), press_event)
        assert self.canvas.is_dragging
        assert result

    def test_mouse_press_starts_dragging_anywhere(self):
        """
        Test that mouse press anywhere starts dragging and scrubs to that position.
        """
        self.canvas.handle_x = 100.0
        old_time_index = self.canvas.current_time_index
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(200, 50),  # Click somewhere else
            QPointF(200, 50),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        result = self.canvas.eventFilter(self.canvas.view.viewport(), press_event)

        assert result is True
        assert self.canvas.is_dragging
        # Time index should change to the clicked position
        assert self.canvas.current_time_index != old_time_index

    def test_mouse_move_during_dragging(self):
        """
        Test mouse movement during dragging updates time index.
        Set mouse dragging and simulate mouse move event.
        Patch singleShot and confirm global signal emission.
        """
        self.canvas.is_dragging = True
        # Move to x=200 (~middle of canvas)
        move_event = QMouseEvent(
            QEvent.Type.MouseMove,
            QPointF(200, 50),
            QPointF(200, 50),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )

        with patch.object(QTimer, 'singleShot') as mock_timer:
            result = self.canvas.eventFilter(self.canvas.view.viewport(), move_event)
            assert 4 <= self.canvas.current_time_index <= 5
            # Should emit global signal
            mock_timer.assert_called_once()
            assert result

    def test_mouse_move_hover_effects(self):
        """
        Test hover effects when not dragging.
        Test that mouse style is changed.
        Test internal state management is correct.
        """
        self.canvas.is_dragging = False
        self.canvas.handle_x = 100.0
        # Move near handle
        hover_event = QMouseEvent(
            QEvent.Type.MouseMove,
            QPointF(105, 50),
            QPointF(105, 50),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        result = self.canvas.eventFilter(self.canvas.view.viewport(), hover_event)
        assert self.canvas.is_hovering
        assert self.canvas.cursor().shape() == Qt.CursorShape.SizeHorCursor
        assert result

        # Move away from handle resets states
        away_event = QMouseEvent(
            QEvent.Type.MouseMove,
            QPointF(200, 50),
            QPointF(200, 50),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        result = self.canvas.eventFilter(self.canvas.view.viewport(), away_event)
        assert not self.canvas.is_hovering
        assert self.canvas.cursor().shape() == Qt.CursorShape.ArrowCursor
        assert result

    def test_mouse_release_stops_dragging(self):
        """Test mouse release stops dragging."""
        self.canvas.is_dragging = True
        release_event = QMouseEvent(
            QEvent.Type.MouseButtonRelease,
            QPointF(100, 50),
            QPointF(100, 50),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        result = self.canvas.eventFilter(self.canvas.view.viewport(), release_event)
        assert not self.canvas.is_dragging
        assert result

    def test_leave_event_resets_hover(self):
        """Test that leaving widget resets hover state."""
        self.canvas.is_hovering = True
        self.canvas.is_dragging = False

        leave_event = QEvent(QEvent.Type.Leave)
        result = self.canvas.eventFilter(self.canvas.view.viewport(), leave_event)
        assert not self.canvas.is_hovering
        assert self.canvas.cursor().shape() == Qt.CursorShape.ArrowCursor
        assert result

    def test_leave_event_not_reset_hover_dragging(self):
        """Test that mouse leave does not reset hover state if dragging."""
        self.canvas.is_hovering = True
        self.canvas.is_dragging = True

        leave_event = QEvent(QEvent.Type.Leave)
        result = self.canvas.eventFilter(self.canvas.view.viewport(), leave_event)
        assert self.canvas.is_hovering  # Should remain True when dragging
        assert result

    def test_update_data(self):
        """Test updating canvas data."""
        new_timestamps = np.linspace(0, 2.0, 20)
        new_values = np.sin(new_timestamps)
        new_min = np.min(new_values)
        new_max = np.max(new_values)

        self.canvas.update_data(new_timestamps, new_values, new_min, new_max)

        assert len(self.canvas.time_stamps) == 20
        assert len(self.canvas.values) == 20
        assert self.canvas.min_val == new_min
        assert self.canvas.max_val == new_max

    def test_global_sync_signal_reception(self):
        """Test that canvas responds to global sync signals."""
        initial_index = self.canvas.current_time_index

        # Emit global signal with new time index
        _global_timeline_sync.time_changed.emit(5)

        assert self.canvas.current_time_index == 5
        assert self.canvas.current_time_index != initial_index

    def test_set_time_index(self):
        """Test setting time index directly."""
        self.canvas.set_time_index(3)
        assert self.canvas.current_time_index == 3

        # Test boundary conditions
        self.canvas.set_time_index(-1)  # Should not change
        assert self.canvas.current_time_index == 3
        self.canvas.set_time_index(100)  # Should not change (out of bounds)
        assert self.canvas.current_time_index == 3

    def test_text_display_functionality(self):
        """Test text display features."""

        # Test setting text display
        self.canvas.set_text_display("Test\nText", QColor(255, 0, 0), 12, 2)
        assert self.canvas.show_text
        assert self.canvas.text_content == "Test\nText"
        assert self.canvas.text_line_count == 2

        # Test clearing text display
        self.canvas.clear_text_display()
        assert not self.canvas.show_text
        assert self.canvas.text_content == ""

    def test_arrow_key_scrub_left(self):
        """
        Test that left arrow key moves to previous time index.
        """
        # Start from the middle
        self.canvas.current_time_index = 5
        old_index = self.canvas.current_time_index
        key_event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Left,
            Qt.KeyboardModifier.NoModifier
        )
        result = self.canvas.eventFilter(self.canvas.view, key_event)

        assert result is True
        assert self.canvas.current_time_index == old_index - 1

    def test_arrow_key_scrub_right(self):
        """
        Test that right arrow key moves to next time index.
        """
        # Start from the beginning
        self.canvas.current_time_index = 0
        old_index = self.canvas.current_time_index
        key_event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Right,
            Qt.KeyboardModifier.NoModifier
        )
        result = self.canvas.eventFilter(self.canvas.view, key_event)

        assert result is True
        assert self.canvas.current_time_index == old_index + 1

    def test_arrow_key_scrub_left_at_beginning(self):
        """
        Test that left arrow key does nothing when already at beginning.
        """
        self.canvas.current_time_index = 0
        key_event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Left,
            Qt.KeyboardModifier.NoModifier
        )
        result = self.canvas.eventFilter(self.canvas.view, key_event)

        assert result is True
        assert self.canvas.current_time_index == 0  # Should stay at 0

    def test_arrow_key_scrub_right_at_end(self):
        """
        Test that right arrow key does nothing when already at end.
        """
        # Set to last valid index
        self.canvas.current_time_index = len(self.canvas.time_stamps) - 1
        old_index = self.canvas.current_time_index
        key_event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Right,
            Qt.KeyboardModifier.NoModifier
        )
        result = self.canvas.eventFilter(self.canvas.view, key_event)

        assert result is True
        assert self.canvas.current_time_index == old_index  # Should stay at end


class TestTimeScrubber:
    """Tests for TimeScrubber widget."""

    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setup_method(self):
        self.parent = QWidget()
        self.mock_metrics = create_mock_cmn_metrics(num_timestamps=10)
        self.scrubber = TimeScrubber(self.parent, self.mock_metrics, height=50)
        self.parent.show()

    def teardown_method(self):
        self.scrubber.deleteLater()
        self.parent.deleteLater()

    def test_initial_state(self):
        """Test initial state of TimeScrubber."""
        assert not self.scrubber.is_playing
        assert self.scrubber.playback_speed == 1.0
        assert self.scrubber.current_time_index == 0
        assert self.scrubber.height() == 50

        # Check UI components exist
        assert hasattr(self.scrubber, 'play_button')
        assert hasattr(self.scrubber, 'stop_button')
        assert hasattr(self.scrubber, 'prev_button')
        assert hasattr(self.scrubber, 'next_button')
        assert hasattr(self.scrubber, 'speed_combobox')
        assert hasattr(self.scrubber, 'timeline_canvas')

    def test_play_pause_functionality(self):
        """Test play/pause button functionality."""
        # Test that default is not playing.
        assert not self.scrubber.is_playing
        # Test play
        self.scrubber._on_play_pause()
        assert self.scrubber.is_playing
        # Test pause
        self.scrubber._on_play_pause()
        assert not self.scrubber.is_playing

    def test_stop_functionality(self):
        """Test stop button functionality."""
        with patch.object(_global_timeline_sync, 'time_changed') as mock_signal:
            # Set up playing state with slightly advanced time index
            self.scrubber.is_playing = True
            self.scrubber.current_time_index = 5
            self.scrubber._on_stop()

            # check state and callbacks
            assert not self.scrubber.is_playing
            assert self.scrubber.current_time_index == 0
            mock_signal.emit.assert_called_with(0)

    def test_previous_next_functionality(self):
        """Test previous/next button functionality."""
        with patch.object(_global_timeline_sync, 'time_changed') as mock_signal:
            # Start at index 5
            self.scrubber.current_time_index = 5

            # Test previous
            self.scrubber._on_previous()
            assert self.scrubber.current_time_index == 4
            mock_signal.emit.assert_called_with(4)

            # Test next
            mock_signal.reset_mock()
            self.scrubber._on_next()
            assert self.scrubber.current_time_index == 5
            mock_signal.emit.assert_called_with(5)

    def test_previous_next_functionality_boundaries(self):
        """
        Test previous/next button functionality on boundaries.
        When current time index is on a boundary, there should be no overflow/underflow.
        """
        self.scrubber.current_time_index = 0
        self.scrubber._on_previous()
        assert self.scrubber.current_time_index == 0

        self.scrubber.current_time_index = len(self.mock_metrics.time_stamps) - 1
        self.scrubber._on_next()
        assert self.scrubber.current_time_index == len(self.mock_metrics.time_stamps) - 1

    @pytest.mark.parametrize("speed_text, expected_speed", [
        ("2x", 2.0),
        ("0.5x", 0.5),
        ("0.25x", 0.25),
        ("1.5x", 1.5),
        ("4x", 4.0),
        ("16x", 16.0),
        ("64x", 64.0),
    ])
    def test_speed_change_valid(self, speed_text, expected_speed):
        """Test valid playback speed changes."""
        self.scrubber._on_speed_change(speed_text)
        assert self.scrubber.playback_speed == expected_speed

    @pytest.mark.parametrize("invalid_text", ["invalid", "not_a_number", "NaNx"])
    def test_speed_change_invalid(self, invalid_text):
        """Test that invalid speeds strings fall back to 1.0."""
        self.scrubber._on_speed_change(invalid_text)
        assert self.scrubber.playback_speed == 1.0

    def test_playback_timing(self):
        """
        Test playback timing calculations with known data and known speed.
        """
        with patch.object(self.scrubber.playback_timer, 'start') as mock_start:
            self.scrubber.is_playing = True
            self.scrubber.current_time_index = 0
            self.scrubber.playback_speed = 2.0

            self.scrubber._schedule_next_frame()

            # Calculate expected delay with known timestamps
            # time_stamps = [0.0, 0.111..., 0.222..., ...] for 10 timestamps
            time_delta = self.mock_metrics.time_stamps[1] - self.mock_metrics.time_stamps[0]
            expected_delay = max(1, int((time_delta * 1000) / 2.0))

            mock_start.assert_called_with(expected_delay)

            args = mock_start.call_args[0]
            delay_called = args[0]
            assert 50 <= delay_called <= 60  # Should be around 111ms / 2 = 55ms

    def test_speed_change_restarts_timer(self):
        """
        Test that changing speed during playback immediately restarts the timer.
        This tests the fix for the issue where speed changes don't take effect
        until the current timer expires.
        """
        with patch.object(self.scrubber.playback_timer, 'stop') as mock_stop, \
             patch.object(self.scrubber, '_schedule_next_frame') as mock_schedule:

            # Set up playing state
            self.scrubber.is_playing = True
            self.scrubber.current_time_index = 2

            # Change speed while playing
            self.scrubber._on_speed_change("64x")

            mock_stop.assert_called_once()
            mock_schedule.assert_called_once()
            assert self.scrubber.playback_speed == 64.0

    def test_start_playback_resets_button_at_end(self):
        """
        Test that _start_playback correctly resets the play button when
        already at the end of timeline.
        """
        with patch.object(self.scrubber.play_button, 'setIcon') as mock_set_icon:

            # Set up at the end
            self.scrubber.current_time_index = len(self.mock_metrics.time_stamps) - 1
            self.scrubber.is_playing = True

            # Try to start playback
            self.scrubber._start_playback()

            assert not self.scrubber.is_playing
            mock_set_icon.assert_called_once()
