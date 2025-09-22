# Cookbook

Practical, copy‑paste recipes organized by what you want to accomplish.

## I want to search and discover files...

### Find specific file types quickly
Use `FdFinder` for powerful pattern-based file discovery:

```python
from filoma.directories import FdFinder

finder = FdFinder()

# Find all Python files
python_files = finder.find_files(pattern=r"\.py$")

# Find files by multiple extensions
code_files = finder.find_by_extension(['py', 'rs', 'js'])

# Find files using a glob pattern
config_files = finder.find_files(pattern="*.{json,yaml}", use_glob=True)

print(f"Found {len(python_files)} Python files.")
```

### Profile directories and files
Get comprehensive analysis of directory contents:

```python
from filoma import probe_to_df
from filoma.directories import DirectoryProfiler

# Quick overview with DataFrame output
dfw = probe_to_df('.')

# Detailed profiling with custom configuration
from filoma.directories import DirectoryProfilerConfig
config = DirectoryProfilerConfig(fast_path_only=True, build_dataframe=True)
analysis = DirectoryProfiler(config).probe('.')
paths_df = analysis.to_df().df
```

### Skip metadata collection for speed
When you only need file paths without size/time information:

```python
from filoma import probe_to_df
from filoma.dataframe import DataFrame

# Fast path discovery without metadata
dfw = probe_to_df('.', enrich=False)

# Add metadata later if needed
base = DataFrame(dfw.df)
with_stats = base.add_file_stats_cols()  # adds size, times, owner, etc.
```

## I want to explore and analyze my data...

### Find the largest files
```python
from filoma import probe_to_df

dfw = probe_to_df('.')
largest = dfw.df.select(['path','size_bytes']).sort('size_bytes', descending=True).head(10)
print(largest)
```

### Analyze file extension distribution
```python
from filoma import probe_to_df

dfw = probe_to_df('.')
by_ext = dfw.df.groupby('suffix').count().sort('count', descending=True).head(15)
print(by_ext)
```

### Count files per directory
```python
from filoma import probe_to_df

dfw = probe_to_df('.')
# Add parent column and count files per directory
counts = dfw.df.with_columns(
    dfw.df['path'].str.split('/').list.slice(-2,1).alias('parent')
).groupby('parent').count().sort('count', descending=True)
print(counts)
```

### Filter files by criteria
```python
from filoma import probe_to_df

dfw = probe_to_df('.')

# Filter by file extension
python_files = dfw.df.filter(dfw.df['path'].str.ends_with('.py'))

# Filter by size (files larger than 5MB)
large_files = dfw.df.filter(dfw.df['size_bytes'] > 5_000_000)

# Filter by modification time (recently modified)
from datetime import datetime, timedelta
cutoff = datetime.utcnow() - timedelta(hours=24)
recent = dfw.df.filter(dfw.df['modified_time'] > cutoff.isoformat())
```

### Analyze directory depth patterns
```python
from filoma import probe_to_df

dfw = probe_to_df('.')
depth_stats = dfw.df.groupby('depth').count().sort('depth')
print(depth_stats)
```

### Profile image files
```python
from filoma import probe_to_df, probe_image

dfw = probe_to_df('.')
images = dfw.df.filter(dfw.df['suffix'].is_in(['.png','.tif','.npy']))
large_images = images.filter(images['size_bytes'] > 5_000_000)

# Get detailed image information
reports = [probe_image(p) for p in large_images['path'].to_list()]
```

## I want to split my data for machine learning...

### Basic train/validation/test split
```python
from filoma import probe_to_df, ml

dfw = probe_to_df('.')
train, val, test = ml.split_data(dfw, train_val_test=(70,15,15), seed=42)
```

### Split by existing folder structure
If your data is already organized in folders like `training/`, `validation/`, `testing/`:

```python
from filoma import probe_to_df, ml

dfw = probe_to_df('.')

# Map custom folder names to splits
train, val, test = ml.split_data(
    dfw,
    feature='path_parts',
    path_parts=(-2,),  # Parent folder name
    split_mapping={
        'training': 'train',
        'validation': 'val', 
        'testing': 'test'
    }
)

# If folders are already named train/val/test:
train, val, test = ml.split_data(
    dfw,
    feature='path_parts', 
    path_parts=(-2,),
    split_mapping={
        'train': 'train',
        'val': 'val',
        'test': 'test'
    }
)
```

### Split by specific path components
Split based on any part of the file path (e.g., user folders, categories):

```python
from filoma import probe_to_df, ml
from filoma.dataframe import DataFrame

# Example paths: /data/user1/files/image.jpg, /data/user2/files/image.jpg
dfw = probe_to_df('.')

# Method 1: Direct path component splitting
train, val, test = ml.split_data(
    dfw, 
    feature='path_parts', 
    path_parts=(-3,),  # Adjust index for your path structure
    train_val_test=(70,15,15), 
    seed=42
)

# Method 2: Inspect path structure first
df = DataFrame(dfw.df)
df_with_parts = df.add_filename_features(include_all_parts=True)
print(df_with_parts.head())  # Check path_part0, path_part1, etc.
train, val, test = df_with_parts.split_data(feature='path_part2')
```

### Split by filename patterns
Extract features from filename tokens (e.g., `subject_condition_trial.txt`):

```python
from filoma import probe_to_df
from filoma.dataframe import DataFrame

dfw = probe_to_df('.')
df = DataFrame(dfw.df)

# Extract filename tokens separated by underscores
df_with_features = df.add_filename_features(sep='_')

# Split by any extracted token
train, val, test = df_with_features.split_data(feature=('feat1',))  # First token
train, val, test = df_with_features.split_data(feature=('feat2',))  # Second token

# Or use split_mapping with filename tokens
train, val, test = df_with_features.split_data(
    feature=('feat2',),
    split_mapping={'train': 'train', 'val': 'val', 'test': 'test'}
)
```

### Split by file properties
```python
from filoma import probe_to_df, ml

dfw = probe_to_df('.')

# Split by file extension
train, val, test = ml.split_data(dfw, feature='suffix', seed=42)

# Split by parent directory
train, val, test = ml.split_data(dfw, feature='path_parts', path_parts=(-2,), seed=42)

# Split by multiple path components
train, val, test = ml.split_data(
    dfw, 
    feature='path_parts', 
    path_parts=(-3, -2),  # Combine multiple path parts
    seed=42
)
```

## I want to find and remove duplicates...

### Simple duplicate detection by size and hash
```python
from filoma import probe_to_df, probe_file
import collections

dfw = probe_to_df('.')

# Find potential duplicates by size
size_groups = dfw.df.groupby('size_bytes').count().filter(pl.col('count') > 1)
candidates = dfw.df.filter(dfw.df['size_bytes'].is_in(size_groups['size_bytes'].to_list()))

# Verify with hash comparison
hash_map = collections.defaultdict(list)
for path in candidates['path'].to_list():
    filo = probe_file(path, compute_hash=True)
    hash_map[filo.sha256].append(path)

duplicates = [v for v in hash_map.values() if len(v) > 1]
print(f"Found {len(duplicates)} groups of duplicates")
```

### Compute hashes for specific files
```python
from filoma import probe_file

paths = ['README.md', 'pyproject.toml']
rows = []
for p in paths:
    filo = probe_file(p, compute_hash=True)
    rows.append({'path': filo.path, 'sha256': filo.sha256})

print(rows)
```

## I want to export and integrate with other tools...

### Export data for downstream processing
```python
from filoma import probe_to_df

dfw = probe_to_df('.')

# Save as different formats
dfw.save_parquet('files.parquet')
dfw.save_csv('files.csv')

# Convert to pandas for other libraries
pandas_df = dfw.to_pandas()

# Convert to raw polars for advanced operations
polars_df = dfw.df
```

### Work with the raw polars DataFrame
```python
from filoma import probe_to_df
import polars as pl

dfw = probe_to_df('.')

# Access the underlying polars DataFrame for advanced operations
raw_df = dfw.df

# Complex polars operations
result = raw_df.lazy().filter(
    (pl.col('size_bytes') > 1000000) & 
    (pl.col('path').str.contains(r'\.py$'))
).group_by('depth').agg([
    pl.col('size_bytes').sum().alias('total_size'),
    pl.col('path').count().alias('file_count')
]).collect()
```

---
Missing a recipe? [Open an issue](https://github.com/kalfasyan/filoma/issues) to request it!
