import json
import pathlib
import uuid
import zipfile
import struct
import polars as pl
import functools
from pathlib import Path
from tacotoolbox.taco.datamodel import Taco
from tacotoolbox.tortilla.datamodel import Tortilla
from contextlib import contextmanager


def requires_tacotiff(func):
    """Simple decorator to ensure tacotiff is available."""
    _checked = False
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal _checked
        if not _checked:
            try:
                import tacotiff
            except ImportError:
                raise ImportError("tacotiff required. Install: pip install tacotiff")
            _checked = True
        return func(*args, **kwargs)
    return wrapper


class TacoCreationError(Exception):
    """Custom exception for TACO creation errors."""
    pass


def parse_size(size_str: str) -> int:
    """Parse human-readable size to bytes."""
    units = {
        'TB': 1024**4,
        'GB': 1024**3,
        'MB': 1024**2, 
        'KB': 1024,
        'B': 1
    }
    
    size_str = size_str.upper().strip()
    
    # Check units in descending order by length to avoid "GB" matching "B" first
    for unit in sorted(units.keys(), key=len, reverse=True):
        if size_str.endswith(unit):
            number_part = size_str[:-len(unit)].strip()
            if not number_part:
                raise ValueError(f"Invalid size format: {size_str}")
            return int(float(number_part) * units[unit])
    
    raise ValueError(f"Invalid size format: {size_str}")


def calculate_sample_size(sample) -> int:
    """Calculate total size of a sample (recursive for TORTILLA types)."""
    if sample.type == "TORTILLA":
        # Recursive case: sum all nested samples
        return sum(calculate_sample_size(s) for s in sample.path.samples)
    else:
        # Base case: file size
        return sample.path.stat().st_size


def group_samples_by_size(samples: list, split_size: int) -> list[list]:
    """Group consecutive samples into chunks that don't exceed split_size."""
    if not samples:
        return []
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sample in samples:
        sample_size = calculate_sample_size(sample)
        
        # If single sample exceeds limit, put it in its own chunk
        if sample_size > split_size:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                current_size = 0
            chunks.append([sample])
            continue
        
        # If adding this sample would exceed limit, start new chunk
        if current_size + sample_size > split_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = [sample]
            current_size = sample_size
        else:
            current_chunk.append(sample)
            current_size += sample_size
    
    # Add final chunk if not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


class MetadataProcessor:
    """Handles metadata processing for TACO files."""
    
    def __init__(self, taco: Taco, zip_path: pathlib.Path, quiet: bool = False, remove_path_column: bool = True):
        self.taco = taco
        self.zip_path = zip_path
        self.quiet = quiet
        self.remove_path_column = remove_path_column
        self.original_depth = taco.tortilla._current_depth
    
    def add_internal_positions(self) -> list[pl.DataFrame]:
        """Add internal position information to metadata tables."""
        file_positions = self._get_zip_data_offsets()
        lookup = self._create_position_lookup(file_positions)
        
        results = []
        
        # FIX: Only iterate through actual depth levels, not hardcoded 5
        for depth in range(self.original_depth + 1):
            self.taco.tortilla._current_depth = depth
            df = self.taco.tortilla.export_metadata(deep=depth)
            
            if df is not None and len(df) > 0:
                processed_df = self._process_metadata_depth(df, lookup)
                # Remove columns that are completely null
                processed_df = self._remove_null_columns(processed_df)
                results.append(processed_df)
        
        self.taco.tortilla._current_depth = self.original_depth
        return results
    
    def _get_zip_data_offsets(self) -> pl.DataFrame:
        """Get actual data offsets for GDAL /vsisubfile/ usage."""
        files_info = []
        
        with zipfile.ZipFile(self.zip_path, 'r') as zip_file:
            with open(self.zip_path, 'rb') as f:
                for info in zip_file.infolist():
                    if info.filename == "TACO_GHOST" or info.filename.endswith('/'):
                        continue
                    
                    # Seek to local file header
                    f.seek(info.header_offset)
                    header = f.read(30)
                    
                    if len(header) < 30:
                        continue
                    
                    # Validate local file header signature
                    signature = struct.unpack('<I', header[0:4])[0]
                    if signature != 0x04034b50:
                        continue
                    
                    filename_len = struct.unpack('<H', header[26:28])[0]
                    extra_len = struct.unpack('<H', header[28:30])[0]
                    
                    files_info.append({
                        'id': info.filename,
                        'internal:offset': info.header_offset + 30 + filename_len + extra_len,
                        'internal:size': info.compress_size,
                    })
        
        return pl.DataFrame(files_info)
    
    def _create_position_lookup(self, file_positions: pl.DataFrame) -> dict[tuple[int, str], tuple[int, int]]:
        """Create lookup table for position information."""
        parent_dirs = []
        
        # Get unique parent directories
        for row in file_positions.iter_rows(named=True):
            path_parts = row['id'].split('/')
            if len(path_parts) >= 2:
                parent_dir = path_parts[-2]
                if parent_dir not in parent_dirs:
                    parent_dirs.append(parent_dir)
        
        # Create lookup: (parent_position, sample_id) -> (offset, size)
        lookup = {}
        for row in file_positions.iter_rows(named=True):
            path_parts = row['id'].split('/')
            if len(path_parts) >= 2:
                parent_dir = path_parts[-2]
                sample_id = path_parts[-1].split('.')[0]
                parent_position = parent_dirs.index(parent_dir)
                
                lookup[(parent_position, sample_id)] = (row['internal:offset'], row['internal:size'])
        
        return lookup
    
    def _process_metadata_depth(self, df: pl.DataFrame, lookup: dict) -> pl.DataFrame:
        """Process metadata for a specific depth level using DataFrame operations."""
        
        # Add new columns with default values first
        df = df.with_columns([
            pl.lit(None, dtype=pl.Int64).alias('internal:offset'),
            pl.lit(None, dtype=pl.Int64).alias('internal:size'),
            pl.lit(None, dtype=pl.Binary).alias('internal:header')
        ])
        
        # Process each row for non-TORTILLA types
        rows_data = []
        for row in df.iter_rows(named=True):
            row_dict = dict(row)
            
            if row_dict['type'] != 'TORTILLA':
                sample_id = row_dict['id']
                position = row_dict.get('internal:position', 0)
                
                key = (position, sample_id)
                if key in lookup:
                    row_dict['internal:offset'], row_dict['internal:size'] = lookup[key]
                
                # Add TACOTIFF header if needed
                if row_dict['type'] == 'TACOTIFF' and 'path' in row_dict:
                    row_dict['internal:header'] = self._get_tacotiff_header(row_dict['path'])
            
            rows_data.append(row_dict)
        
        # Recreate DataFrame with updated data
        result_df = pl.DataFrame(rows_data, schema=df.schema)
        
        # Remove path column if configured to do so
        if self.remove_path_column and 'path' in result_df.columns:
            result_df = result_df.drop('path')
        
        return result_df
    
    def _remove_null_columns(self, df: pl.DataFrame) -> pl.DataFrame:
        """Remove columns that are completely null or empty."""
        cols_to_keep = []
        for col in df.columns:
            # First check if column has any non-null values
            if not df[col].is_null().all():
                # For string columns, also check for empty strings and "None"
                if df[col].dtype == pl.Utf8:
                    non_empty_count = df.filter(
                        (pl.col(col).is_not_null()) & 
                        (pl.col(col) != "") & 
                        (pl.col(col) != "None")
                    ).height
                    
                    if non_empty_count > 0:
                        cols_to_keep.append(col)
                else:
                    # For non-string columns, just check if not all null
                    cols_to_keep.append(col)
        
        return df.select(cols_to_keep) if cols_to_keep else df.select([df.columns[0]])  # Keep at least one column
    
    @requires_tacotiff
    def _get_tacotiff_header(self, path: str) -> bytes | None:
        """Get TACOTIFF header information as binary."""
        import tacotiff  # Safe after decorator check
        
        try:
            header_data = tacotiff.metadata_from_tiff(path)
            if header_data is None:
                return None
            # FIX: Handle both bytes and string returns from tacotiff.metadata_from_tiff
            return header_data if isinstance(header_data, bytes) else header_data.encode('utf-8')
        except Exception as e:
            if not self.quiet:
                print(f"Warning: Could not extract header for {path}: {e}")
            return None


class FileExtractor:
    """Handles file extraction for TACO creation."""
    
    @staticmethod
    def extract_files_recursive(
        samples, 
        data_root: str = "DATA/", 
        src_files: list[str] | None = None, 
        arc_files: list[str] | None = None, 
        path_prefix: str = ""  # Changed from parent_id to path_prefix
    ) -> tuple[list[str], list[str]]:
        """Recursively extract source and archive file paths."""
        if src_files is None:
            src_files = []
        if arc_files is None:
            arc_files = []
        
        for sample in samples:
            if sample.type == "TORTILLA":
                # Build the new path prefix by appending current sample id
                new_path_prefix = f"{path_prefix}{sample.id}/" if path_prefix else f"{sample.id}/"
                
                FileExtractor.extract_files_recursive(
                    sample.path.samples, 
                    data_root, 
                    src_files, 
                    arc_files,
                    path_prefix=new_path_prefix  # Pass the accumulated path
                )
            else:
                src_files.append(str(sample.path))
                
                file_suffix = Path(sample.path).suffix
                # Use the full accumulated path prefix
                arc_files.append(f"{data_root}{path_prefix}{sample.id}{file_suffix}")
        
        return src_files, arc_files


class MetadataManager:
    """Manages metadata parquet file operations."""
    
    @staticmethod
    def get_parquet_offsets(zip_path: pathlib.Path) -> tuple[list[int], list[int]]:
        """Return offsets and lengths for metadata parquet files."""
        offsets = []
        lengths = []
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            parquet_files = [
                info for info in zf.infolist() 
                if info.filename.startswith('METADATA/') and info.filename.endswith('.parquet')
            ]
            parquet_files.sort(key=lambda x: x.filename)
            
            for info in parquet_files:
                offsets.append(info.header_offset + len(info.extra) + len(info.filename) + 30)
                lengths.append(info.file_size)
        
        return offsets, lengths
    
    @staticmethod
    @contextmanager
    def temporary_parquet_files(metadata_tables: list[pl.DataFrame], output_path: pathlib.Path):
        """Context manager for temporary parquet files."""
        temp_files = []
        try:
            for df in metadata_tables:
                temp_file = output_path.parent / f"{uuid.uuid4()}.parquet"
                df.write_parquet(temp_file)
                temp_files.append(temp_file)
            
            yield temp_files
            
        finally:
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                except Exception:
                    pass  # Ignore cleanup errors

    @staticmethod
    @contextmanager
    def temporary_json_file(data: dict, output_path: pathlib.Path):
        """Context manager for temporary JSON file."""
        temp_file = output_path.parent / f"{uuid.uuid4()}.json"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            yield temp_file
        finally:
            try:
                temp_file.unlink()
            except Exception:
                pass  # Ignore cleanup error


def _create_single_taco(
    taco: Taco,
    output_path: pathlib.Path, 
    quiet: bool,
    remove_path_column: bool
) -> pathlib.Path:
    """Create a single TACO file with the original logic."""
    try:
        # 1. Extract file paths
        src_files, arc_files = FileExtractor.extract_files_recursive(
            samples=taco.tortilla.samples
        )
        
        # 2. Create the TACO ZIP file
        import tacozip
        tacozip.create(
            zip_path=str(output_path),
            src_files=src_files,
            arc_files=arc_files,
            entries=[(0, 0) for _ in range(taco.tortilla._current_depth + 1)]
        )
        
        # 3. Process metadata with internal positions
        metadata_processor = MetadataProcessor(taco, output_path, quiet, remove_path_column)
        metadata_tables = metadata_processor.add_internal_positions()
        
        # 4. Add metadata parquet files
        with MetadataManager.temporary_parquet_files(metadata_tables, output_path) as temp_files:
            tacozip.append_files(
                zip_path=str(output_path),
                entries=[(str(temp_file), f"METADATA/level{i}.parquet") 
                        for i, temp_file in enumerate(temp_files)]
            )
        
        # 5. Update ghost with metadata parquet offsets
        offsets, lengths = MetadataManager.get_parquet_offsets(output_path)
        tacozip.update_header(
            zip_path=str(output_path),
            entries=list(zip(offsets, lengths))
        )

        # 6. Aggregate the TACO Collection metadata
        taco_json = taco.model_dump()
        taco_json.pop('tortilla', None)
        with MetadataManager.temporary_json_file(taco_json, output_path) as temp_json:
            tacozip.append_files(
                zip_path=str(output_path),
                entries=[(str(temp_json), "COLLECTION.json")]
            )
        
        if not quiet:
            print(f"TACO file created successfully: {output_path}")
        
        return output_path
        
    except Exception as e:
        raise TacoCreationError(f"Failed to create TACO file: {e}") from e


def create(
    taco: Taco,    
    output: str | pathlib.Path,
    split_size: str | None = None,
    quiet: bool = False,
    remove_path_column: bool = True,
) -> list[pathlib.Path]:
    """
    Create TACO file(s) with optional size-based splitting.

    A TACO is a ZIP64 container optimized for storing large datasets 
    that require partial reading and random access.

    Args:
        taco: A TACO object containing the collection metadata and samples
        output: The path where the TACO file(s) will be saved
        split_size: Optional size limit for splitting (e.g., "5GB", "100MB", "2TB")
        quiet: Whether to suppress output messages
        remove_path_column: Whether to remove path column from metadata

    Returns:
        list[pathlib.Path]: List of created TACO file paths

    Raises:
        TacoCreationError: If TACO creation fails
    """
    output_path = pathlib.Path(output)
    
    # If no split_size, use original single-file logic
    if split_size is None:
        result = _create_single_taco(taco, output_path, quiet, remove_path_column)
        return [result]
    
    try:
        # Parse split size and group samples
        max_size = parse_size(split_size)
        sample_chunks = group_samples_by_size(taco.tortilla.samples, max_size)
        
        if len(sample_chunks) == 1:
            # No splitting needed
            result = _create_single_taco(taco, output_path, quiet, remove_path_column)
            return [result]
        
        # Create multiple TACO files
        created_files = []
        base_name = output_path.stem
        extension = output_path.suffix
        parent_dir = output_path.parent
        
        for i, chunk_samples in enumerate(sample_chunks, 1):
            # Create new Tortilla with chunk samples
            chunk_tortilla = Tortilla(samples=chunk_samples)
            
            # Create new Taco with same metadata but new tortilla
            chunk_taco_data = taco.model_dump()
            chunk_taco_data['tortilla'] = chunk_tortilla
            chunk_taco = Taco(**chunk_taco_data)
            
            # Generate chunk filename
            chunk_filename = f"{base_name}_part{i:03d}{extension}"
            chunk_path = parent_dir / chunk_filename
            
            # Create chunk TACO file
            result = _create_single_taco(chunk_taco, chunk_path, quiet, remove_path_column)
            created_files.append(result)
        
        if not quiet:
            print(f"Created {len(created_files)} TACO chunks with target size {split_size}")
        
        return created_files
        
    except Exception as e:
        raise TacoCreationError(f"Failed to create TACO file: {e}") from e