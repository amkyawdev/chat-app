"""
Compression utilities - gzip and zstd compression for batch storage.
"""
import gzip
import zstandard as zstd
from typing import bytes
from pathlib import Path
import json


def compress_gzip(data: bytes) -> bytes:
    """Compress data using gzip."""
    return gzip.compress(data, compresslevel=6)


def decompress_gzip(data: bytes) -> bytes:
    """Decompress gzip data."""
    return gzip.decompress(data)


def compress_zstd(data: bytes, level: int = 3) -> bytes:
    """Compress data using zstd (better compression ratio)."""
    cctx = zstd.ZstdCompressor(level=level)
    return cctx.compress(data)


def decompress_zstd(data: bytes) -> bytes:
    """Decompress zstd data."""
    dctx = zstd.ZstdDecompressor()
    return dctx.decompress(data)


async def compress_file(input_path: Path, output_path: Path, method: str = "zstd") -> bool:
    """
    Compress a file and save to output path.
    
    Args:
        input_path: Source file path
        output_path: Destination file path
        method: 'zstd' or 'gzip'
    """
    try:
        with open(input_path, "rb") as f:
            data = f.read()
        
        if method == "zstd":
            compressed = compress_zstd(data)
        else:
            compressed = compress_gzip(data)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(compressed)
        
        return True
    except Exception as e:
        print(f"Compression error: {e}")
        return False


async def decompress_file(input_path: Path, output_path: Path, method: str = "zstd") -> bool:
    """Decompress a file."""
    try:
        with open(input_path, "rb") as f:
            data = f.read()
        
        if method == "zstd":
            decompressed = decompress_zstd(data)
        else:
            decompressed = decompress_gzip(data)
        
        with open(output_path, "wb") as f:
            f.write(decompressed)
        
        return True
    except Exception as e:
        print(f"Decompression error: {e}")
        return False


def get_compression_ratio(original_size: int, compressed_size: int) -> float:
    """Calculate compression ratio."""
    if original_size == 0:
        return 0.0
    return round((1 - compressed_size / original_size) * 100, 2)