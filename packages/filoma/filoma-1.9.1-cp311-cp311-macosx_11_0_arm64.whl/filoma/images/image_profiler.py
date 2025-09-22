"""Utilities for analyzing image data and computing image reports.

This module provides an :class:`ImageReport` dataclass used to store
analysis results and the :class:`ImageProfiler` helper for in-memory
arrays.
"""

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Optional, Tuple

import numpy as np

from filoma import dedup as _dedup


@dataclass
class ImageReport(Mapping):
    """Structured container for image analysis results.

    This dataclass implements the mapping protocol for convenient
    serialization and template-friendly access.
    """

    path: Optional[str] = None
    file_type: Optional[str] = None
    shape: Optional[Tuple[int, ...]] = None
    dtype: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None
    mean: Optional[float] = None
    nans: int = 0
    infs: int = 0
    unique: int = 0
    status: Optional[str] = None

    def to_dict(self) -> dict:
        """Return a JSON-serializable dict representation of the report."""
        d = asdict(self)
        # Ensure shape is a plain tuple (JSON-serializable)
        if isinstance(self.shape, (list, tuple)):
            d["shape"] = tuple(self.shape)
        return d

    def as_dict(self) -> dict:
        """Alias for :meth:`to_dict`."""
        return self.to_dict()

    # Mapping protocol for dict access
    def _as_dict(self) -> dict:
        return self.to_dict()

    def __getitem__(self, key):
        """Get a value by key from the internal mapping."""
        return self._as_dict()[key]

    def __iter__(self):
        """Iterate over mapping keys."""
        return iter(self._as_dict())

    def __len__(self):
        """Return the number of items in the mapping."""
        return len(self._as_dict())


class ImageProfiler:
    """Provides common analysis methods for image data loaded as numpy arrays.

    Returns an :class:`ImageReport` dataclass for consistency with the rest
    of the API.
    """

    def probe(self, arr: np.ndarray) -> ImageReport:
        """Analyze the given NumPy array and return an :class:`ImageReport`.

        This computes simple statistics (min/max/mean), counts of NaNs and
        infinities, and the number of unique values.
        """
        report = ImageReport(
            shape=tuple(arr.shape) if hasattr(arr, "shape") else None,
            dtype=str(arr.dtype) if hasattr(arr, "dtype") else None,
            min=float(np.nanmin(arr)) if arr.size > 0 else None,
            max=float(np.nanmax(arr)) if arr.size > 0 else None,
            mean=float(np.nanmean(arr)) if arr.size > 0 else None,
            nans=int(np.isnan(arr).sum()),
            infs=int(np.isinf(arr).sum()),
            unique=int(np.unique(arr).size) if arr.size > 0 else 0,
        )
        return report

    # --- Dedup integration helpers ---
    def compute_ahash(self, path: str, hash_size: int = 8) -> str:
        """Compute an aHash for an image file via :mod:`filoma.dedup`.

        Requires Pillow to be installed.
        """
        return _dedup.ahash_image(path, hash_size=hash_size)

    def compute_dhash(self, path: str, hash_size: int = 8) -> str:
        """Compute a dHash for an image file via :mod:`filoma.dedup`.

        Requires Pillow to be installed.
        """
        return _dedup.dhash_image(path, hash_size=hash_size)
