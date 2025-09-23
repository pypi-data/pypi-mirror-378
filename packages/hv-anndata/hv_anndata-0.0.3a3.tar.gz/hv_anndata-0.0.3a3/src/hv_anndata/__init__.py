"""Anndata interface for holoviews."""

from __future__ import annotations

from .components import GeneSelector
from .interface import ACCESSOR, AnnDataGriddedInterface, AnnDataInterface, register
from .plotting import (
    ClusterMap,
    ClusterMapConfig,
    Dotmap,
    DotmapParams,
    ManifoldMap,
    ManifoldMapConfig,
    create_clustermap_plot,
    create_manifoldmap_plot,
    dotmap_from_manifoldmap,
    labeller,
)

ACCESSOR = ACCESSOR  # noqa: PLW0127
"""Accessor for anndata.

>>> from hv_anndata import ACCESSOR as A
>>> A.layers["counts"][:, "gene-3"]  # 1D access
>>> A[:, :]  # gridded
"""

__all__ = [
    "ACCESSOR",
    "AnnDataGriddedInterface",
    "AnnDataInterface",
    "ClusterMap",
    "ClusterMapConfig",
    "Dotmap",
    "DotmapParams",
    "GeneSelector",
    "ManifoldMap",
    "ManifoldMapConfig",
    "create_clustermap_plot",
    "create_manifoldmap_plot",
    "dotmap_from_manifoldmap",
    "labeller",
    "register",
]
