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

import pytest
import pandas as pd
import numpy as np
from unittest import mock
from unittest.mock import MagicMock
from PySide6.QtGui import QPalette, QColor
from wperf_cmn_visualizer.cmn_metrics import CMNMetrics

from wperf_cmn_visualizer.cmn import CMN, CMN_MAX_PORTS, CMN_MAX_CHILDS, CMN_XP_DEVICE_ID
from wperf_cmn_visualizer.cmn import CMN_MAX_MESH_WIDTH, CMN_MAX_MESH_HEIGHT
from wperf_cmn_visualizer.cmn import mesh_dtype
from wperf_cmn_visualizer.telemetry_loader import (
    TIME_COLUMN_NAME, METRICS_COLUMN_NAME, NODE_COLUMN_NAME, VALUE_COLUMN_NAME,
    NODEID_COLUMN_NAME, MESH_COLUMN_NAME, UNITS_COLUMN_NAME
)


class TestCMNMetrics:
    """Tests for CMNMetrics data structure and operations."""

    @pytest.fixture
    def mock_cmn(self):
        """Create a mock CMN object for testing."""
        mock_cmn = MagicMock(spec=CMN)
        mock_cmn.num_meshes = 1

        mock_meshes = np.zeros(1, dtype=mesh_dtype)
        mock_mesh = mock_meshes[0]

        mock_mesh["x_dim"] = 2
        mock_mesh["y_dim"] = 2

        for y in range(2):
            for x in range(2):
                xp = mock_mesh["xps"][y, x]
                # Set up XP node info
                xp["node_info"]["coord"]["x"] = x
                xp["node_info"]["coord"]["y"] = y
                xp["node_info"]["nodeid"] = 1000 + y * 2 + x
                xp["node_info"]["type"] = CMN_XP_DEVICE_ID
                xp["node_info"]["type_str"] = "XP"

                # Set up ports
                xp["num_device_ports"] = 1

                # First port has devices
                port = xp["ports"][0]
                port["type"] = 1
                port["type_str"] = "device_port"
                port["num_devices"] = 2

                # Add devices to first port
                for d in range(2):
                    device = port["devices"][d]
                    device["coord"]["x"] = x
                    device["coord"]["y"] = y
                    device["nodeid"] = 100 + y * 2 + x + d
                    device["type"] = 1
                    device["type_str"] = "HN-F"

                # Other ports are empty
                for p in range(1, CMN_MAX_PORTS):
                    port = xp["ports"][p]
                    port["num_devices"] = 0

        mock_cmn.meshes = mock_meshes
        return mock_cmn

    @pytest.fixture
    def sample_metrics_data(self):
        """Create sample metrics DataFrame for testing."""
        return pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 1.0, 1.0, 1.0],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric2", "metric1", "metric2", "metric3"
            ]),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0",
                "XP at X=1 Y=0",
                "HN-F (100) at X=0 Y=0 Port=0",
                "XP at X=0 Y=1",
                "HN-F (101) at X=1 Y=0 Port=0",
                "Global"
            ],
            VALUE_COLUMN_NAME: [10.5, 20.3, 30.7, 15.2, 25.8, 40.1],
            NODEID_COLUMN_NAME: [0, 1, 100, 2, 101, 0],
            MESH_COLUMN_NAME: [0] * 6,
            UNITS_COLUMN_NAME: ["unit"] * 6
        })

    def test_metrics_initialization_basic(self, mock_cmn, sample_metrics_data):
        """Test basic CMNMetrics initialization."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())

        assert len(metrics.metric_names) == 3
        assert "metric1" in metrics.metric_names
        assert "metric2" in metrics.metric_names
        assert "metric3" in metrics.metric_names

        assert metrics.metric_id_map["metric1"] == 0
        assert metrics.metric_id_map["metric2"] == 1
        assert metrics.metric_id_map["metric3"] == 2

        assert len(metrics.time_stamps) == 2
        assert metrics.time_stamps[0] == 0.5
        assert metrics.time_stamps[1] == 1.0
        assert metrics.num_time_stamps == 2

        assert hasattr(metrics, 'global_data')
        assert metrics.global_data.shape == (2, 3, 1)

    def test_xp_data_loading(self, mock_cmn, sample_metrics_data):
        """Test loading XP metric data."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())

        # Check XP at X=0 Y=0, time=0.5, metric1
        time_idx = 0
        mesh_idx = 0
        metric_idx = 0  # metric1
        y, x = 0, 0
        assert metrics.xp_data[time_idx, metric_idx, mesh_idx, y, x] == 10.5

        # Check XP at X=1 Y=0, time=0.5, metric2
        metric_idx = 0  # metric1
        y, x = 0, 1
        assert metrics.xp_data[time_idx, metric_idx, mesh_idx, y, x] == 20.3

        # Check XP at X=0 Y=1, time=1.0, metric1
        time_idx = 1
        metric_idx = 0  # metric1
        y, x = 1, 0
        assert metrics.xp_data[time_idx, metric_idx, mesh_idx, y, x] == 15.2

    def test_global_data_loading(self, mock_cmn, sample_metrics_data):
        """Test loading global metric data."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())

        time_idx = 1
        mesh_idx = 0
        metric_idx = 2  # metric3
        assert metrics.global_data[time_idx, metric_idx, mesh_idx] == 40.1

    def test_node_parsing_edge_cases(self, mock_cmn):
        """Test edge cases in node string parsing."""
        edge_case_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1", "metric1", "metric1"
            ]),
            NODE_COLUMN_NAME: [
                "Global",  # Global node
                "XP at X=0 Y=0",  # Valid XP
                "XP at X=999 Y=999",  # Out of bounds XP
                "HN-F at X=0 Y=0 Port=0",  # Valid device
                "HN-F at X=0 Y=0 Port=0"  # Device with unmatched nodeid
            ],
            VALUE_COLUMN_NAME: [1.0, 2.0, 3.0, 4.0, 5.0],
            NODEID_COLUMN_NAME: [pd.NA, 0, 0, 100, 999],
            MESH_COLUMN_NAME: [0] * 5,
            UNITS_COLUMN_NAME: ["unit"] * 5
        })

        metrics = CMNMetrics(mock_cmn, edge_case_data, QPalette())

        time_idx = 0
        mesh_idx = 0

        # Check global data
        assert metrics.global_data[time_idx, :, mesh_idx] == 1.0

        # Check valid XP
        assert metrics.xp_data[time_idx, :, mesh_idx, 0, 0] == 2.0

        # Check valid device
        assert metrics.device_data[time_idx, :, mesh_idx, 0, 0, 0, 0] == 4.0

        # Check out of bounds XP is not loaded (should remain 0)
        for y in range(CMN_MAX_MESH_HEIGHT):
            for x in range(CMN_MAX_MESH_WIDTH):
                if y == 0 and x == 0:
                    continue  # Skip the valid one
                assert np.isnan(metrics.xp_data[time_idx, :, mesh_idx, y, x])

    def test_invalid_port_handling(self, mock_cmn):
        """Test handling of invalid port numbers."""
        invalid_port_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1"
            ]),
            NODE_COLUMN_NAME: [
                "HN-F at X=0 Y=0 Port=0",  # Valid port
                f"HN-F at X=0 Y=0 Port={CMN_MAX_PORTS}",  # Invalid port (too high)
                "HN-F at X=0 Y=0 Port=-1"  # Invalid port (negative)
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0],
            NODEID_COLUMN_NAME: [100, 100, 100],
            MESH_COLUMN_NAME: [0] * 3,
            UNITS_COLUMN_NAME: ["unit"] * 3
        })

        metrics = CMNMetrics(mock_cmn, invalid_port_data, QPalette())

        # Only valid port should be loaded
        time_idx = 0
        mesh_idx = 0
        y, x = 0, 0

        # Valid port should have data
        assert metrics.device_data[time_idx, :, mesh_idx, y, x, 0, 0] == 10.0

    def test_device_nodeid_matching(self, mock_cmn):
        """Test device nodeid matching in port devices."""
        mesh = mock_cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]

        # Clear existing devices and add new ones
        port["num_devices"] = 3
        port["devices"][0]["nodeid"] = 100
        port["devices"][1]["nodeid"] = 200
        port["devices"][2]["nodeid"] = 300

        nodeid_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1", "metric1"
            ]),
            NODE_COLUMN_NAME: [
                "HN-F at X=0 Y=0 Port=0",  # First device
                "HN-F at X=0 Y=0 Port=0",  # Second device
                "HN-F at X=0 Y=0 Port=0",  # Third device
                "HN-F at X=0 Y=0 Port=0"   # Non-existent device
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0, 40.0],
            NODEID_COLUMN_NAME: [100, 200, 300, 999],
            MESH_COLUMN_NAME: [0] * 4,
            UNITS_COLUMN_NAME: ["unit"] * 4
        })

        metrics = CMNMetrics(mock_cmn, nodeid_data, QPalette())

        time_idx = 0
        mesh_idx = 0
        y, x = 0, 0
        port = 0

        assert metrics.device_data[time_idx, :, mesh_idx, y, x, port, 0] == 10.0
        assert metrics.device_data[time_idx, :, mesh_idx, y, x, port, 1] == 20.0
        assert metrics.device_data[time_idx, :, mesh_idx, y, x, port, 2] == 30.0

    def test_multiple_time_stamps(self, mock_cmn):
        """Test handling of multiple time stamps."""
        multi_time_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 1.0, 1.5, 0.5, 1.0, 1.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1", "metric2", "metric2", "metric2"
            ]),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0",
                "XP at X=1 Y=0", "XP at X=1 Y=0", "XP at X=1 Y=0"
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0, 15.0, 25.0, 35.0],
            NODEID_COLUMN_NAME: [0, 0, 0, 0, 0, 0],
            MESH_COLUMN_NAME: [0] * 6,
            UNITS_COLUMN_NAME: ["unit"] * 6
        })

        metrics = CMNMetrics(mock_cmn, multi_time_data, QPalette())

        assert len(metrics.time_stamps) == 3
        assert metrics.time_stamps[0] == 0.5
        assert metrics.time_stamps[1] == 1.0
        assert metrics.time_stamps[2] == 1.5

        # Check data at different time stamps
        mesh_idx = 0

        # XP at X=0 Y=0, metric1
        assert metrics.xp_data[0, 0, mesh_idx, 0, 0] == 10.0
        assert metrics.xp_data[1, 0, mesh_idx, 0, 0] == 20.0
        assert metrics.xp_data[2, 0, mesh_idx, 0, 0] == 30.0

        # XP at X=1 Y=0, metric2
        assert metrics.xp_data[0, 1, mesh_idx, 0, 1] == 15.0
        assert metrics.xp_data[1, 1, mesh_idx, 0, 1] == 25.0
        assert metrics.xp_data[2, 1, mesh_idx, 0, 1] == 35.0

    def test_empty_metrics_data(self, mock_cmn):
        """Test handling of empty metrics DataFrame."""
        empty_data = pd.DataFrame({
            TIME_COLUMN_NAME: pd.Series([], dtype='float64'),
            METRICS_COLUMN_NAME: pd.Categorical([]),
            NODE_COLUMN_NAME: pd.Series([], dtype='string'),
            VALUE_COLUMN_NAME: pd.Series([], dtype='float64'),
            NODEID_COLUMN_NAME: pd.Series([], dtype="UInt16"),
            MESH_COLUMN_NAME: pd.Series([], dtype=int),
            UNITS_COLUMN_NAME: pd.Series([])
        })

        metrics = CMNMetrics(mock_cmn, empty_data, QPalette())

        assert len(metrics.metric_names) == 0
        assert len(metrics.metric_id_map) == 0
        assert len(metrics.time_stamps) == 0
        assert metrics.num_time_stamps == 0

        # Data array should still be initialized but empty in time dimension
        assert metrics.xp_data.shape[0] == 0
        assert metrics.port_data.shape[0] == 0
        assert metrics.device_data.shape[0] == 0
        assert metrics.global_data.shape[0] == 0

    def test_malformed_node_strings(self, mock_cmn):
        """Test handling of malformed node strings."""
        malformed_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1", "metric1"
            ]),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0",  # Valid XP string
                "XP at X=abc Y=def",  # Invalid coordinates
                "Random string",  # Completely invalid
                ""  # Empty string
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0, 50.0],
            NODEID_COLUMN_NAME: [pd.NA] * 4,
            MESH_COLUMN_NAME: [0] * 4,
            UNITS_COLUMN_NAME: ["unit"] * 4
        })

        metrics = CMNMetrics(mock_cmn, malformed_data, QPalette())

        # Only the valid XP should be loaded
        time_idx = 0
        mesh_idx = 0
        assert metrics.xp_data[time_idx, :, mesh_idx, 0, 0] == 10.0

        # All other positions should remain at default values
        for y in range(CMN_MAX_MESH_HEIGHT):
            for x in range(CMN_MAX_MESH_WIDTH):
                if y == 0 and x == 0:  # ignore valid case
                    continue
                assert np.isnan(metrics.xp_data[time_idx, :, mesh_idx, y, x])

    def test_metrics_hash_consistency(self, mock_cmn, sample_metrics_data):
        """Test that metrics hash is consistent with metrics array."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())

        for i, metric in enumerate(metrics.metric_names):
            assert metrics.metric_id_map[metric] == i

        # Test that hash lookup gives correct metric ID
        assert metrics.metric_id_map["metric1"] == 0
        assert metrics.metric_id_map["metric2"] == 1
        assert metrics.metric_id_map["metric3"] == 2

    def test_time_stamp_sorting(self, mock_cmn):
        """Test that time stamps are properly sorted."""
        unsorted_time_data = pd.DataFrame({
            TIME_COLUMN_NAME: [2.0, 0.5, 1.5, 1.0, 0.5, 2.0],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1", "metric1", "metric1", "metric1"
            ]),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0",
                "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0"
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
            NODEID_COLUMN_NAME: [pd.NA] * 6,
            MESH_COLUMN_NAME: [0] * 6,
            UNITS_COLUMN_NAME: ["unit"] * 6
        })

        metrics = CMNMetrics(mock_cmn, unsorted_time_data, QPalette())

        # Check that time stamps are sorted and unique
        expected_times = [0.5, 1.0, 1.5, 2.0]
        assert len(metrics.time_stamps) == 4
        assert np.array_equal(metrics.time_stamps, expected_times)
        assert metrics.num_time_stamps == 4

    def test_device_index_bounds_checking(self, mock_cmn):
        """Test device index bounds checking with CMN_MAX_CHILDS."""
        mesh = mock_cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]
        port["num_devices"] = CMN_MAX_CHILDS + 5

        # Add devices up to the limit
        for i in range(CMN_MAX_CHILDS + 5):
            if i < CMN_MAX_CHILDS:
                port["devices"][i]["nodeid"] = i

        # overflow child count by arbitary amount 5
        device_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5] * (CMN_MAX_CHILDS + 5),
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1"] * (CMN_MAX_CHILDS + 5)
            ),
            NODE_COLUMN_NAME: ["HN-F at X=0 Y=0 Port=0"] * (CMN_MAX_CHILDS + 5),
            VALUE_COLUMN_NAME: list(range(CMN_MAX_CHILDS + 5)),
            NODEID_COLUMN_NAME: [i for i in range(CMN_MAX_CHILDS + 5)],
            MESH_COLUMN_NAME: [0] * (CMN_MAX_CHILDS + 5),
            UNITS_COLUMN_NAME: ["unit"] * (CMN_MAX_CHILDS + 5)
        })

        metrics = CMNMetrics(mock_cmn, device_data, QPalette())  # should not crash

        time_idx = 0
        mesh_idx = 0
        y, x = 0, 0
        port_idx = 0

        for i in range(CMN_MAX_CHILDS):
            assert metrics.device_data[time_idx, :, mesh_idx, y, x, port_idx, i] == i

    def test_multi_metric_data_separation(self, mock_cmn, sample_metrics_data):
        """Test that multiple metrics are properly separated in data arrays."""
        # Extend sample data with more metrics and nodes
        extended_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.5, 1.5, 1.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric2", "metric3",
                "metric1", "metric2", "metric3",
                "metric1", "metric2", "metric3"
            ]),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0",
                "XP at X=1 Y=0", "XP at X=1 Y=0", "XP at X=1 Y=0",
                "XP at X=0 Y=1", "XP at X=0 Y=1", "XP at X=0 Y=1"
            ],
            VALUE_COLUMN_NAME: [100, 5.2, 0.85, 150, 3.8, 0.92, 120, 4.1, 0.78],
            NODEID_COLUMN_NAME: [pd.NA] * 9,
            MESH_COLUMN_NAME: [0] * 9,
            UNITS_COLUMN_NAME: ["unit"] * 9
        })

        metrics = CMNMetrics(mock_cmn, extended_data, QPalette())

        # Verify metric separation
        assert len(metrics.metric_names) == 3
        assert "metric1" in metrics.metric_names
        assert "metric2" in metrics.metric_names
        assert "metric3" in metrics.metric_names

        # Test data access for different metrics
        metric1 = metrics.metric_id_map["metric1"]
        metric2 = metrics.metric_id_map["metric2"]
        metric3 = metrics.metric_id_map["metric3"]

        # Check XP at (0,0) time=0.5
        assert metrics.xp_data[0, metric1, 0, 0, 0] == 100
        assert metrics.xp_data[0, metric2, 0, 0, 0] == 5.2
        assert metrics.xp_data[0, metric3, 0, 0, 0] == 0.85

        # Check XP at (1,0) time=1.0
        assert metrics.xp_data[1, metric1, 0, 0, 1] == 150
        assert metrics.xp_data[1, metric2, 0, 0, 1] == 3.8
        assert metrics.xp_data[1, metric3, 0, 0, 1] == 0.92

    def test_multi_metric_device_data(self, mock_cmn):
        """Test device data with multiple metrics."""
        # Set up mock CMN with devices
        mesh = mock_cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]
        port["num_devices"] = 2
        port["devices"][0]["nodeid"] = 100
        port["devices"][1]["nodeid"] = 101

        multi_metric_device_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0],
            METRICS_COLUMN_NAME: pd.Categorical([
                "xp_tx_read_metric_name", "hnf_snoop_send_metric_name", "xp_tx_read_metric_name", "hnf_snoop_send_metric_name",
                "xp_tx_read_metric_name", "hnf_snoop_send_metric_name", "xp_tx_read_metric_name", "hnf_snoop_send_metric_name"
            ]),
            NODE_COLUMN_NAME: [
                "HN-F at X=0 Y=0 Port=0", "HN-F at X=0 Y=0 Port=0",
                "HN-F at X=0 Y=0 Port=0", "HN-F at X=0 Y=0 Port=0",
                "HN-F at X=0 Y=0 Port=0", "HN-F at X=0 Y=0 Port=0",
                "HN-F at X=0 Y=0 Port=0", "HN-F at X=0 Y=0 Port=0"
            ],
            VALUE_COLUMN_NAME: [50.0, 25.0, 60.0, 30.0, 55.0, 28.0, 65.0, 32.0],
            NODEID_COLUMN_NAME: [100, 100, 101, 101, 100, 100, 101, 101],
            MESH_COLUMN_NAME: [0] * 8,
            UNITS_COLUMN_NAME: ["unit"] * 8
        })

        metrics = CMNMetrics(mock_cmn, multi_metric_device_data, QPalette())

        xp_tx_read_metric = metrics.metric_id_map["xp_tx_read_metric_name"]
        hnf_snoop_send_metric = metrics.metric_id_map["hnf_snoop_send_metric_name"]

        # Check device 0 (nodeid 100) at time=0.5
        assert metrics.device_data[0, xp_tx_read_metric, 0, 0, 0, 0, 0] == 50.0
        assert metrics.device_data[0, hnf_snoop_send_metric, 0, 0, 0, 0, 0] == 25.0

        # Check device 1 (nodeid 101) at time=1.0
        assert metrics.device_data[1, xp_tx_read_metric, 0, 0, 0, 0, 1] == 65.0
        assert metrics.device_data[1, hnf_snoop_send_metric, 0, 0, 0, 0, 1] == 32.0

    def test_multi_metric_global_data(self, mock_cmn):
        """Test global data with multiple metrics across time."""
        global_multi_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.5, 1.5, 1.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric2", "metric3",
                "metric1", "metric2", "metric3",
                "metric1", "metric2", "metric3"
            ]),
            NODE_COLUMN_NAME: ["Global"] * 9,
            VALUE_COLUMN_NAME: [450.5, 65.2, 0.82, 475.3, 67.8, 0.89, 460.1, 66.5, 0.85],
            NODEID_COLUMN_NAME: [pd.NA] * 9,
            MESH_COLUMN_NAME: [0] * 9,
            UNITS_COLUMN_NAME: ["unit"] * 9
        })

        metrics = CMNMetrics(mock_cmn, global_multi_data, QPalette())

        metric1 = metrics.metric_id_map["metric1"]
        metric2 = metrics.metric_id_map["metric2"]
        metric3 = metrics.metric_id_map["metric3"]

        # Check values across different times
        assert metrics.global_data[0, metric1, 0] == 450.5
        assert metrics.global_data[0, metric2, 0] == 65.2
        assert metrics.global_data[0, metric3, 0] == 0.82

        assert metrics.global_data[1, metric1, 0] == 475.3
        assert metrics.global_data[2, metric2, 0] == 66.5

    def test_mixed_node_types_multi_metrics(self, mock_cmn):
        """Test handling of mixed node types with multiple metrics."""
        # Set up device in mock CMN
        mesh = mock_cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]
        port["num_devices"] = 1
        port["devices"][0]["nodeid"] = 200

        mixed_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5] * 6 + [1.0] * 6,
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric_a", "metric_a", "metric_a", "metric_b", "metric_b", "metric_b",
                "metric_a", "metric_a", "metric_a", "metric_b", "metric_b", "metric_b"
            ]),
            NODE_COLUMN_NAME: [
                "Global", "XP at X=0 Y=0", "HN-F at X=0 Y=0 Port=0",
                "Global", "XP at X=0 Y=0", "HN-F at X=0 Y=0 Port=0",
                "Global", "XP at X=0 Y=0", "HN-F at X=0 Y=0 Port=0",
                "Global", "XP at X=0 Y=0", "HN-F at X=0 Y=0 Port=0"
            ],
            VALUE_COLUMN_NAME: [10, 20, 30, 40, 50, 60, 15, 25, 35, 45, 55, 65],
            NODEID_COLUMN_NAME: [pd.NA, pd.NA, 200] * 4,
            MESH_COLUMN_NAME: [0] * 12,
            UNITS_COLUMN_NAME: ["unit"] * 12
        })

        metrics = CMNMetrics(mock_cmn, mixed_data, QPalette())

        metric_a_idx = metrics.metric_id_map["metric_a"]
        metric_b_idx = metrics.metric_id_map["metric_b"]

        # Check all data types are populated correctly
        # Time 0.5
        assert metrics.global_data[0, metric_a_idx, 0] == 10
        assert metrics.global_data[0, metric_b_idx, 0] == 40
        assert metrics.xp_data[0, metric_a_idx, 0, 0, 0] == 20
        assert metrics.xp_data[0, metric_b_idx, 0, 0, 0] == 50
        assert metrics.device_data[0, metric_a_idx, 0, 0, 0, 0, 0] == 30
        assert metrics.device_data[0, metric_b_idx, 0, 0, 0, 0, 0] == 60

        # Time 1.0
        assert metrics.global_data[1, metric_a_idx, 0] == 15
        assert metrics.global_data[1, metric_b_idx, 0] == 45

    def test_value_to_colour_returns_white_on_invalid_range(self, mock_cmn, sample_metrics_data):
        """Ensure that when _value_to_colour is supplied with invalid ranges, return values is white"""
        palette = QPalette()
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        assert cm._value_to_colour(10, 20, 10) == palette.color(QPalette.ColorRole.Window).name()
        assert cm._value_to_colour(10, 10, 10) == palette.color(QPalette.ColorRole.Window).name()

    def test_value_to_colour_maps_correctly_at_bounds(self, mock_cmn, sample_metrics_data):
        """Basic tests for _value_to_colour function"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        assert cm._value_to_colour(0, 0, 100) == "#FFFFFF"
        assert cm._value_to_colour(100, 0, 100) == "#FF0000"
        assert cm._value_to_colour(50, 0, 100) == "#FF7F7F"

    def test_value_to_colour_clamps_to_range(self, mock_cmn, sample_metrics_data):
        """Ensure _value_to_colour clamps colour between white and red"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        assert cm._value_to_colour(-100, 0, 10) == "#FFFFFF"
        assert cm._value_to_colour(100, 0, 10) == "#FF0000"

    def test_get_xp_colour_returns_expected_hex(self, mock_cmn, sample_metrics_data):
        """Ensure XP colour getter reads from xp_data member and produces correct colour"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        cm.xp_data[0, 0, 0, 0, 0] = 5.0
        with mock.patch.object(cm, 'get_metric_min_max', return_value=(0.0, 10.0)):
            colour = cm.get_xp_colour(0, 0, 0, 0, 0)

        assert colour == "#FF7F7F"

    def test_get_port_colour_returns_expected_hex(self, mock_cmn, sample_metrics_data):
        """Ensure port colour getter reads from port_data member and produces correct colour"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        cm.port_data[0, 0, 0, 0, 0, 0] = 10.0
        with mock.patch.object(cm, 'get_metric_min_max', return_value=(0.0, 10.0)):
            colour = cm.get_port_colour(0, 0, 0, 0, 0, 0)

        assert colour == "#FF0000"

    def test_get_device_colour_returns_expected_hex(self, mock_cmn, sample_metrics_data):
        """Ensure device colour getter reads from device_data member and produces correct colour"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        cm.device_data[0, 0, 0, 0, 0, 0, 0] = 0.0
        with mock.patch.object(cm, 'get_metric_min_max', return_value=(0.0, 10.0)):
            colour = cm.get_device_colour(0, 0, 0, 0, 0, 0, 0)

        assert colour == "#FFFFFF"

    def test_palette_storage_and_usage(self, mock_cmn, sample_metrics_data):
        """Test that the palette is properly stored and used"""
        palette = QPalette()
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        assert cm.palette is palette
        assert isinstance(cm.palette, QPalette)

    def test_custom_palette_affects_color_output(self, mock_cmn, sample_metrics_data):
        """Test that different palettes produce different base colors"""
        palette1 = QPalette()
        palette2 = QPalette()
        palette2.setColor(QPalette.ColorRole.Window, QColor(200, 200, 200))

        cm1 = CMNMetrics(mock_cmn, sample_metrics_data, palette1)
        cm2 = CMNMetrics(mock_cmn, sample_metrics_data, palette2)

        color1 = cm1._value_to_colour(0, 0, 100)
        color2 = cm2._value_to_colour(0, 0, 100)
        assert color1 != color2

    def test_dark_theme_palette(self, mock_cmn, sample_metrics_data):
        """Test color mapping with a dark theme palette"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, "#2D2D2D")

        cm = CMNMetrics(mock_cmn, sample_metrics_data, dark_palette)

        min_color = cm._value_to_colour(0, 0, 100)
        assert min_color == "#2D2D2D"
        max_color = cm._value_to_colour(100, 0, 100)
        assert max_color == "#FF0000"

    def test_light_theme_palette(self, mock_cmn, sample_metrics_data):
        """Test color mapping with a light theme palette"""
        light_palette = QPalette()
        light_palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")

        cm = CMNMetrics(mock_cmn, sample_metrics_data, light_palette)

        min_color = cm._value_to_colour(0, 0, 100)
        assert min_color == "#FFFFFF"
        max_color = cm._value_to_colour(100, 0, 100)
        assert max_color == "#FF0000"
        mid_color = cm._value_to_colour(50, 0, 100)
        assert mid_color == "#FF7F7F"

    def test_populate_min_max_lookup_table_correctly(self, mock_cmn, sample_metrics_data):
        """Test that the min/max LUT is populated with correct values"""
        cm = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())
        cm.xp_data.fill(np.nan)
        cm.port_data.fill(np.nan)
        cm.device_data.fill(np.nan)
        cm.xp_data[0, 0, 0, 0, 0] = 5.0
        cm.xp_data[1, 0, 0, 0, 1] = 10.0
        cm.device_data[0, 0, 0, 1, 1, 0, 0] = 2.0
        cm.device_data[1, 0, 0, 1, 1, 1, 0] = 15.0
        # Repopulate LUT
        cm._populate_min_max_lookup_table(mock_cmn)

        # Verify min/max are correct
        min_val, max_val = cm.get_metric_min_max(0, 0)
        assert min_val == 2.0
        assert max_val == 15.0

    def test_get_metric_min_max_bounds_checking(self, mock_cmn, sample_metrics_data):
        """Test bounds checking for metric_id and mesh_idx"""
        cm = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())
        cm.xp_data.fill(np.nan)
        cm.port_data.fill(np.nan)
        cm.device_data.fill(np.nan)
        cm._populate_min_max_lookup_table(mock_cmn)

        # Test negative indices
        min_val, max_val = cm.get_metric_min_max(-1, -1)
        assert isinstance(min_val, float)
        assert isinstance(max_val, float)

        # Test out-of-bounds indices
        min_val, max_val = cm.get_metric_min_max(999, 999)
        assert isinstance(min_val, float)
        assert isinstance(max_val, float)

    def test_min_max_with_all_empty_values(self, mock_cmn, sample_metrics_data):
        """Test min/max calculation when all metric values are zero"""
        cm = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())
        cm.xp_data.fill(np.nan)
        cm.port_data.fill(np.nan)
        cm.device_data.fill(np.nan)
        cm._populate_min_max_lookup_table(mock_cmn)

        min_val, max_val = cm.get_metric_min_max(0, 0)
        assert np.isnan(min_val)
        assert np.isnan(max_val)

    def test_min_max_considers_all_data_levels(self, mock_cmn, sample_metrics_data):
        """Test that min/max calculation considers XP, port, and device level data"""
        cm = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())
        cm.xp_data.fill(np.nan)
        cm.port_data.fill(np.nan)
        cm.device_data.fill(np.nan)

        # Set different values at each level
        cm.xp_data[0, 0, 0, 0, 0] = 100.0  # Should be max
        cm.port_data[0, 0, 0, 1, 1, 0] = 1.0   # Should be min
        cm.device_data[0, 0, 0, 2, 2, 1, 0] = 50.0  # Middle value
        cm._populate_min_max_lookup_table(mock_cmn)

        min_val, max_val = cm.get_metric_min_max(0, 0)
        assert min_val == 1.0
        assert max_val == 100.0

    def test_aggregation_basic_mean(self, mock_cmn):
        """Ensure basic device metric aggregation single port"""
        data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5] * 2,
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 2),
            NODE_COLUMN_NAME: [
                "HN-F at X=0 Y=0 Port=0",
                "HN-F at X=0 Y=0 Port=0"
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0],
            NODEID_COLUMN_NAME: [100, 101],
            MESH_COLUMN_NAME: [0] * 2,
            UNITS_COLUMN_NAME: ["unit"] * 2
        })

        metrics = CMNMetrics(mock_cmn, data, QPalette())

        # check device values
        time_idx = 0
        metric_idx = 0
        mesh_idx = 0
        y, x, port = 0, 0, 0

        # Check initial device data
        device_values = metrics.device_data[time_idx, metric_idx, mesh_idx, y, x, port, :2]
        assert np.allclose(device_values, [10.0, 20.0])

        # Check port data is mean of device data: (10 + 20)/2 = 15
        port_value = metrics.port_data[time_idx, metric_idx, mesh_idx, y, x, port]
        assert np.isclose(port_value, 15.0)

        # Check XP data is mean over ports - only one port so same as port mean
        xp_value = metrics.xp_data[time_idx, metric_idx, mesh_idx, y, x]
        assert np.isclose(xp_value, 15.0)

    def test_aggregation_with_empty_ports(self, mock_cmn):
        """Test that empty ports dont contribute data to aggregation"""
        mesh = mock_cmn.meshes[0]
        xp = mesh["xps"][0, 0]
        xp["ports"][1]["num_devices"] = 0  # simulat empty port 1

        # Prepare data for devices only on port 0
        data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical(["metric1", "metric1"]),
            NODE_COLUMN_NAME: [
                "HN-F at X=0 Y=0 Port=0",
                "HN-F at X=0 Y=0 Port=0"
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0],
            NODEID_COLUMN_NAME: [100, 101],
            MESH_COLUMN_NAME: [0] * 2,
            UNITS_COLUMN_NAME: ["unit"] * 2
        })

        metrics = CMNMetrics(mock_cmn, data, QPalette())

        time_idx = 0
        metric_idx = 0
        mesh_idx = 0
        y, x = 0, 0

        port_0_val = metrics.port_data[time_idx, metric_idx, mesh_idx, y, x, 0]
        assert np.isclose(port_0_val, 15.0)

        # port 1 should not have a value
        port_1_val = metrics.port_data[time_idx, metric_idx, mesh_idx, y, x, 1]
        assert np.isnan(port_1_val)

        # only contribution from port 0
        xp_val = metrics.xp_data[time_idx, metric_idx, mesh_idx, y, x]
        assert np.isclose(xp_val, 15.0)

    def test_aggregation_multiple_time_and_metrics(self, mock_cmn):
        """Test that aggregatinos is metric independant"""
        data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 1.0, 1.0],
            METRICS_COLUMN_NAME: pd.Categorical(["metric1", "metric2", "metric1", "metric2"]),
            NODE_COLUMN_NAME: [
                "HN-F at X=0 Y=0 Port=0",
                "HN-F at X=0 Y=0 Port=0",
                "HN-F at X=0 Y=0 Port=0",
                "HN-F at X=0 Y=0 Port=0"
            ],
            VALUE_COLUMN_NAME: [10.0, 100.0, 20.0, 200.0],
            NODEID_COLUMN_NAME: [100] * 4,
            MESH_COLUMN_NAME: [0] * 4,
            UNITS_COLUMN_NAME: ["unit"] * 4
        })

        metrics = CMNMetrics(mock_cmn, data, QPalette())

        time_idx_0 = metrics.time_stamps.tolist().index(0.5)
        time_idx_1 = metrics.time_stamps.tolist().index(1.0)
        metric_idx_1 = metrics.metric_id_map["metric1"]
        metric_idx_2 = metrics.metric_id_map["metric2"]
        mesh_idx = 0
        y, x, port = 0, 0, 0

        # Device data should match input
        dev_val_0_t_0 = metrics.device_data[time_idx_0, metric_idx_1, mesh_idx, y, x, port, 0]
        dev_val_1_t_0 = metrics.device_data[time_idx_0, metric_idx_2, mesh_idx, y, x, port, 0]
        dev_val_0_t_1 = metrics.device_data[time_idx_1, metric_idx_1, mesh_idx, y, x, port, 0]
        dev_val_1_t_1 = metrics.device_data[time_idx_1, metric_idx_2, mesh_idx, y, x, port, 0]
        assert np.isclose(dev_val_0_t_0, 10.0)
        assert np.isclose(dev_val_1_t_0, 100.0)
        assert np.isclose(dev_val_0_t_1, 20.0)
        assert np.isclose(dev_val_1_t_1, 200.0)

        # Values from different metrics should not mix
        port_val_0 = metrics.port_data[time_idx_0, metric_idx_1, mesh_idx, y, x, port]
        port_val_1 = metrics.port_data[time_idx_0, metric_idx_2, mesh_idx, y, x, port]
        xp_val_0 = metrics.xp_data[time_idx_0, metric_idx_1, mesh_idx, y, x]
        xp_val_1 = metrics.xp_data[time_idx_0, metric_idx_2, mesh_idx, y, x]
        port_val_0_t1 = metrics.port_data[time_idx_1, metric_idx_1, mesh_idx, y, x, port]
        port_val_1_t1 = metrics.port_data[time_idx_1, metric_idx_2, mesh_idx, y, x, port]
        xp_val_0_t1 = metrics.xp_data[time_idx_1, metric_idx_1, mesh_idx, y, x]
        xp_val_1_t1 = metrics.xp_data[time_idx_1, metric_idx_2, mesh_idx, y, x]

        assert np.isclose(port_val_0, 10.0)
        assert np.isclose(port_val_1, 100.0)
        assert np.isclose(xp_val_0, 10.0)
        assert np.isclose(xp_val_1, 100.0)
        assert np.isclose(port_val_0_t1, 20.0)
        assert np.isclose(port_val_1_t1, 200.0)
        assert np.isclose(xp_val_0_t1, 20.0)
        assert np.isclose(xp_val_1_t1, 200.0)


class TestCMNMetricsOutlierRemoval:
    """Tests for the outlier removal functionality."""

    @pytest.fixture
    def mock_cmn_simple(self):
        """Simple mock CMN for outlier tests."""
        mock_cmn = MagicMock(spec=CMN)
        mock_cmn.num_meshes = 1
        mock_meshes = np.zeros(1, dtype=mesh_dtype)
        mock_cmn.meshes = mock_meshes
        return mock_cmn

    def test_outlier_removal_basic(self, mock_cmn_simple):
        """Test basic outlier removal functionality."""
        # Create data with outliers
        data_with_outliers = pd.DataFrame({
            TIME_COLUMN_NAME: list(np.arange(0.5, 5.5, 0.5)),
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 10),
            NODE_COLUMN_NAME: ["Global"] * 10,
            VALUE_COLUMN_NAME: [10, 12, 11, 13, 9, 1000, 8, 14, 10, 12],
            # Outlier                              ^^^^
            NODEID_COLUMN_NAME: [pd.NA] * 10,
            MESH_COLUMN_NAME: [0] * 10,
            UNITS_COLUMN_NAME: ["unit"] * 10
        })

        metrics = CMNMetrics(mock_cmn_simple, data_with_outliers, QPalette())

        global_values = metrics.global_data[:, 0, 0]
        assert 1000 not in global_values

    def test_outlier_removal_extreme_values(self, mock_cmn_simple):
        """Test removal of extremely large values (>1e10)."""
        extreme_data = pd.DataFrame({
            TIME_COLUMN_NAME: list(np.arange(0.5, 3.5, 0.5)),
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 6),
            NODE_COLUMN_NAME: ["Global"] * 6,
            VALUE_COLUMN_NAME: [10, 12, 11, 1e15, 9, 13],
            # extreme value                 ^^^^
            NODEID_COLUMN_NAME: [pd.NA] * 6,
            MESH_COLUMN_NAME: [0] * 6,
            UNITS_COLUMN_NAME: ["unit"] * 6
        })

        metrics = CMNMetrics(mock_cmn_simple, extreme_data, QPalette())

        global_values = metrics.global_data[:, 0, 0]
        assert all(val < 1e10 for val in global_values)

    def test_outlier_removal_separate_metrics(self, mock_cmn_simple):
        """Test that outlier removal is done separately for each metric."""
        mixed_metrics_data = pd.DataFrame({
            TIME_COLUMN_NAME: list(np.arange(0.5, 10.5, 0.5)),
            METRICS_COLUMN_NAME: pd.Categorical(
                ["metric1"] * 10 + ["metric2"] * 10
            ),
            NODE_COLUMN_NAME: ["Global"] * 20,
            VALUE_COLUMN_NAME: [
                10, 12, 11, 13, 100, 9, 8, 14, 10, 12,
                #               ^^^ metric1 outlier
                100, 120, 101, 130, 1000, 90, 180, 140, 100, 102
                #                   ^^^^ metric2 outlier
            ],
            NODEID_COLUMN_NAME: [pd.NA] * 20,
            MESH_COLUMN_NAME: [0] * 20,
            UNITS_COLUMN_NAME: ["unit"] * 20
        })

        metrics = CMNMetrics(mock_cmn_simple, mixed_metrics_data, QPalette())
        assert len(metrics.metric_names) == 2

        metric1_data = metrics.global_data[:, 0, 0]
        metric2_data = metrics.global_data[:, 1, 0]

        assert 100 not in metric1_data
        assert 1000 not in metric2_data

    def test_outlier_removal_insufficient_data(self, mock_cmn_simple):
        """Test behavior when there's insufficient data for outlier removal."""
        insufficient_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 1.0, 1.5],  # Only 3 data points
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 3),
            NODE_COLUMN_NAME: ["Global"] * 3,
            VALUE_COLUMN_NAME: [10, 1000, 12],  # One potential outlier
            NODEID_COLUMN_NAME: [pd.NA] * 3,
            MESH_COLUMN_NAME: [0] * 3,
            UNITS_COLUMN_NAME: ["unit"] * 3
        })

        metrics = CMNMetrics(mock_cmn_simple, insufficient_data, QPalette())
        assert metrics is not None
        assert np.array_equal(metrics.global_data[:, 0, 0], np.array([10, 1000, 12]))

    def test_outlier_removal_global_vs_local(self, mock_cmn_simple):
        """Test that global and local metrics are processed separately."""
        mixed_node_data = pd.DataFrame({
            TIME_COLUMN_NAME: list(np.arange(0.5, 10.5, 0.5)),
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 20),
            NODE_COLUMN_NAME: (
                ["Global"] * 10 + ["XP at X=0 Y=0"] * 10
            ),
            VALUE_COLUMN_NAME: [
                10, 12, 11, 13, 100, 9, 8, 14, 10, 12,
                #               ^^^ Global outlier
                100, 120, 101, 130, 1000, 90, 180, 140, 100, 102
                #                   ^^^^ XP outlier
            ],
            NODEID_COLUMN_NAME: [pd.NA] * 20,
            MESH_COLUMN_NAME: [0] * 20,
            UNITS_COLUMN_NAME: ["unit"] * 20
        })

        metrics = CMNMetrics(mock_cmn_simple, mixed_node_data, QPalette())
        XP_data = metrics.xp_data[:, :, 0, 0, 0]  # values for XP(0,0)

        assert 1000 not in XP_data
        assert 100 not in metrics.global_data


class TestCMNMetricsMultiMesh:
    """Tests for multi-mesh functionality."""

    @pytest.fixture
    def mock_cmn_multi_mesh(self):
        """Create a mock CMN object with multiple meshes for testing."""
        mock_cmn = MagicMock(spec=CMN)
        mock_cmn.num_meshes = 3
        mock_meshes = np.zeros(3, dtype=mesh_dtype)

        for mesh_idx in range(3):
            mock_mesh = mock_meshes[mesh_idx]
            mock_mesh["x_dim"] = 2
            mock_mesh["y_dim"] = 2

            for y in range(2):
                for x in range(2):
                    xp = mock_mesh["xps"][y, x]
                    # Set up XP node info
                    xp["node_info"]["coord"]["x"] = x
                    xp["node_info"]["coord"]["y"] = y
                    xp["node_info"]["nodeid"] = 1000 + mesh_idx * 100 + y * 2 + x
                    xp["node_info"]["type"] = CMN_XP_DEVICE_ID
                    xp["node_info"]["type_str"] = "XP"

                    # Set up ports
                    xp["num_device_ports"] = 1

                    # First port has devices
                    port = xp["ports"][0]
                    port["type"] = 1
                    port["type_str"] = "device_port"
                    port["num_devices"] = 2

                    # Add devices to first port
                    for d in range(2):
                        device = port["devices"][d]
                        device["coord"]["x"] = x
                        device["coord"]["y"] = y
                        device["nodeid"] = 100 + mesh_idx * 100 + y * 2 + x + d
                        device["type"] = 1
                        device["type_str"] = "HN-F"

                    # Other ports are empty
                    for p in range(1, CMN_MAX_PORTS):
                        port = xp["ports"][p]
                        port["num_devices"] = 0

        mock_cmn.meshes = mock_meshes
        return mock_cmn

    def test_multi_mesh_global_data_separation(self, mock_cmn_multi_mesh):
        """Test that global data is properly separated by mesh."""
        multi_mesh_global_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 1.0, 1.0, 1.0],
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 6),
            NODE_COLUMN_NAME: ["Global"] * 6,
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0, 15.0, 25.0, 35.0],
            NODEID_COLUMN_NAME: [pd.NA] * 6,
            MESH_COLUMN_NAME: [0, 1, 2, 0, 1, 2],  # Different meshes
            UNITS_COLUMN_NAME: ["unit"] * 6
        })

        metrics = CMNMetrics(mock_cmn_multi_mesh, multi_mesh_global_data, QPalette())
        time_idx_0 = 0  # time=0.5
        time_idx_1 = 1  # time=1.0
        metric_idx = 0  # metric1

        # Mesh 0
        assert metrics.global_data[time_idx_0, metric_idx, 0] == 10.0
        assert metrics.global_data[time_idx_1, metric_idx, 0] == 15.0
        # Mesh 1
        assert metrics.global_data[time_idx_0, metric_idx, 1] == 20.0
        assert metrics.global_data[time_idx_1, metric_idx, 1] == 25.0
        # Mesh 2
        assert metrics.global_data[time_idx_0, metric_idx, 2] == 30.0
        assert metrics.global_data[time_idx_1, metric_idx, 2] == 35.0

    def test_multi_mesh_xp_data_separation(self, mock_cmn_multi_mesh):
        """Test that XP data is properly separated by mesh."""
        multi_mesh_xp_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5] * 6,
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 6),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0",  # Same coordinates, different meshes
                "XP at X=1 Y=0", "XP at X=1 Y=0", "XP at X=1 Y=0"
            ],
            VALUE_COLUMN_NAME: [100.0, 200.0, 300.0, 110.0, 210.0, 310.0],
            NODEID_COLUMN_NAME: [pd.NA] * 6,
            MESH_COLUMN_NAME: [0, 1, 2, 0, 1, 2],
            UNITS_COLUMN_NAME: ["unit"] * 6
        })

        metrics = CMNMetrics(mock_cmn_multi_mesh, multi_mesh_xp_data, QPalette())
        time_idx = 0
        metric_idx = 0

        # XP at (0,0) in different meshes
        assert metrics.xp_data[time_idx, metric_idx, 0, 0, 0] == 100.0
        assert metrics.xp_data[time_idx, metric_idx, 1, 0, 0] == 200.0
        assert metrics.xp_data[time_idx, metric_idx, 2, 0, 0] == 300.0
        # XP at (1,0) in different meshes
        assert metrics.xp_data[time_idx, metric_idx, 0, 0, 1] == 110.0
        assert metrics.xp_data[time_idx, metric_idx, 1, 0, 1] == 210.0
        assert metrics.xp_data[time_idx, metric_idx, 2, 0, 1] == 310.0

    def test_multi_mesh_device_data_separation(self, mock_cmn_multi_mesh):
        """Test that device data is properly separated by mesh."""
        multi_mesh_device_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5] * 6,
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 6),
            NODE_COLUMN_NAME: ["HN-F at X=0 Y=0 Port=0"] * 6,
            VALUE_COLUMN_NAME: [50.0, 60.0, 70.0, 55.0, 65.0, 75.0],
            NODEID_COLUMN_NAME: [100, 200, 300, 101, 201, 301],  # Different nodeids for different meshes
            MESH_COLUMN_NAME: [0, 1, 2, 0, 1, 2],
            UNITS_COLUMN_NAME: ["unit"] * 6
        })

        metrics = CMNMetrics(mock_cmn_multi_mesh, multi_mesh_device_data, QPalette())
        time_idx = 0
        metric_idx = 0
        y, x, port = 0, 0, 0

        # Mesh 0
        assert metrics.device_data[time_idx, metric_idx, 0, y, x, port, 0] == 50.0
        assert metrics.device_data[time_idx, metric_idx, 0, y, x, port, 1] == 55.0
        # Mesh 1
        assert metrics.device_data[time_idx, metric_idx, 1, y, x, port, 0] == 60.0
        assert metrics.device_data[time_idx, metric_idx, 1, y, x, port, 1] == 65.0
        # Mesh 2
        assert metrics.device_data[time_idx, metric_idx, 2, y, x, port, 0] == 70.0
        assert metrics.device_data[time_idx, metric_idx, 2, y, x, port, 1] == 75.0

    def test_invalid_mesh_index_filtering(self, mock_cmn_multi_mesh):
        """Test that invalid mesh indices are properly filtered out."""
        invalid_mesh_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5] * 8,
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 8),
            NODE_COLUMN_NAME: [
                "Global", "Global", "Global", "Global",
                "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0"
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0],
            NODEID_COLUMN_NAME: [pd.NA] * 8,
            MESH_COLUMN_NAME: [0, 1, 2, 5, 0, 1, 2, -1],  # 5 and -1 should be ignored
            UNITS_COLUMN_NAME: ["unit"] * 8
        })

        # Should not raise exception:
        metrics = CMNMetrics(mock_cmn_multi_mesh, invalid_mesh_data, QPalette())
        time_idx = 0
        metric_idx = 0

        # Valid mesh indices should have data
        assert metrics.global_data[time_idx, metric_idx, 0] == 10.0
        assert metrics.global_data[time_idx, metric_idx, 1] == 20.0
        assert metrics.global_data[time_idx, metric_idx, 2] == 30.0
        assert metrics.xp_data[time_idx, metric_idx, 0, 0, 0] == 50.0
        assert metrics.xp_data[time_idx, metric_idx, 1, 0, 0] == 60.0
        assert metrics.xp_data[time_idx, metric_idx, 2, 0, 0] == 70.0
        assert metrics.global_data.shape[2] == 3  # Should still be 3 meshes

    def test_mixed_mesh_data_types(self, mock_cmn_multi_mesh):
        """Test handling of mixed data types across different meshes."""
        mixed_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5] * 9,
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 9),
            NODE_COLUMN_NAME: [
                "Global", "Global", "Global",
                "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0",
                "HN-F at X=0 Y=0 Port=0", "HN-F at X=0 Y=0 Port=0", "HN-F at X=0 Y=0 Port=0"
            ],
            VALUE_COLUMN_NAME: [100.0, 200.0, 300.0, 10.0, 20.0, 30.0, 1.0, 2.0, 3.0],
            NODEID_COLUMN_NAME: [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, 100, 200, 300],
            MESH_COLUMN_NAME: [0, 1, 2, 0, 1, 2, 0, 1, 2],
            UNITS_COLUMN_NAME: ["unit"] * 9
        })

        metrics = CMNMetrics(mock_cmn_multi_mesh, mixed_data, QPalette())
        time_idx = 0
        metric_idx = 0

        # Check all data types are properly distributed across meshes
        for mesh_idx in range(3):
            expected_global = 100.0 + mesh_idx * 100.0
            expected_xp = 10.0 + mesh_idx * 10.0
            expected_device = 1.0 + mesh_idx * 1.0
            assert metrics.global_data[time_idx, metric_idx, mesh_idx] == expected_global
            assert metrics.xp_data[time_idx, metric_idx, mesh_idx, 0, 0] == expected_xp
            assert metrics.device_data[time_idx, metric_idx, mesh_idx, 0, 0, 0, 0] == expected_device

    def test_empty_mesh_handling(self, mock_cmn_multi_mesh):
        """Test handling when some meshes have no data."""
        partial_mesh_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 2),
            NODE_COLUMN_NAME: ["Global", "XP at X=0 Y=0"],
            VALUE_COLUMN_NAME: [100.0, 10.0],
            NODEID_COLUMN_NAME: [pd.NA, pd.NA],
            MESH_COLUMN_NAME: [0, 2],  # Only mesh 0 and 2 have data, mesh 1 is empty
            UNITS_COLUMN_NAME: ["unit"] * 2
        })

        metrics = CMNMetrics(mock_cmn_multi_mesh, partial_mesh_data, QPalette())
        time_idx = 0
        metric_idx = 0

        # Mesh 0 and 2 must have data
        assert metrics.global_data[time_idx, metric_idx, 0] == 100.0
        assert np.isnan(metrics.global_data[time_idx, metric_idx, 2])  # No global data for mesh 2
        assert metrics.xp_data[time_idx, metric_idx, 2, 0, 0] == 10.0

        # Mesh 1 should be empty
        assert np.isnan(metrics.global_data[time_idx, metric_idx, 1])
        assert np.isnan(metrics.xp_data[time_idx, metric_idx, 1, 0, 0])


class TestCMNMetricsUnits(TestCMNMetrics, TestCMNMetricsMultiMesh):
    """Tests for units handling functionality."""

    @pytest.fixture
    def sample_metrics_data_with_units(self):
        """Create sample metrics DataFrame with different units for testing."""
        return pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 1.0, 1.0, 1.0],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric2",
                "metric1", "metric2", "metric3"
            ]),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0",
                "XP at X=1 Y=0",
                "HN-F (100) at X=0 Y=0 Port=0",
                "XP at X=0 Y=1",
                "HN-F (101) at X=1 Y=0 Port=0",
                "Global"
            ],
            VALUE_COLUMN_NAME: [10.5, 20.3, 30.7, 15.2, 25.8, 40.1],
            NODEID_COLUMN_NAME: [0, 1, 100, 2, 101, 0],
            MESH_COLUMN_NAME: [0] * 6,
            UNITS_COLUMN_NAME: ["unit1", "unit1", "unit2", "unit1", "unit2", "unit3"]
        })

    def test_units_initialization_basic(self, mock_cmn, sample_metrics_data_with_units):
        """Test basic units initialization and mapping."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data_with_units, QPalette())

        # Check that metric_units array is created correctly
        assert len(metrics.metric_units) == 3

        metric1 = metrics.metric_id_map["metric1"]
        metric2 = metrics.metric_id_map["metric2"]
        metric3 = metrics.metric_id_map["metric3"]
        assert metrics.metric_units[metric1] == "unit1"
        assert metrics.metric_units[metric2] == "unit2"
        assert metrics.metric_units[metric3] == "unit3"

    def test_units_missing_or_empty(self, mock_cmn):
        """Test handling of missing or empty units."""
        missing_units_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric_with_unit", "metric_without_unit",
            ]),
            NODE_COLUMN_NAME: ["Global", "Global"],
            VALUE_COLUMN_NAME: [10.0, 20.0],
            NODEID_COLUMN_NAME: [pd.NA] * 2,
            MESH_COLUMN_NAME: [0] * 2,
            UNITS_COLUMN_NAME: ["valid_unit", ""]
        })

        metrics = CMNMetrics(mock_cmn, missing_units_data, QPalette())

        valid_idx = metrics.metric_id_map["metric_with_unit"]
        missing_idx = metrics.metric_id_map["metric_without_unit"]

        assert metrics.metric_units[valid_idx] == "valid_unit"
        assert metrics.metric_units[missing_idx] == ""

    def test_units_array_length_matches_metrics(self, mock_cmn, sample_metrics_data_with_units):
        """Test that units array length always matches metrics array length."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data_with_units, QPalette())

        assert len(metrics.metric_units) == len(metrics.metric_names)
        assert len(metrics.metric_units) == metrics.num_metrics

    def test_units_across_multiple_metrics_and_meshes(self, mock_cmn_multi_mesh):
        """Test units handling with multiple metrics across multiple meshes."""
        multi_metric_mesh_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5] * 12,
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric2", "metric3", "metric1",
                "metric1", "metric2", "metric3", "metric1",
                "metric1", "metric2", "metric3", "metric1"
            ]),
            NODE_COLUMN_NAME: ["Global"] * 12,
            VALUE_COLUMN_NAME: [100, 50, 2000, 110, 120, 55, 2100, 130, 105, 48, 1950, 115],
            NODEID_COLUMN_NAME: [pd.NA] * 12,
            MESH_COLUMN_NAME: [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2],
            UNITS_COLUMN_NAME: ["unit1", "unit2", "unit3", "unit1", "unit1", "unit2", "unit3", "unit1", "unit1", "unit2", "unit3", "unit1"]
        })

        metrics = CMNMetrics(mock_cmn_multi_mesh, multi_metric_mesh_data, QPalette())

        metric1 = metrics.metric_id_map["metric1"]
        metric2 = metrics.metric_id_map["metric2"]
        metric3 = metrics.metric_id_map["metric3"]

        # Units should be consistent regardless of mesh
        assert metrics.metric_units[metric1] == "unit1"
        assert metrics.metric_units[metric2] == "unit2"
        assert metrics.metric_units[metric3] == "unit3"
