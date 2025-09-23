# -*- coding: utf-8 -*-

from collections import namedtuple
from pathlib import Path
from typing import Dict, Iterable, Tuple, Optional
import io
import os
import struct

from starbound import sbon


# Override range with xrange when running Python 2.x.
try:
    range = xrange
except:
    pass


HEADER = '>8sQ'
HEADER_SIZE = struct.calcsize(HEADER)


IndexEntry = namedtuple('IndexEntry', ['offset', 'length'])


class SBAsset6(object):
    def __init__(self, stream):
        self.stream = stream

    def get(self, path):
        if not hasattr(self, 'index'):
            self.read_index()
        offset, length = self.index[path.lower()]
        self.stream.seek(offset)
        return self.stream.read(length)

    def read_header(self):
        self.stream.seek(0)
        data = struct.unpack(HEADER, self.stream.read(HEADER_SIZE))
        assert data[0] == b'SBAsset6', 'Invalid header'
        self.metadata_offset = data[1]
        # Read the metadata as well.
        self.stream.seek(self.metadata_offset)
        assert self.stream.read(5) == b'INDEX', 'Invalid index data'
        self.metadata = sbon.read_map(self.stream)
        self.file_count = sbon.read_varint(self.stream)
        # Store the offset of where the file index starts.
        self.index_offset = self.stream.tell()

    def read_index(self):
        if not hasattr(self, 'index_offset'):
            self.read_header()
        self.stream.seek(self.index_offset)
        self.index = {}
        for i in range(self.file_count):
            path = sbon.read_string(self.stream).lower()
            offset, length = struct.unpack('>QQ', self.stream.read(16))
            self.index[path] = IndexEntry(offset, length)


def _normalize_asset_path(p: str) -> str:
    # Ensure leading slash, forward slashes, and lowercase
    p = p.replace('\\', '/')
    if not p.startswith('/'):
        p = '/' + p
    return p.lower()


def write_sbasset6(stream, files: Dict[str, bytes], metadata: Optional[Dict] = None) -> None:
    """Write an SBAsset6 package to a binary stream.
    - stream: a writable, seekable binary stream (e.g., open(path, 'wb'))
    - files: mapping of asset path -> file bytes
    - metadata: optional dict to store in the INDEX metadata map
    """
    # Placeholder header; fill metadata_offset later
    stream.write(struct.pack('>8sQ', b'SBAsset6', 0))
    index: Dict[str, Tuple[int, int]] = {}
    # Write all files and record offsets/lengths
    for path in sorted(files.keys()):
        norm = _normalize_asset_path(path)
        data = files[path]
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError('files values must be bytes')
        off = stream.tell()
        stream.write(data)
        index[norm] = (off, len(data))
    # Build index (metadata) at end
    metadata_pos = stream.tell()
    stream.write(b'INDEX')
    sbon.write_map(stream, metadata or {})
    sbon.write_varint(stream, len(index))
    for path, (off, length) in index.items():
        sbon.write_string(stream, path)
        stream.write(struct.pack('>QQ', off, length))
    # Patch header with metadata offset
    stream.seek(8)
    stream.write(struct.pack('>Q', metadata_pos))


def write_sbasset6_from_dir(input_dir: str, out_path: str, *, metadata: Optional[Dict] = None) -> None:
    """Create an SBAsset6 package from a directory tree."""
    root = Path(input_dir)
    if not root.is_dir():
        raise FileNotFoundError(f'Not a directory: {input_dir}')
    # Collect files
    files: Dict[str, bytes] = {}
    for fp in root.rglob('*'):
        if fp.is_file():
            rel = str(fp.relative_to(root))
            with open(fp, 'rb') as f:
                files[rel] = f.read()
    # Write package
    with open(out_path, 'wb') as out:
        write_sbasset6(out, files, metadata=metadata)


def verify_sbasset6(path: str) -> Dict[str, object]:
    """Verify structural integrity of an SBAsset6 package.
    Returns a dict with keys: ok (bool), files (int), issues (list[str]).
    """
    issues = []
    size = os.stat(path).st_size
    with open(path, 'rb') as f:
        try:
            pkg = SBAsset6(f)
            pkg.read_index()
        except Exception as e:
            issues.append(f'Failed to read header/index: {e}')
            return {"ok": False, "files": 0, "issues": issues}
        count = 0
        for p, (off, length) in pkg.index.items():
            count += 1
            if off < 0 or length < 0:
                issues.append(f'Negative offset/length for {p}')
                continue
            end = off + length
            if end > size:
                issues.append(f'Out-of-bounds entry {p}: {off}+{length}>{size}')
        return {"ok": len(issues) == 0, "files": count, "issues": issues}
