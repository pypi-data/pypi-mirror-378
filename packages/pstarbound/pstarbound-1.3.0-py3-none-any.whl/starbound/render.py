from __future__ import annotations
from typing import Optional, Dict, List
import os
import io
from PIL import Image, ImageDraw
from .sbasset6 import SBAsset6
from .shipworld import load_shipworld, ShipWorld
from .materials import MaterialRegistry


def render_shipworld(shipworld_path: str, assets_dir: Optional[str], out_png: str, tile_size: int = 8, grid: Optional[ShipWorld] = None, textured: bool = False) -> None:
    sw = grid if grid is not None else load_shipworld(shipworld_path)
    reg = MaterialRegistry(assets_dir)

    # Create canvas; y=0 at bottom; we’ll flip vertically for human-friendly display
    width_px = sw.width * tile_size
    height_px = sw.height * tile_size
    img = Image.new("RGBA", (width_px, height_px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Optional textured mode helpers
    roots: List[str] = [r for r in str(assets_dir).split(os.pathsep) if r] if assets_dir else []

    # Cache textures by material id to avoid repeated I/O
    _tex_cache: Dict[int, Optional[Image.Image]] = {}

    # Build .pak list once for lookups
    pak_paths: List[str] = []
    if roots:
        for root in roots:
            try:
                for dirpath, dirnames, filenames in os.walk(root):
                    for fn in filenames:
                        if fn.endswith('.pak') or fn.endswith('.modpak'):
                            pak_paths.append(os.path.join(dirpath, fn))
            except Exception:
                continue

    def _load_texture_for_material(material_id: int) -> Optional[Image.Image]:
        # Try cached
        if material_id in _tex_cache:
            return _tex_cache[material_id]
        tex_path = reg.get_texture(material_id)
        img_im: Optional[Image.Image] = None
        # First, try directories
        if tex_path and roots:
            rel = tex_path[1:] if tex_path.startswith('/') else tex_path
            for root in roots:
                fp = os.path.join(root, rel)
                if os.path.isfile(fp):
                    try:
                        with Image.open(fp) as im:
                            im = im.convert('RGBA')
                            if im.size != (tile_size, tile_size):
                                im = im.resize((tile_size, tile_size), Image.NEAREST)
                            img_im = im.copy()
                            break
                    except Exception:
                        pass
        # Next, look into .pak files
        if img_im is None and tex_path and pak_paths:
            norm = tex_path.replace('\\','/')
            if not norm.startswith('/'):
                norm = '/' + norm
            norm = norm.lower()
            for pak in pak_paths:
                try:
                    with open(pak, 'rb') as fh:
                        pkg = SBAsset6(fh)
                        pkg.read_index()
                        if norm in pkg.index:
                            data = pkg.get(norm)
                            try:
                                with Image.open(io.BytesIO(data)) as im:
                                    im = im.convert('RGBA')
                                    if im.size != (tile_size, tile_size):
                                        im = im.resize((tile_size, tile_size), Image.NEAREST)
                                    img_im = im.copy()
                                    break
                            except Exception:
                                continue
                except Exception:
                    continue
        _tex_cache[material_id] = img_im
        return img_im

    def paste_tile_texture(ix: int, iy: int, material_id: int) -> bool:
        if not (textured and roots):
            return False
        try:
            im = _load_texture_for_material(material_id)
            if im is None:
                return False
            x0 = ix * tile_size
            y0 = (sw.height - 1 - iy) * tile_size
            img.paste(im, (x0, y0), im)
            return True
        except Exception:
            return False

    def draw_tile(ix: int, iy: int, color, alpha=255):
        x0 = ix * tile_size
        y0 = (sw.height - 1 - iy) * tile_size
        x1 = x0 + tile_size
        y1 = y0 + tile_size
        r, g, b, a = color
        draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=(r, g, b, min(alpha, a)))

    # Background first with lower alpha (textures if available)
    for iy in range(sw.height):
        row_off = iy * sw.width
        for ix in range(sw.width):
            mid = sw.bg[row_off + ix]
            # Only real materials should draw (>0 and <65000)
            if 0 < mid < 65000:
                if paste_tile_texture(ix, iy, mid):
                    continue
                draw_tile(ix, iy, reg.get_color(mid), alpha=180)

    # Foreground next opaque (textures if available)
    for iy in range(sw.height):
        row_off = iy * sw.width
        for ix in range(sw.width):
            mid = sw.fg[row_off + ix]
            if 0 < mid < 65000:
                if paste_tile_texture(ix, iy, mid):
                    continue
                draw_tile(ix, iy, reg.get_color(mid), alpha=255)

    img.save(out_png)
