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
CMN metrics data structures and operations.
"""

from PySide6.QtGui import QPalette, QColor
import numpy as np
import pandas as pd
from typing import Dict
import warnings

from wperf_cmn_visualizer.cmn import CMN_MAX_PORTS, CMN_MAX_CHILDS, CMN_MAX_MESH_WIDTH, CMN_MAX_MESH_HEIGHT
from wperf_cmn_visualizer.cmn import CMN
from wperf_cmn_visualizer.telemetry_loader import (
    TIME_COLUMN_NAME, METRICS_COLUMN_NAME, NODE_COLUMN_NAME, VALUE_COLUMN_NAME,
    NODEID_COLUMN_NAME, MESH_COLUMN_NAME, UNITS_COLUMN_NAME
)


class CMNMetrics:
    """
    Handles CMN metrics by storing them in structured numpy arrays
    indexed by time, mesh, and coordinates within the mesh.

    Attributes:
        self.metric_names (np.ndarray[dtype=str]): Compact list of unique names indexed by metric ids.
        self.metric_id_map (Dict[str, int]): Map from metric string to metric id
        self.time_stamps (np.ndarray[dtype=f8]): 1d numpy array of unique time stamps which which data is available.
        self.num_time_stamps (int): number of time_stamps
        self.data (np.nradday): 4d numpy array, index with self.data[time_stamp, mesh_index, XP coord Y, XP coord X]
    """
    def __init__(self, cmn: CMN, metrics_data: pd.DataFrame, palette: QPalette) -> None:
        """
        Contruct CMNMesh object.
        Args:
            cmn (CMN): Read-only CMN object used to validate input data. Invalid input is ignored.
            metrics_data (pd.DataFrame): Data frame from pandas loaded from cmn_telemtry_loader.
            palette (QPalette): Colors used to determine heatmap colouring
        """

        # Metric names and corresponding IDs (categorical for compactness)
        self.metric_names: np.ndarray = metrics_data[METRICS_COLUMN_NAME].cat.categories.to_numpy(dtype=str)
        self.metric_id_map: Dict[str, int] = {name: idx for idx, name in enumerate(self.metric_names)}
        self.num_metrics: int = len(self.metric_names)

        self.metric_units: np.ndarray = np.array([
            metrics_data.groupby(METRICS_COLUMN_NAME, observed=True)[UNITS_COLUMN_NAME].first().get(name, "")
            for name in self.metric_names
        ], dtype=str)

        # Extract coordinate and node info using regex from the 'node' column
        # node column has three formats:
        # 1> "global" which indicates the entire mesh
        # 2> "XP at X=0 Y=0" which indicates a specific XP at given coordinate
        # 3> HN-F (101) at X=0 Y=0 Port=0 which indicates a device on a specific XP and port. Device identified using nodeid.
        node_info: pd.DataFrame = metrics_data[NODE_COLUMN_NAME].str.extract(
            r"^(?:(?P<device>.+?) at X=(?P<x_device>\d+) Y=(?P<y_device>\d+) Port=(?P<port>\d+)"
            r"|(?P<device_xp>XP) at X=(?P<x_xp>\d+) Y=(?P<y_xp>\d+)"
            r"|(?P<global>Global))$"
        )
        node_info[NODEID_COLUMN_NAME] = metrics_data[NODEID_COLUMN_NAME]
        node_info[MESH_COLUMN_NAME] = metrics_data[MESH_COLUMN_NAME]

        # remove outliers
        metrics_data, node_info = self._remove_outliers_mean_std(metrics_data, node_info)

        self.time_stamps: np.ndarray = np.sort(metrics_data[TIME_COLUMN_NAME].unique())
        self.num_time_stamps: int = len(self.time_stamps)

        # data holding members: Global level, XP level, Port level, Device level
        # Initialize with NaN
        self.global_data: np.ndarray = np.full(
            shape=(self.num_time_stamps, self.num_metrics, cmn.num_meshes),
            fill_value=np.nan,
            dtype="f8"
        )
        self.xp_data: np.ndarray = np.full(
            shape=(
                self.num_time_stamps, self.num_metrics, cmn.num_meshes,
                CMN_MAX_MESH_HEIGHT, CMN_MAX_MESH_WIDTH
            ),
            fill_value=np.nan,
            dtype="f8"
        )
        self.port_data: np.ndarray = np.full(
            shape=(
                self.num_time_stamps, self.num_metrics, cmn.num_meshes,
                CMN_MAX_MESH_HEIGHT, CMN_MAX_MESH_WIDTH,
                CMN_MAX_PORTS
            ),
            fill_value=np.nan,
            dtype="f8"
        )
        self.device_data: np.ndarray = np.full(
            shape=(
                self.num_time_stamps, self.num_metrics, cmn.num_meshes,
                CMN_MAX_MESH_HEIGHT, CMN_MAX_MESH_WIDTH,
                CMN_MAX_PORTS, CMN_MAX_CHILDS
            ),
            fill_value=np.nan,
            dtype="f8"
        )

        time_indices = np.searchsorted(self.time_stamps, metrics_data[TIME_COLUMN_NAME].to_numpy())
        metric_ids = metrics_data[METRICS_COLUMN_NAME].cat.codes.to_numpy()
        metric_values = metrics_data[VALUE_COLUMN_NAME].to_numpy()

        self._load_global_data(node_info, cmn, time_indices, metric_ids, metric_values)
        self._load_device_data(node_info, cmn, time_indices, metric_ids, metric_values)
        self._load_xp_data(node_info, cmn, time_indices, metric_ids, metric_values)

        # min/max look up table. arrays storing min and max values for each metric and mesh.
        self.min_values: np.ndarray = np.full((self.num_metrics, cmn.num_meshes), np.nan, dtype="f8")
        self.max_values: np.ndarray = np.full((self.num_metrics, cmn.num_meshes), np.nan, dtype="f8")
        self._populate_min_max_lookup_table(cmn)

        self.palette: QPalette = palette
        self.base_color = self.palette.color(QPalette.ColorRole.Window)

    def _remove_outliers_mean_std(
        self,
        df: pd.DataFrame, node_info: pd.DataFrame,
        std_multiplier: float = 2.0
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Properly removes outliers by filtering per-metric and per-node-type.
        Keeps values within [mean - N*std, mean + N*std] AND < 1e6.
        """
        keep_mask = pd.Series(False, index=df.index)

        global_mask = node_info["global"].notna()
        non_global_mask = ~global_mask

        for metric in self.metric_names:
            metric_mask = df[METRICS_COLUMN_NAME] == metric

            # GLOBAL
            subset_global = df[metric_mask & global_mask]
            subset_global = subset_global[subset_global[VALUE_COLUMN_NAME] < 1e10]

            if len(subset_global) >= 4:
                values = subset_global[VALUE_COLUMN_NAME]
                mean = values.mean()
                std = values.std()
                lower = mean - std_multiplier * std
                upper = mean + std_multiplier * std
                valid_mask = (values >= lower) & (values <= upper)
                keep_mask.loc[subset_global[valid_mask].index] = True
            else:
                keep_mask.loc[subset_global.index] = True

            # NON-GLOBAL
            subset_local = df[metric_mask & non_global_mask]
            subset_local = subset_local[subset_local[VALUE_COLUMN_NAME] < 1e10]

            if len(subset_local) >= 4:
                values = subset_local[VALUE_COLUMN_NAME]
                mean = values.mean()
                std = values.std()
                lower = mean - std_multiplier * std
                upper = mean + std_multiplier * std
                valid_mask = (values >= lower) & (values <= upper)
                keep_mask.loc[subset_local[valid_mask].index] = True
            else:
                keep_mask.loc[subset_local.index] = True

        filtered_df = df[keep_mask].reset_index(drop=True)
        filtered_node_info = node_info[keep_mask].reset_index(drop=True)

        return filtered_df, filtered_node_info

    def _load_global_data(self, node_info, cmn, time_indices, metric_ids, metric_values) -> None:
        global_mask = node_info["global"].notna()
        if global_mask.any():
            global_rows = np.where(global_mask)[0]
            global_t = time_indices[global_rows]
            global_mesh_indices = node_info.loc[global_mask, MESH_COLUMN_NAME].astype(int).to_numpy()

            valid_mesh_mask = (global_mesh_indices >= 0) & (global_mesh_indices < cmn.num_meshes)
            if valid_mesh_mask.any():
                valid_rows = global_rows[valid_mesh_mask]
                global_t = time_indices[valid_rows]
                global_m = global_mesh_indices[valid_mesh_mask]
                global_ids = metric_ids[valid_rows]
                global_vals = metric_values[valid_rows]
                self.global_data[global_t, global_ids, global_m] = global_vals

    def _load_xp_data(self, node_info, cmn, time_indices, metric_ids, metric_values) -> None:
        x_xp = node_info["x_xp"].astype("float")
        y_xp = node_info["y_xp"].astype("float")
        mesh_indices = node_info[MESH_COLUMN_NAME].astype("float")

        xp_mask = (
            x_xp.notna() & y_xp.notna() & mesh_indices.notna()
            & (x_xp >= 0) & (x_xp < CMN_MAX_MESH_WIDTH)
            & (y_xp >= 0) & (y_xp < CMN_MAX_MESH_HEIGHT)
            & (mesh_indices >= 0) & (mesh_indices < cmn.num_meshes)
        )

        if xp_mask.any():
            xp_rows = np.where(xp_mask)[0]
            xp_t = time_indices[xp_rows]
            xp_m = node_info.loc[xp_mask, MESH_COLUMN_NAME].astype(int).to_numpy()
            xp_y = node_info.loc[xp_mask, "y_xp"].astype(int).to_numpy()
            xp_x = node_info.loc[xp_mask, "x_xp"].astype(int).to_numpy()
            xp_ids = metric_ids[xp_rows]
            xp_vals = metric_values[xp_rows]
            self.xp_data[xp_t, xp_ids, xp_m, xp_y, xp_x] = xp_vals

    def _load_device_data(self, node_info, cmn, time_indices, metric_ids, metric_values) -> None:
        x_dev = node_info["x_device"].astype("float")
        y_dev = node_info["y_device"].astype("float")
        port_dev = node_info["port"].astype("float")
        mesh_indices = node_info[MESH_COLUMN_NAME].astype("float")

        device_mask = (
            x_dev.notna() & y_dev.notna() & port_dev.notna() & mesh_indices.notna()
            & (x_dev >= 0) & (x_dev < CMN_MAX_MESH_WIDTH)
            & (y_dev >= 0) & (y_dev < CMN_MAX_MESH_HEIGHT)
            & (port_dev >= 0) & (port_dev < CMN_MAX_PORTS)
            & (mesh_indices >= 0) & (mesh_indices < cmn.num_meshes)
        )

        if device_mask.any():
            dev_rows = np.where(device_mask)[0]
            dev_t = time_indices[dev_rows]
            dev_nodeids = node_info.loc[device_mask, NODEID_COLUMN_NAME].astype(int)
            dev_mesh_indices = node_info.loc[device_mask, MESH_COLUMN_NAME].astype(int)
            dev_y = node_info.loc[device_mask, "y_device"].astype(int)
            dev_x = node_info.loc[device_mask, "x_device"].astype(int)
            dev_ports = node_info.loc[device_mask, "port"].astype(int)
            dev_ids = metric_ids[dev_rows]
            dev_vals = metric_values[dev_rows]

            for t, nodeid, mesh_idx, y, x, port, mid, val in zip(
                dev_t, dev_nodeids, dev_mesh_indices, dev_y, dev_x, dev_ports, dev_ids, dev_vals
            ):
                # Ensure mesh_idx is valid before accessing cmn.meshes
                if 0 <= mesh_idx < cmn.num_meshes:
                    for device_idx, device in enumerate(cmn.meshes[mesh_idx]["xps"][y, x]["ports"][port]["devices"]):
                        if device["nodeid"] == nodeid:
                            self.device_data[t, mid, mesh_idx, y, x, port, device_idx] = val

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                self.port_data = np.nanmean(self.device_data, axis=6)
                self.xp_data   = np.nanmean(self.port_data, axis=5)

    def get_metric_min_max(self, metric_id: int, mesh_idx: int) -> tuple[float, float]:
        """
        Get the minimum and maximum non-zero values for a given metric and mesh.
        Args:
            metric_id: Metric identifier to filter by.
            mesh_idx: Index of the mesh to extract from.
        Returns:
            A tuple containing (min_value, max_value) for the selected metric.
        """
        metric_id = max(0, min(metric_id, self.num_metrics - 1))
        mesh_idx = max(0, min(mesh_idx, self.min_values.shape[1] - 1))

        return (
            float(self.min_values[metric_id, mesh_idx]),
            float(self.max_values[metric_id, mesh_idx])
        )

    def _populate_min_max_lookup_table(self, cmn: CMN) -> None:
        """
        Populate the min/max cache for all metric/mesh combinations.
        """
        for metric_id in range(self.num_metrics):
            for mesh_idx in range(cmn.num_meshes):
                min_val = np.inf
                max_val = -np.inf

                # XP level
                xp_vals = self.xp_data[:, metric_id, mesh_idx, :, :]
                xp_mask = np.isfinite(xp_vals)
                if np.any(xp_mask):
                    xp_filtered = xp_vals[xp_mask]
                    min_val = min(min_val, np.nanmin(xp_filtered))
                    max_val = max(max_val, np.nanmax(xp_filtered))

                # Port level
                port_vals = self.port_data[:, metric_id, mesh_idx, :, :, :]
                port_mask = np.isfinite(port_vals)
                if np.any(port_mask):
                    port_filtered = port_vals[port_mask]
                    min_val = min(min_val, np.nanmin(port_filtered))
                    max_val = max(max_val, np.nanmax(port_filtered))

                # Device level
                dev_vals = self.device_data[:, metric_id, mesh_idx, :, :, :, :]
                dev_mask = np.isfinite(dev_vals)
                if np.any(dev_mask):
                    dev_filtered = dev_vals[dev_mask]
                    min_val = min(min_val, np.nanmin(dev_filtered))
                    max_val = max(max_val, np.nanmax(dev_filtered))

                if min_val == np.inf:
                    min_val = np.nan
                if max_val == -np.inf:
                    max_val = np.nan
                self.min_values[metric_id, mesh_idx] = min_val
                self.max_values[metric_id, mesh_idx] = max_val

    def _value_to_colour(self, value: float, vmin: float, vmax: float) -> QColor:
        """Blend between window colour and bright red based on value."""
        if np.isnan(value) or np.isnan(vmin) or np.isnan(vmax) or vmax <= vmin:
            return self.base_color

        norm = (value - vmin) / (vmax - vmin)
        norm = max(0.0, min(norm, 1.0))
        inv_norm = 1 - norm
        r = int(self.base_color.red() * inv_norm + 255.0 * norm)
        g = int(self.base_color.green() * inv_norm)
        b = int(self.base_color.blue() * inv_norm)
        return QColor(r, g, b)

    def get_xp_colour(self, time_idx: int, metric_id: int, mesh_idx: int, y: int, x: int) -> QColor:
        val = self.xp_data[time_idx, metric_id, mesh_idx, y, x]
        vmin, vmax = self.get_metric_min_max(metric_id, mesh_idx)
        return self._value_to_colour(val, vmin, vmax)

    def get_port_colour(self, time_idx: int, metric_id: int, mesh_idx: int, y: int, x: int, port: int) -> QColor:
        val = self.port_data[time_idx, metric_id, mesh_idx, y, x, port]
        vmin, vmax = self.get_metric_min_max(metric_id, mesh_idx)
        return self._value_to_colour(val, vmin, vmax)

    def get_device_colour(self, time_idx: int, metric_id: int, mesh_idx: int, y: int, x: int, port: int, device_idx: int) -> QColor:
        val = self.device_data[time_idx, metric_id, mesh_idx, y, x, port, device_idx]
        vmin, vmax = self.get_metric_min_max(metric_id, mesh_idx)
        return self._value_to_colour(val, vmin, vmax)
