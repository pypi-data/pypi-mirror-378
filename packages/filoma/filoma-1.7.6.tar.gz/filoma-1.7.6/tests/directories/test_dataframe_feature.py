#!/usr/bin/env python3
"""
Test script to demonstrate the DataFrame feature in DirectoryProfiler.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import filoma
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from filoma import DataFrame
from filoma.directories.directory_profiler import DirectoryProfiler


def test_dataframe_functionality():
    """Test the new DataFrame functionality."""
    print("Testing DataFrame functionality in DirectoryProfiler...")

    # Test with DataFrame enabled
    from filoma.directories import DirectoryProfilerConfig

    cfg = DirectoryProfilerConfig(search_backend="auto", build_dataframe=True, show_progress=False)
    profiler = DirectoryProfiler(cfg)

    print(f"DataFrame enabled: {profiler.is_dataframe_enabled()}")
    print(f"Implementation info: {profiler.get_implementation_info()}")

    # Analyze a small temporary directory to keep the test fast and deterministic
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        current_dir = Path(td)
        # create a couple of files and subdirs
        (current_dir / "a").mkdir()
        (current_dir / "a" / "f1.txt").write_text("x")
        (current_dir / "b").mkdir()
        (current_dir / "b" / "f2.py").write_text("print(1)")

        analysis = profiler.probe(str(current_dir), max_depth=1)

        # Print basic summary
        profiler.print_summary(analysis)

        # Get the DataFrame
        df = profiler.get_dataframe(analysis)
        if df is not None:
            print(f"\n📊 DataFrame created with {len(df)} rows")
            print("First 5 rows:")
            print(df.head())

            # Test DataFrame methods
            print("\n🔧 Testing DataFrame methods...")

            # Add path components
            df_with_components = df.add_path_components()
            print(f"Added path components. Columns: {df_with_components.df.columns}")
            print(df_with_components.head())

            # Group by extension
            print("\n📁 Files by extension:")
            ext_counts = df.group_by_extension()
            print(ext_counts)

            # Filter Python files
            py_files = df.filter_by_extension([".py", ".pyc"])
            print(f"\n🐍 Found {len(py_files)} Python files")
            if len(py_files) > 0:
                print(py_files.head())

            # Add depth information
            df_with_depth = df.add_depth_col(current_dir)
            print("\n📏 Added depth column")
            print(df_with_depth.head())

        else:
            print("❌ No DataFrame was created")

    # exceptions should propagate to fail the test


def test_standalone_dataframe():
    """Test the standalone DataFrame class."""
    print("\n" + "=" * 50)
    print("Testing standalone DataFrame class...")

    # Create a DataFrame with some test paths
    test_paths = [
        "/home/user/documents/file1.txt",
        "/home/user/documents/file2.py",
        "/home/user/projects/main.py",
        "/home/user/projects/utils.py",
        "/home/user/pictures/photo.jpg",
    ]

    df = DataFrame(test_paths)
    print(f"Created DataFrame with {len(df)} rows")
    print(df.head())

    # Test methods
    print("\n🔧 Testing DataFrame methods...")

    # Add components
    df_with_components = df.add_path_components()
    print("With path components:")
    print(df_with_components.df)

    # Filter by extension
    py_files = df.filter_by_extension(".py")
    print(f"\nPython files ({len(py_files)}):")
    print(py_files.df)

    # Group by extension
    print("\nGrouped by extension:")
    print(df.group_by_extension())


if __name__ == "__main__":
    test_dataframe_functionality()
    test_standalone_dataframe()
