"""
This module provides functions for generating statistics for ISEA4T DGGS cells.
"""

import pandas as pd
import numpy as np
import argparse
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import TwoSlopeNorm
from vgrid.utils.constants import (
    AUTHALIC_AREA,
    VMIN_TRI,
    VMAX_TRI,
    VCENTER_TRI,
    DGGS_TYPES,
)
from vgrid.generator.isea4tgrid import isea4tgrid
from vgrid.utils.io import validate_isea4t_resolution
from vgrid.utils.geometry import check_crossing_geom, characteristic_length_scale
import math

min_res = DGGS_TYPES["isea4t"]["min_res"]
max_res = DGGS_TYPES["isea4t"]["max_res"]


def isea4t_metrics(resolution, unit: str = "m"):  # length unit is km, area unit is km2
    """
    Calculate metrics for ISEA4T DGGS cells at a given resolution.

    Args:
        resolution: Resolution level (0-39)
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'

    Returns:
        tuple: (num_cells, edge_length_in_unit, cell_area_in_unit_squared)
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")

    num_cells = 20 * (4**resolution)
    avg_cell_area = AUTHALIC_AREA / num_cells  # cell area in m2
    avg_edge_len = math.sqrt((4 * avg_cell_area) / math.sqrt(3))  # edge length in km
    cls = characteristic_length_scale(avg_cell_area, unit=unit)
    # Convert to requested unit
    if unit == "km":
        avg_edge_len = avg_edge_len / (10**3)  # edge length in m
        avg_cell_area = avg_cell_area / (10**6)  # cell area in m²

    return num_cells, avg_edge_len, avg_cell_area, cls


def isea4tstats(unit: str = "m"):  # length unit is km, area unit is km2
    """
    Generate statistics for ISEA4T DGGS cells.

    Args:
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'

    Returns:
        pandas.DataFrame: DataFrame containing ISEA4T DGGS statistics with columns:
            - Resolution: Resolution level (0-39)
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
        num_cells, avg_edge_len, avg_cell_area, cls = isea4t_metrics(
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


def isea4tstats_cli():
    """
    Command-line interface for generating ISEA4T DGGS statistics.

    CLI options:
      -unit, --unit {m,km}
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-unit", "--unit", dest="unit", choices=["m", "km"], default="m"
    )
    args, _ = parser.parse_known_args()  # type: ignore

    unit = args.unit

    # Get the DataFrame
    df = isea4tstats(unit=unit)

    # Display the DataFrame
    print(df)


def isea4tinspect(resolution):
    """
    Generate comprehensive inspection data for ISEA4T DGGS cells at a given resolution.

    This function creates a detailed analysis of ISEA4T cells including area variations,
    compactness measures, and dateline crossing detection.

    Args:
        resolution: ISEA4T resolution level (0-15)

    Returns:
        geopandas.GeoDataFrame: DataFrame containing ISEA4T cell inspection data with columns:
            - isea4t: ISEA4T cell ID
            - resolution: Resolution level
            - geometry: Cell geometry
            - cell_area: Cell area in square meters
            - cell_perimeter: Cell perimeter in meters
            - crossed: Whether cell crosses the dateline
            - norm_area: Normalized area (cell_area / mean_area)
            - ipq: Isoperimetric Quotient compactness
            - zsc: Zonal Standardized Compactness
    """
    # Allow running on all platforms
    resolution = validate_isea4t_resolution(resolution)
    isea4t_gpd = isea4tgrid(resolution, output_format="gpd")
    isea4t_gpd["crossed"] = isea4t_gpd["geometry"].apply(check_crossing_geom)
    mean_area = isea4t_gpd["cell_area"].mean()
    # Calculate normalized area
    isea4t_gpd["norm_area"] = isea4t_gpd["cell_area"] / mean_area
    # Calculate IPQ compactness using the standard formula: CI = 4πA/P²
    isea4t_gpd["ipq"] = (
        4 * np.pi * isea4t_gpd["cell_area"] / (isea4t_gpd["cell_perimeter"] ** 2)
    )
    # Calculate zonal standardized compactness
    isea4t_gpd["zsc"] = (
        np.sqrt(
            4 * np.pi * isea4t_gpd["cell_area"]
            - np.power(isea4t_gpd["cell_area"], 2) / np.power(6378137, 2)
        )
        / isea4t_gpd["cell_perimeter"]
    )
    return isea4t_gpd


def isea4t_norm_area(isea4t_gpd):
    """
    Plot normalized area map for ISEA4T cells.

    This function creates a visualization showing how ISEA4T cell areas vary relative
    to the mean area across the globe, highlighting areas of distortion.

    Args:
        isea4t_gpd: GeoDataFrame from isea4tinspect function
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    vmin, vmax, vcenter = (
        isea4t_gpd["norm_area"].min(),
        isea4t_gpd["norm_area"].max(),
        1,
    )
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    isea4t_gpd = isea4t_gpd[
        ~isea4t_gpd["crossed"]
    ]  # remove cells that cross the dateline
    isea4t_gpd.to_crs("proj=moll").plot(
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
    cb_ax.set_xlabel(xlabel="ISEA4T Normalized Area", fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()


def isea4t_compactness(isea4t_gpd):
    """
    Plot IPQ compactness map for ISEA4T cells.

    This function creates a visualization showing the Isoperimetric Quotient (IPQ)
    compactness of ISEA4T cells across the globe. IPQ measures how close each cell
    is to being circular, with values closer to 0.907 indicating more regular hexagons.

    Args:
        isea4t_gpd: GeoDataFrame from isea4tinspect function
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    # vmin, vmax, vcenter = isea4t_gpd['ipq'].min(), isea4t_gpd['ipq'].max(), np.mean([isea4t_gpd['ipq'].min(), isea4t_gpd['ipq'].max()])
    norm = TwoSlopeNorm(vmin=VMIN_TRI, vcenter=VCENTER_TRI, vmax=VMAX_TRI)
    isea4t_gpd = isea4t_gpd[
        ~isea4t_gpd["crossed"]
    ]  # remove cells that cross the dateline
    isea4t_gpd.to_crs("proj=moll").plot(
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
    cb_ax.set_xlabel(xlabel="ISEA4T IPQ Compactness", fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()


def isea4t_norm_area_hist(isea4t_gpd):
    """
    Plot histogram of normalized area for ISEA4T cells.

    This function creates a histogram visualization showing the distribution
    of normalized areas for ISEA4T cells, helping to understand area variations
    and identify patterns in area distortion.

    Args:
        isea4t_gpd: GeoDataFrame from isea4tinspect function
    """
    # Filter out cells that cross the dateline
    isea4t_gpd_filtered = isea4t_gpd[~isea4t_gpd["crossed"]]

    # Create the histogram with color ramp
    fig, ax = plt.subplots(figsize=(10, 6))

    # Get histogram data
    counts, bins, patches = ax.hist(
        isea4t_gpd_filtered["norm_area"], bins=50, alpha=0.7, edgecolor="black"
    )

    # Create color ramp using the same normalization as the map function
    vmin, vmax, vcenter = (
        isea4t_gpd_filtered["norm_area"].min(),
        isea4t_gpd_filtered["norm_area"].max(),
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
    stats_text = f"Mean: {isea4t_gpd_filtered['norm_area'].mean():.3f}\nStd: {isea4t_gpd_filtered['norm_area'].std():.3f}\nMin: {isea4t_gpd_filtered['norm_area'].min():.3f}\nMax: {isea4t_gpd_filtered['norm_area'].max():.3f}"
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
    ax.set_xlabel("ISEA4T normalized area", fontsize=14)
    ax.set_ylabel("Number of cells", fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()


def isea4t_compactness_hist(isea4t_gpd):
    """
    Plot histogram of IPQ compactness for ISEA4T cells.

    This function creates a histogram visualization showing the distribution
    of Isoperimetric Quotient (IPQ) compactness values for ISEA4T cells, helping
    to understand how close cells are to being regular triangles.

    Args:
        isea4t_gpd: GeoDataFrame from isea4tinspect function
    """
    # Filter out cells that cross the dateline
    isea4t_gpd_filtered = isea4t_gpd[~isea4t_gpd["crossed"]]

    # Create the histogram with color ramp
    fig, ax = plt.subplots(figsize=(10, 6))

    # Get histogram data
    counts, bins, patches = ax.hist(
        isea4t_gpd_filtered["ipq"], bins=50, alpha=0.7, edgecolor="black"
    )

    # Create color ramp using the same normalization as the map function
    norm = TwoSlopeNorm(vmin=VMIN_TRI, vcenter=VCENTER_TRI, vmax=VMAX_TRI)

    # Apply colors to histogram bars using the same color mapping as the map
    for i, patch in enumerate(patches):
        # Use the center of each bin for color mapping
        bin_center = (bins[i] + bins[i + 1]) / 2
        color = plt.cm.viridis(norm(bin_center))
        patch.set_facecolor(color)

    # Add reference line at ideal triangle IPQ value (0.604)
    ax.axvline(
        x=0.604,
        color="red",
        linestyle="--",
        linewidth=2,
        label="Ideal Triangle (IPQ = 0.604)",
    )

    # Add statistics text box
    stats_text = f"Mean: {isea4t_gpd_filtered['ipq'].mean():.3f}\nStd: {isea4t_gpd_filtered['ipq'].std():.3f}\nMin: {isea4t_gpd_filtered['ipq'].min():.3f}\nMax: {isea4t_gpd_filtered['ipq'].max():.3f}"
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
    ax.set_xlabel("ISEA4T IPQ Compactness", fontsize=14)
    ax.set_ylabel("Number of cells", fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()


def isea4tinspect_cli():
    """
    Command-line interface for ISEA4T cell inspection.

    CLI options:
      -r, --resolution: ISEA4T resolution level (0-15)
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-r", "--resolution", dest="resolution", type=int, default=0)
    args = parser.parse_args()
    resolution = args.resolution
    print(isea4tinspect(resolution))


if __name__ == "__main__":
    isea4tstats_cli()
