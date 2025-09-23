from __future__ import annotations
import mmap
import struct
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Callable, Deque
from collections import deque

from . import World


@dataclass
class ShipWorld:
    width: int
    height: int
    fg: List[int]  # flattened width*height foreground material ids (0 for empty)
    bg: List[int]  # flattened width*height background material ids (0 for empty)


def _to_u16(x: int) -> int:
    return x & 0xFFFF


def load_shipworld(path: str) -> ShipWorld:
    with open(path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        world = World(mm)
        world.read_metadata()
        width, height = world.width, world.height
        # Initialize grids
        n = width * height
        fg = [0] * n
        bg = [0] * n

        # Iterate all regions that contain tiles
        for rx, ry in world.get_all_regions_with_tiles():
            try:
                tiles = world.get_tiles(rx, ry)
            except Exception:
                continue
            # 32x32 tiles per region
            for i, tile in enumerate(tiles):
                tx = rx * 32 + (i % 32)
                ty = ry * 32 + (i // 32)
                if tx < 0 or ty < 0 or tx >= width or ty >= height:
                    continue
                idx = ty * width + tx
                bgu = _to_u16(tile.background_material)
                fgu = _to_u16(tile.foreground_material)
                # Only real materials (1..64999). Empty/Null/Structure are >= 65000
                bg[idx] = bgu if (0 < bgu < 65000) else 0
                fg[idx] = fgu if (0 < fgu < 65000) else 0

        return ShipWorld(width=width, height=height, fg=fg, bg=bg)


def extract_objects(path: str) -> List[Dict[str, Any]]:
    """Extract placeable objects from the shipworld entities.
    Returns a list of dicts compatible with structure 'objects' entries:
    { position: [x,y], name: str, direction: 'left'|'right', parameters: {}, residual: false }
    """
    objs: List[Dict[str, Any]] = []
    with open(path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        world = World(mm)
        world.read_metadata()
        # Scan BTree keys for entity regions; layer 2 is entities
        for key in world.get_all_keys():
            try:
                layer, rx, ry = struct.unpack('>BHH', key)
            except Exception:
                continue
            if layer != 2:
                continue
            try:
                ents = world.get_entities(rx, ry)
            except Exception:
                continue
            for e in ents:
                # e is VersionedJSON(name, version, data)
                d = getattr(e, 'data', {}) or {}
                # Guess object position (tile coordinates)
                pos = d.get('tilePosition') or d.get('position') or d.get('tileposition')
                if not pos or not isinstance(pos, (list, tuple)) or len(pos) < 2:
                    continue
                x, y = int(pos[0]), int(pos[1])
                # Guess object name
                oname = d.get('name') or d.get('objectName') or d.get('objectname') or d.get('configName') or d.get('object')
                if not oname or not isinstance(oname, str):
                    continue
                # Direction mapping
                direction = d.get('direction') or d.get('facingDirection')
                if isinstance(direction, (int, float)):
                    direction = 'left' if direction < 0 else 'right'
                if direction not in ('left', 'right'):
                    direction = 'left'
                parameters = d.get('parameters') or {}
                obj = {
                    'position': [x, y],
                    'name': oname,
                    'direction': direction,
                    'parameters': parameters,
                    'residual': False,
                }
                objs.append(obj)
    return objs


def load_world_grid(path: str, dungeon_id: Optional[int] = None) -> ShipWorld:
    """Load a planet/world file into a simple material grid (fg/bg), optionally
    filtering tiles to a specific dungeon_id. Metamaterials (>=65000) are
    zeroed, matching the behavior of load_shipworld.

    This uses the generic World4 reader and works for both .world and .shipworld.
    """
    with open(path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        world = World(mm)
        world.read_metadata()
        width, height = world.width, world.height
        n = width * height
        fg = [0] * n
        bg = [0] * n
        for rx, ry in world.get_all_regions_with_tiles():
            try:
                tiles = world.get_tiles(rx, ry)
            except Exception:
                continue
            for i, tile in enumerate(tiles):
                tx = rx * 32 + (i % 32)
                ty = ry * 32 + (i // 32)
                if tx < 0 or ty < 0 or tx >= width or ty >= height:
                    continue
                if dungeon_id is not None and getattr(tile, 'dungeon_id', None) != dungeon_id:
                    # Keep defaults (zeros) outside the chosen dungeon
                    continue
                idx = ty * width + tx
                bgu = _to_u16(tile.background_material)
                fgu = _to_u16(tile.foreground_material)
                bg[idx] = bgu if (0 < bgu < 65000) else 0
                fg[idx] = fgu if (0 < fgu < 65000) else 0
        return ShipWorld(width=width, height=height, fg=fg, bg=bg)
def dungeon_tile_counts(path: str) -> Dict[int, int]:
    """Return a map of dungeon_id -> tile count for a given .world file.
    Only counts ids > 0.
    """
    counts: Dict[int, int] = {}
    with open(path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        world = World(mm)
        world.read_metadata()
        width, height = world.width, world.height
        for rx, ry in world.get_all_regions_with_tiles():
            try:
                tiles = world.get_tiles(rx, ry)
            except Exception:
                continue
            for i, tile in enumerate(tiles):
                tx = rx * 32 + (i % 32)
                ty = ry * 32 + (i // 32)
                if tx < 0 or ty < 0 or tx >= width or ty >= height:
                    continue
                did = getattr(tile, 'dungeon_id', 0)
                if isinstance(did, int) and did > 0:
                    counts[did] = counts.get(did, 0) + 1
    return counts


def dungeon_bounding_boxes(path: str) -> Dict[int, Tuple[int, int, int, int]]:
    """Return a map of dungeon_id -> (min_x, min_y, max_x, max_y) for a .world file.
    Only ids > 0 are included.
    """
    boxes: Dict[int, Tuple[int, int, int, int]] = {}
    with open(path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        world = World(mm)
        world.read_metadata()
        width, height = world.width, world.height
        for rx, ry in world.get_all_regions_with_tiles():
            try:
                tiles = world.get_tiles(rx, ry)
            except Exception:
                continue
            for i, tile in enumerate(tiles):
                tx = rx * 32 + (i % 32)
                ty = ry * 32 + (i // 32)
                if tx < 0 or ty < 0 or tx >= width or ty >= height:
                    continue
                did = getattr(tile, 'dungeon_id', 0)
                if not isinstance(did, int) or did <= 0:
                    continue
                if did not in boxes:
                    boxes[did] = (tx, ty, tx, ty)
                else:
                    minx, miny, maxx, maxy = boxes[did]
                    if tx < minx:
                        minx = tx
                    if ty < miny:
                        miny = ty
                    if tx > maxx:
                        maxx = tx
                    if ty > maxy:
                        maxy = ty
                    boxes[did] = (minx, miny, maxx, maxy)
    return boxes


def compute_nonzero_bounds(sw: ShipWorld) -> Tuple[int, int, int, int]:
    min_x, min_y = sw.width, sw.height
    max_x, max_y = -1, -1
    for y in range(sw.height):
        row = y * sw.width
        for x in range(sw.width):
            if (sw.bg[row + x] > 0) or (sw.fg[row + x] > 0):
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y
    if max_x < 0:
        return (0, 0, sw.width - 1, sw.height - 1)
    return (min_x, min_y, max_x, max_y)


def crop_shipworld(sw: ShipWorld, bounds: Tuple[int, int, int, int]) -> ShipWorld:
    x0, y0, x1, y1 = bounds
    x0 = max(0, min(x0, sw.width - 1))
    y0 = max(0, min(y0, sw.height - 1))
    x1 = max(0, min(x1, sw.width - 1))
    y1 = max(0, min(y1, sw.height - 1))
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    new_w = x1 - x0 + 1
    new_h = y1 - y0 + 1
    fg = [0] * (new_w * new_h)
    bg = [0] * (new_w * new_h)
    for y in range(new_h):
        for x in range(new_w):
            src_idx = (y0 + y) * sw.width + (x0 + x)
            dst_idx = y * new_w + x
            fg[dst_idx] = sw.fg[src_idx]
            bg[dst_idx] = sw.bg[src_idx]
    return ShipWorld(width=new_w, height=new_h, fg=fg, bg=bg)


def extract_component_bounds(sw: ShipWorld, seed_x: int, seed_y: int, mode: str = "any", connectivity: str = "four") -> Tuple[Tuple[int,int,int,int], List[bool]]:
    """Flood fill from seed over tiles considered "occupied" per mode.
    mode: 'any' (fg or bg), 'fg', or 'bg'. connectivity: 'four' or 'eight'.
    Returns (bounds, mask) where mask is a flat list of booleans length width*height indicating component membership.
    """
    def occ(ix: int, iy: int) -> bool:
        idx = iy * sw.width + ix
        if mode == 'fg':
            return sw.fg[idx] > 0
        if mode == 'bg':
            return sw.bg[idx] > 0
        return (sw.fg[idx] > 0) or (sw.bg[idx] > 0)
    if seed_x < 0 or seed_y < 0 or seed_x >= sw.width or seed_y >= sw.height:
        return ((0, 0, sw.width - 1, sw.height - 1), [False] * (sw.width * sw.height))
    if not occ(seed_x, seed_y):
        return ((0, 0, sw.width - 1, sw.height - 1), [False] * (sw.width * sw.height))
    visited = [False] * (sw.width * sw.height)
    q: Deque[Tuple[int,int]] = deque()
    q.append((seed_x, seed_y))
    visited[seed_y * sw.width + seed_x] = True
    min_x = seed_x
    min_y = seed_y
    max_x = seed_x
    max_y = seed_y
    if connectivity == 'eight':
        neighbors = ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1))
    else:
        neighbors = ((1,0),(-1,0),(0,1),(0,-1))
    while q:
        x, y = q.popleft()
        if x < min_x: min_x = x
        if y < min_y: min_y = y
        if x > max_x: max_x = x
        if y > max_y: max_y = y
        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= sw.width or ny >= sw.height:
                continue
            nidx = ny * sw.width + nx
            if visited[nidx]:
                continue
            if occ(nx, ny):
                visited[nidx] = True
                q.append((nx, ny))
    return ((min_x, min_y, max_x, max_y), visited)


def apply_mask(sw: ShipWorld, mask: List[bool]) -> ShipWorld:
    """Return a copy of sw where tiles not in mask are zeroed (fg=bg=0)."""
    assert len(mask) == sw.width * sw.height
    fg = sw.fg[:]
    bg = sw.bg[:]
    for idx, keep in enumerate(mask):
        if not keep:
            fg[idx] = 0
            bg[idx] = 0
    return ShipWorld(width=sw.width, height=sw.height, fg=fg, bg=bg)
