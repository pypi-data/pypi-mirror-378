"""File system profiling utilities.

This module exposes :class:`FileProfiler` and the :class:`Filo` dataclass used
to represent file metadata collected from the filesystem.
"""

import datetime
import grp
import os
import pwd
import stat
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.table import Table

from filoma import dedup as _dedup


class FileProfiler:
    """Profiles a file for system metadata.

    The profiler collects size, permissions, owner, group, timestamps and
    optionally computes hashes or delves into extended attributes. It prefers
    :func:`os.lstat` to correctly handle symlinks.
    """

    def probe(self, path: str, compute_hash: bool = False) -> "Filo":
        """Profile a file and return a :class:`Filo` dataclass.

        Parameters
        ----------
        path : str
            Filesystem path to probe.
        compute_hash : bool
            Whether to compute SHA256 (may be slow).

        Returns
        -------
        Filo
            A dataclass containing file metadata.

        """
        path_obj = Path(path)
        full_path = str(path_obj.resolve(strict=False))

        st = path_obj.lstat()
        is_symlink = path_obj.is_symlink()
        # For non-symlinks prefer Path methods which follow symlinks by default
        is_file = path_obj.is_file() if not is_symlink else None
        is_dir = path_obj.is_dir() if not is_symlink else None
        target_is_file = None
        target_is_dir = None
        if is_symlink:
            try:
                st_target = path_obj.stat()
                target_is_file = stat.S_ISREG(st_target.st_mode)
                target_is_dir = stat.S_ISDIR(st_target.st_mode)
            except Exception:
                target_is_file = False
                target_is_dir = False

        # Current user rights
        rights = {
            "read": os.access(path, os.R_OK),
            "write": os.access(path, os.W_OK),
            "execute": os.access(path, os.X_OK),
        }

        report = {
            "path": full_path,
            "size": st.st_size,
            "mode": oct(st.st_mode),
            "owner": (pwd.getpwuid(st.st_uid).pw_name if hasattr(pwd, "getpwuid") else st.st_uid),
            "group": (grp.getgrgid(st.st_gid).gr_name if hasattr(grp, "getgrgid") else st.st_gid),
            "created": datetime.datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "accessed": datetime.datetime.fromtimestamp(st.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
            "is_symlink": is_symlink,
            "rights": rights,
        }
        # Add inode, link count and human-readable mode
        report["inode"] = getattr(st, "st_ino", None)
        report["nlink"] = getattr(st, "st_nlink", None)
        try:
            report["mode_str"] = stat.filemode(st.st_mode)
        except Exception:
            report["mode_str"] = None

        # Optional SHA256
        if compute_hash:
            report["sha256"] = self._compute_sha256(full_path)
        else:
            report["sha256"] = None

        # Try to collect extended attributes (xattrs) if available
        report["xattrs"] = self._get_xattrs(full_path)
        if is_symlink:
            report["target_is_file"] = target_is_file
            report["target_is_dir"] = target_is_dir
        else:
            report["is_file"] = is_file
            report["is_dir"] = is_dir

        # Convert to dataclass (preferred structured return)
        return Filo.from_report(report)

    def print_report(self, report: "Filo"):
        """Print a human-friendly report for a :class:`Filo` dataclass."""
        if not isinstance(report, Filo):
            raise TypeError("print_report expects a Filo dataclass")

        console = Console()
        report = report.to_dict()
        table = Table(title=f"File Profile: {report['path']}")
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="white")
        # Only show target_is_file/target_is_dir if is_symlink, otherwise show is_file/is_dir
        fields = [
            "size",
            "mode",
            "owner",
            "group",
            "created",
            "modified",
            "accessed",
            "is_symlink",
        ]
        if report.get("is_symlink"):
            fields += ["target_is_file", "target_is_dir"]
        else:
            fields += ["is_file", "is_dir"]
        for key in fields:
            table.add_row(key, str(report.get(key)))
        rights = report.get("rights", {})
        rights_str = ", ".join(f"{k}: {'✔' if v else '✗'}" for k, v in rights.items())
        table.add_row("rights", rights_str)
        console.print(table)

    def _compute_sha256(self, path: str, chunk_size: int = 1 << 20) -> str | None:
        """Compute SHA256 of a file in streaming fashion.

        Returns the hex digest or ``None`` on error.
        """
        import hashlib

        h = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def _get_xattrs(self, path: str) -> dict | None:
        """Return extended attributes as a dict if available, otherwise ``None``."""
        try:
            # xattr API differs by platform; try to import common modules
            try:
                import xattr as _xattr

                xa = {k.decode(): _xattr.get(path, k).decode(errors="ignore") for k in _xattr.listxattr(path)}
                return xa
            except Exception:
                # fallback to os.listxattr if available
                if hasattr(os, "listxattr"):
                    xa = {}
                    for k in os.listxattr(path):
                        try:
                            v = os.getxattr(path, k)
                            if isinstance(k, bytes):
                                kk = k.decode(errors="ignore")
                            else:
                                kk = k
                            xa[kk] = v.decode(errors="ignore") if isinstance(v, (bytes, bytearray)) else str(v)
                        except Exception:
                            xa[k] = None
                    return xa
        except Exception:
            pass
        return None

    # --- Dedup integration helpers ---
    def text_shingles(self, path: str, k: int = 3) -> set | None:
        """Return k-shingles for a text file (or ``None`` on error).

        Uses the same normalization/shingle function used by the :mod:`filoma.dedup` module.
        """
        try:
            with open(path, "r", encoding="utf8") as f:
                txt = f.read()
        except Exception:
            return None
        return _dedup.text_shingles(txt, k=k)

    def fingerprint_for_dedup(
        self,
        path: str,
        compute_text: bool = False,
        compute_image: bool = False,
        text_k: int = 3,
        image_hash: str = "ahash",
    ) -> dict:
        """Return a high-level fingerprint useful for duplicate detection.

        The returned dict contains keys: ``path``, ``size``, ``sha256`` and
        optionally ``text_shingles`` and ``image_hash`` depending on the flags.
        """
        report = {"path": path}
        try:
            st = os.stat(path)
            report["size"] = st.st_size
        except Exception:
            report["size"] = None

        report["sha256"] = self._compute_sha256(path)

        if compute_text:
            report["text_shingles"] = self.text_shingles(path, k=text_k)
        else:
            report["text_shingles"] = None

        if compute_image:
            try:
                if image_hash == "dhash":
                    report["image_hash"] = _dedup.dhash_image(path)
                else:
                    report["image_hash"] = _dedup.ahash_image(path)
            except Exception:
                report["image_hash"] = None
        else:
            report["image_hash"] = None

        return report


@dataclass
class Filo(Mapping):
    """Structured container for file metadata collected by :class:`FileProfiler`.

    The :attr:`path` field is a :class:`pathlib.Path` and date fields are
    :class:`datetime.datetime` objects.
    """

    path: Path
    size: Optional[int] = None
    mode: Optional[str] = None
    mode_str: Optional[str] = None
    owner: Optional[str] = None
    group: Optional[str] = None
    created: Optional[datetime.datetime] = None
    modified: Optional[datetime.datetime] = None
    accessed: Optional[datetime.datetime] = None
    is_symlink: Optional[bool] = None
    is_file: Optional[bool] = None
    is_dir: Optional[bool] = None
    target_is_file: Optional[bool] = None
    target_is_dir: Optional[bool] = None
    rights: Optional[Dict[str, bool]] = None
    inode: Optional[int] = None
    nlink: Optional[int] = None
    sha256: Optional[str] = None
    xattrs: Optional[Dict[str, Any]] = None

    @classmethod
    def from_report(cls, report: dict) -> "Filo":
        """Construct a :class:`Filo` from a plain dict report.

        The function accepts the dict shape produced by :meth:`FileProfiler.probe`.
        """
        # Convert path string to Path
        path_val = report.get("path")
        path_obj = Path(path_val) if path_val is not None else None

        def _parse_dt(v):
            if not v:
                return None
            if isinstance(v, datetime.datetime):
                return v
            try:
                return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            except Exception:
                # fallback: leave as None
                return None

        created = _parse_dt(report.get("created"))
        modified = _parse_dt(report.get("modified"))
        accessed = _parse_dt(report.get("accessed"))

        return cls(
            path=path_obj,
            size=report.get("size"),
            mode=report.get("mode"),
            mode_str=report.get("mode_str"),
            owner=report.get("owner"),
            group=report.get("group"),
            created=created,
            modified=modified,
            accessed=accessed,
            is_symlink=report.get("is_symlink"),
            is_file=report.get("is_file"),
            is_dir=report.get("is_dir"),
            target_is_file=report.get("target_is_file"),
            target_is_dir=report.get("target_is_dir"),
            rights=report.get("rights"),
            inode=report.get("inode"),
            nlink=report.get("nlink"),
            sha256=report.get("sha256"),
            xattrs=report.get("xattrs"),
        )

    def to_dict(self) -> dict:
        """Convert to a JSON-serializable dict (Path->str, datetime->isoformat)."""
        d = asdict(self)
        # path -> str
        if isinstance(self.path, Path):
            d["path"] = str(self.path)
        # datetime fields -> ISO strings
        for key in ("created", "modified", "accessed"):
            val = getattr(self, key)
            if isinstance(val, datetime.datetime):
                d[key] = val.strftime("%Y-%m-%d %H:%M:%S")
            else:
                d[key] = None
        return d

    # alias for requested API: as_dict()
    def as_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation of this Filo."""
        return self.to_dict()

    # Mapping protocol so dict-style access (report['path']) keeps working
    def _as_dict(self) -> dict:
        return self.to_dict()

    def __getitem__(self, key):
        """Mapping-style access: return the value for ``key``."""
        return self._as_dict()[key]

    def __iter__(self):
        """Iterate over mapping keys for this Filo."""
        return iter(self._as_dict())

    def __len__(self):
        """Return the number of fields in this Filo mapping."""
        return len(self._as_dict())
