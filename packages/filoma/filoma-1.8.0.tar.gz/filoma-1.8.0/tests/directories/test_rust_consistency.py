import os
import tempfile
from pathlib import Path

import pytest

from filoma.directories import DirectoryProfiler, DirectoryProfilerConfig

# Skip these filesystem-heavy tests on CI where external tools like `fd` may be missing
CI = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"
pytestmark = pytest.mark.skipif(CI, reason="Skip on CI where fd may be unavailable")


def test_rust_python_consistency():
    """Test that Rust and Python implementations produce consistent results."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create test structure
        (tmp_path / "level1" / "level2" / "level3").mkdir(parents=True)
        (tmp_path / "level1" / "file1.txt").write_text("test")
        (tmp_path / "level1" / "level2" / "file2.txt").write_text("test")
        (tmp_path / "level1" / "level2" / "level3" / "file3.txt").write_text("test")

        # Test both implementations
        python_profiler = DirectoryProfiler(DirectoryProfilerConfig(use_rust=False))
        rust_profiler = DirectoryProfiler(DirectoryProfilerConfig(use_rust=True))

        # Test without max_depth - should find all files and folders
        result_py = python_profiler.probe(str(tmp_path))
        result_rust = rust_profiler.probe(str(tmp_path))

        assert result_py["summary"]["total_files"] == 3
        assert result_rust["summary"]["total_files"] == 3
        assert result_py["summary"]["total_folders"] == 4
        assert result_rust["summary"]["total_folders"] == 4

        # Test with max_depth=2
        result_py_depth = python_profiler.probe(str(tmp_path), max_depth=2)
        result_rust_depth = rust_profiler.probe(str(tmp_path), max_depth=2)

        assert result_py_depth["summary"]["total_files"] == 2
        assert result_rust_depth["summary"]["total_files"] == 2
        assert result_py_depth["summary"]["total_folders"] == 3
        assert result_rust_depth["summary"]["total_folders"] == 3


def test_empty_directory_consistency():
    """Test consistency with empty directories."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create structure with empty directories
        (tmp_path / "empty1").mkdir()
        (tmp_path / "non_empty").mkdir()
        (tmp_path / "non_empty" / "file.txt").write_text("test")
        (tmp_path / "non_empty" / "empty2").mkdir()

        python_profiler = DirectoryProfiler(DirectoryProfilerConfig(use_rust=False))
        rust_profiler = DirectoryProfiler(DirectoryProfilerConfig(use_rust=True))

        result_py = python_profiler.probe(str(tmp_path))
        result_rust = rust_profiler.probe(str(tmp_path))

        assert (
            result_py["summary"]["total_files"]
            == result_rust["summary"]["total_files"]
            == 1
        )
        assert (
            result_py["summary"]["total_folders"]
            == result_rust["summary"]["total_folders"]
            == 4
        )


def test_single_file_consistency():
    """Test consistency with just a single file."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        (tmp_path / "single_file.txt").write_text("test")

        python_profiler = DirectoryProfiler(DirectoryProfilerConfig(use_rust=False))
        rust_profiler = DirectoryProfiler(DirectoryProfilerConfig(use_rust=True))

        result_py = python_profiler.probe(str(tmp_path))
        result_rust = rust_profiler.probe(str(tmp_path))

        assert (
            result_py["summary"]["total_files"]
            == result_rust["summary"]["total_files"]
            == 1
        )
        assert (
            result_py["summary"]["total_folders"]
            == result_rust["summary"]["total_folders"]
            == 1
        )
