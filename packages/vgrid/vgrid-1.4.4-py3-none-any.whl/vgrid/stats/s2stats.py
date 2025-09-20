"""
This module provides functions for generating statistics for S2 DGGS cells.
"""

import math
import pandas as pd
import numpy as np
import argparse
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import TwoSlopeNorm
from vgrid.utils.constants import (
    AUTHALIC_AREA,
    DGGS_TYPES,
    VMIN_QUAD,
    VMAX_QUAD,
    VCENTER_QUAD,
)
from vgrid.generator.s2grid import s2grid
from vgrid.utils.geometry import check_crossing_geom, characteristic_length_scale

min_res = DGGS_TYPES["s2"]["min_res"]
max_res = DGGS_TYPES["s2"]["max_res"]


def s2_metrics(res, unit: str = "m"):  # length unit is km, area unit is km2
    """
    Calculate metrics for S2 DGGS cells at a given resolution.

    Args:
        res: Resolution level (0-30)
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'

    Returns:
        tuple: (num_cells, edge_length_in_unit, cell_area_in_unit_squared)
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")

    num_cells = 6 * (4**res)

    # Calculate area in km² first
    avg_cell_area = AUTHALIC_AREA / num_cells  # area in m2
    avg_edge_len = math.sqrt(avg_cell_area)
    cls = characteristic_length_scale(avg_cell_area, unit=unit)
    # Convert to requested unit
    if unit == "km":
        avg_cell_area = avg_cell_area / (10**6)  # Convert km² to m²
        avg_edge_len = avg_edge_len / (10**3)  # Convert km to m

    return num_cells, avg_edge_len, avg_cell_area, cls


def s2stats(unit: str = "m"):  # length unit is km, area unit is km2
    """
    Generate statistics for S2 DGGS cells.

    Args:
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'

    Returns:
        pandas.DataFrame: DataFrame containing S2 DGGS statistics with columns:
            - Resolution: Resolution level (0-30)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_{unit}: Average edge length in the given unit
            - Avg_Cell_Area_{unit}2: Average cell area in the squared unit
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")

    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lens = []
    avg_cell_areas = []
    cls_list = []
    for res in range(min_res, max_res + 1):
        num_cells, avg_edge_len, avg_cell_area, cls = s2_metrics(
            res, unit=unit
        )  # length unit is km, area unit is km2
        resolutions.append(res)
        num_cells_list.append(num_cells)
        avg_edge_lens.append(avg_edge_len)
        avg_cell_areas.append(avg_cell_area)
        cls_list.append(cls)
    # Create DataFrame
    # Build column labels with unit awareness
    avg_edge_len = f"avg_edge_len_{unit}"
    unit_area_label = {"m": "m2", "km": "km2"}[unit]
    avg_cell_area = f"avg_cell_area_{unit_area_label}"
    cls_label = f"cls_{unit}"
    df = pd.DataFrame(
        {
            "resolution": resolutions,
            "number_of_cells": num_cells_list,
            avg_edge_len: avg_edge_lens,
            avg_cell_area: avg_cell_areas,
            cls_label: cls_list,
        }
    )

    return df


def s2stats_cli():
    """
    Command-line interface for generating S2 DGGS statistics.

    CLI options:
      -unit, --unit {m,km}
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-unit", "--unit", dest="unit", choices=["m", "km"], default="m"
    )
    args = parser.parse_args()  # type: ignore

    unit = args.unit

    # Get the DataFrame
    df = s2stats(unit=unit)

    # Display the DataFrame
    print(df)


def s2inspect(res):
    """
    Generate comprehensive inspection data for S2 DGGS cells at a given resolution.

    Args:
        res: S2 resolution level (0-30)

    Returns:
        geopandas.GeoDataFrame: DataFrame containing S2 cell inspection data with columns:
            - s2: S2 cell ID
            - resolution: Resolution level
            - geometry: Cell geometry
            - cell_area: Cell area in square meters
            - cell_perimeter: Cell perimeter in meters
            - crossed: Whether cell crosses the dateline
            - norm_area: Normalized area (cell_area / mean_area)
            - ipq: Isoperimetric Quotient compactness
            - zsc: Zonal Standardized Compactness
    """
    s2_gpd = s2grid(res, output_format="gpd")
    s2_gpd["crossed"] = s2_gpd["geometry"].apply(check_crossing_geom)
    mean_area = s2_gpd["cell_area"].mean()
    # Calculate normalized area
    s2_gpd["norm_area"] = s2_gpd["cell_area"] / mean_area
    # Calculate IPQ compactness using the standard formula: CI = 4πA/P²
    s2_gpd["ipq"] = 4 * np.pi * s2_gpd["cell_area"] / (s2_gpd["cell_perimeter"] ** 2)
    # Calculate zonal standardized compactness
    s2_gpd["zsc"] = (
        np.sqrt(
            4 * np.pi * s2_gpd["cell_area"]
            - np.power(s2_gpd["cell_area"], 2) / np.power(6378137, 2)
        )
        / s2_gpd["cell_perimeter"]
    )
    return s2_gpd


def s2_norm_area(s2_gpd):
    """
    Plot normalized area map for S2 cells.

    Args:
        s2_gpd: GeoDataFrame from s2inspect function
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    vmin, vmax, vcenter = s2_gpd["norm_area"].min(), s2_gpd["norm_area"].max(), 1
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    s2_gpd = s2_gpd[~s2_gpd["crossed"]]  # remove cells that cross the dateline
    s2_gpd.to_crs("proj=moll").plot(
        column="norm_area",
        ax=ax,
        norm=norm,
        legend=True,
        cax=cax,
        cmap="RdYlBu_r",
        legend_kwds={"label": "cell area/mean cell area", "orientation": "horizontal"},
    )
    world_countries = gpd.read_file(
        "https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson"
    )
    world_countries.boundary.to_crs("proj=moll").plot(
        color=None, edgecolor="black", linewidth=0.2, ax=ax
    )
    ax.axis("off")
    cb_ax = fig.axes[1]
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel="S2 Normalized Area", fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()


def s2_compactness(s2_gpd):
    """
    Plot IPQ compactness map for S2 cells.

    Args:
        s2_gpd: GeoDataFrame from s2inspect function
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    # vmin, vmax, vcenter = s2_gpd['ipq'].min(), s2_gpd['ipq'].max(),np.mean([s2_gpd['ipq'].min(), s2_gpd['ipq'].max()])
    norm = TwoSlopeNorm(vmin=VMIN_QUAD, vcenter=VCENTER_QUAD, vmax=VMAX_QUAD)
    s2_gpd = s2_gpd[~s2_gpd["crossed"]]  # remove cells that cross the dateline
    s2_gpd.to_crs("proj=moll").plot(
        column="ipq",
        ax=ax,
        norm=norm,
        legend=True,
        cax=cax,
        cmap="viridis",
        legend_kwds={"orientation": "horizontal"},
    )
    world_countries = gpd.read_file(
        "https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson"
    )
    world_countries.boundary.to_crs("proj=moll").plot(
        color=None, edgecolor="black", linewidth=0.2, ax=ax
    )
    ax.axis("off")
    cb_ax = fig.axes[1]
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel="S2 IPQ Compactness", fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()


def s2_norm_area_hist(s2_gpd):
    """
    Plot histogram of normalized area for S2 cells.

    This function creates a histogram visualization showing the distribution
    of normalized areas for S2 cells, helping to understand area variations
    and identify patterns in area distortion.

    Args:
        s2_gpd: GeoDataFrame from s2inspect function
    """
    # Filter out cells that cross the dateline
    s2_gpd_filtered = s2_gpd[~s2_gpd["crossed"]]

    # Create the histogram with color ramp
    fig, ax = plt.subplots(figsize=(10, 6))

    # Get histogram data
    counts, bins, patches = ax.hist(
        s2_gpd_filtered["norm_area"], bins=50, alpha=0.7, edgecolor="black"
    )

    # Create color ramp using the same normalization as the map function
    vmin, vmax, vcenter = (
        s2_gpd_filtered["norm_area"].min(),
        s2_gpd_filtered["norm_area"].max(),
        1,
    )
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)

    # Apply colors to histogram bars using the same color mapping as the map
    for i, patch in enumerate(patches):
        # Use the center of each bin for color mapping
        bin_center = (bins[i] + bins[i + 1]) / 2
        color = plt.cm.RdYlBu_r(norm(bin_center))
        patch.set_facecolor(color)

    # Add reference line at mean area (norm_area = 1)
    ax.axvline(
        x=1, color="red", linestyle="--", linewidth=2, label="Mean Area (norm_area = 1)"
    )

    # Add statistics text box
    stats_text = f"Mean: {s2_gpd_filtered['norm_area'].mean():.3f}\nStd: {s2_gpd_filtered['norm_area'].std():.3f}\nMin: {s2_gpd_filtered['norm_area'].min():.3f}\nMax: {s2_gpd_filtered['norm_area'].max():.3f}"
    ax.text(
        0.02,
        0.98,
        stats_text,
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    # Customize the plot
    ax.set_xlabel("S2 normalized area", fontsize=14)
    ax.set_ylabel("Number of cells", fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()


def s2_compactness_hist(s2_gpd):
    """
    Plot histogram of IPQ compactness for S2 cells.

    This function creates a histogram visualization showing the distribution
    of Isoperimetric Quotient (IPQ) compactness values for S2 cells, helping
    to understand how close cells are to being regular squares.

    Args:
        s2_gpd: GeoDataFrame from s2inspect function
    """
    # Filter out cells that cross the dateline
    s2_gpd_filtered = s2_gpd[~s2_gpd["crossed"]]

    # Create the histogram with color ramp
    fig, ax = plt.subplots(figsize=(10, 6))

    # Get histogram data
    counts, bins, patches = ax.hist(
        s2_gpd_filtered["ipq"], bins=50, alpha=0.7, edgecolor="black"
    )

    # Create color ramp using the same normalization as the map function
    norm = TwoSlopeNorm(vmin=VMIN_QUAD, vcenter=VCENTER_QUAD, vmax=VMAX_QUAD)

    # Apply colors to histogram bars using the same color mapping as the map
    for i, patch in enumerate(patches):
        # Use the center of each bin for color mapping
        bin_center = (bins[i] + bins[i + 1]) / 2
        color = plt.cm.viridis(norm(bin_center))
        patch.set_facecolor(color)

    # Add reference line at ideal square IPQ value (1.0)
    ax.axvline(
        x=1.0,
        color="red",
        linestyle="--",
        linewidth=2,
        label="Ideal Square (IPQ = 1.0)",
    )

    # Add statistics text box
    stats_text = f"Mean: {s2_gpd_filtered['ipq'].mean():.3f}\nStd: {s2_gpd_filtered['ipq'].std():.3f}\nMin: {s2_gpd_filtered['ipq'].min():.3f}\nMax: {s2_gpd_filtered['ipq'].max():.3f}"
    ax.text(
        0.02,
        0.98,
        stats_text,
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    # Customize the plot
    ax.set_xlabel("S2 IPQ Compactness", fontsize=14)
    ax.set_ylabel("Number of cells", fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()


def s2inspect_cli():
    """
    Command-line interface for S2 cell inspection.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-r", "--resolution", dest="resolution", type=int, default=0)
    args = parser.parse_args()  # type: ignore
    resolution = args.resolution
    print(s2inspect(resolution))


if __name__ == "__main__":
    s2stats_cli()
