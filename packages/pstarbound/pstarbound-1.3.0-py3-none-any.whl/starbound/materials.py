from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any
import json
import hashlib
import os
import mmap
from .sbasset6 import SBAsset6


@dataclass
class MaterialInfo:
    material_id: int
    name: str
    map_color: Tuple[int, int, int, int]
    texture: Optional[str] = None  # asset path like '/tiles/materials/name.png'


class MaterialRegistry:
    def __init__(self, assets_dir: Optional[str] = None):
        self._by_id: Dict[int, MaterialInfo] = {}
        if assets_dir:
            # support multiple roots separated by os.pathsep
            for p in str(assets_dir).split(os.pathsep):
                p = p.strip()
                if not p:
                    continue
                path = Path(p)
                self._load(path)
                # If a directory root is given, also load any .pak files inside it
                try:
                    if path.is_dir():
                        for pak in list(path.rglob("*.pak")) + list(path.rglob("*.modpak")):
                            self._load(pak)
                except Exception:
                    pass

    def _load(self, root: Path) -> None:
        """Load material info from a directory tree or a .pak file."""
        try:
            if root.is_file() and root.suffix.lower() in (".pak", ".modpak"):
                with open(root, 'rb') as fh:
                    mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
                    pkg = SBAsset6(mm)
                    pkg.read_index()
                    for path in pkg.index.keys():
                        if not path.endswith(".material"):
                            continue
                        try:
                            data = json.loads(pkg.get(path).decode('utf-8'))
                            mid = int(data.get("materialId"))
                            name = str(data.get("materialName", f"mat:{mid}"))
                            map_color = data.get("mapColor") or [150, 150, 150, 255]
                            if isinstance(map_color, list) and len(map_color) == 3:
                                map_color = [*map_color, 255]
                            # Try to resolve a texture path from renderParameters
                            tex = None
                            rp = data.get("renderParameters") or {}
                            if isinstance(rp, dict):
                                # Try common keys and simple variants collection
                                for k in ("texture", "fgTexture", "bgTexture"):
                                    t = rp.get(k)
                                    if isinstance(t, str) and t:
                                        tex = t
                                        break
                                if not tex and isinstance(rp.get("textures"), dict):
                                    # pick first string value
                                    for v in rp.get("textures").values():
                                        if isinstance(v, str) and v:
                                            tex = v
                                            break
                            info = MaterialInfo(material_id=mid, name=name, map_color=tuple(map_color), texture=tex)
                            self._by_id[mid] = info
                        except Exception:
                            continue
                return
        except Exception:
            # fall back to directory handling
            pass
        # Directory handling
        mats = list(root.rglob("*.material")) if root.exists() else []
        for m in mats:
            try:
                data = json.loads(m.read_text())
                mid = int(data.get("materialId"))
                name = str(data.get("materialName", f"mat:{mid}"))
                map_color = data.get("mapColor") or [150, 150, 150, 255]
                if isinstance(map_color, list) and len(map_color) == 3:
                    map_color = [*map_color, 255]
                tex = None
                rp = data.get("renderParameters") or {}
                if isinstance(rp, dict):
                    for k in ("texture", "fgTexture", "bgTexture"):
                        t = rp.get(k)
                        if isinstance(t, str) and t:
                            tex = t
                            break
                    if not tex and isinstance(rp.get("textures"), dict):
                        for v in rp.get("textures").values():
                            if isinstance(v, str) and v:
                                tex = v
                                break
                info = MaterialInfo(material_id=mid, name=name, map_color=tuple(map_color), texture=tex)
                self._by_id[mid] = info
            except Exception:
                continue

    def get_color(self, material_id: int) -> Tuple[int, int, int, int]:
        # Real materials: id > 0 and < 65000 per engine (metamaterials >= 65000)
        if 0 < material_id < 65000 and material_id in self._by_id:
            return self._by_id[material_id].map_color
        # fallback stable pseudo color
        h = hashlib.sha1(str(material_id).encode()).digest()
        return (80 + h[0] % 120, 80 + h[1] % 120, 80 + h[2] % 120, 255)

    def get_name(self, material_id: int) -> Optional[str]:
        mi = self._by_id.get(material_id)
        return mi.name if mi else None

    def get_texture(self, material_id: int) -> Optional[str]:
        mi = self._by_id.get(material_id)
        return mi.texture if mi else None


def _read_dir_metadata(root: Path) -> Dict[str, Any]:
    for fn in ("_metadata", ".metadata"):
        p = root / fn
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                return {}
    return {}


def _read_pak_metadata(pak_path: Path) -> Dict[str, Any]:
    try:
        with open(pak_path, 'rb') as fh:
            mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
            pkg = SBAsset6(mm)
            pkg.read_index()
            for meta_name in ("/_metadata", "/.metadata"):
                if meta_name in pkg.index:
                    try:
                        data = pkg.get(meta_name)
                        return json.loads(data.decode('utf-8'))
                    except Exception:
                        return {}
    except Exception:
        return {}
    return {}


def build_provenance(assets_dir: Optional[str]) -> Dict[str, Any]:
    """Scan assets roots (dirs or .pak) and return provenance:
    {
      'materials': { id: { 'name': str|None, 'mod': str|None } },
      'objects':   { name: { 'mod': str|None } },
      'mods':      [ { 'path': root, 'name': modname } ... ]
    }
    Later roots override earlier ones for conflicts.
    """
    prov_mats: Dict[int, Dict[str, Any]] = {}
    prov_objs: Dict[str, Dict[str, Any]] = {}
    mods_list: List[Dict[str, Any]] = []

    def scan_dir_mod(mod_root: Path, modname: str):
        # materials
        for m in mod_root.rglob("*.material"):
            try:
                data = json.loads(m.read_text())
                mid = int(data.get("materialId"))
                name = data.get("materialName")
                prov_mats[mid] = {"name": name, "mod": modname}
            except Exception:
                continue
        # objects
        for o in mod_root.rglob("*.object"):
            try:
                data = json.loads(o.read_text())
                name = data.get("objectName") or o.stem
                if isinstance(name, str) and name:
                    prov_objs[name] = {"mod": modname}
            except Exception:
                try:
                    nm = o.stem
                    if nm:
                        prov_objs[nm] = {"mod": modname}
                except Exception:
                    continue

    def scan_pak(p: Path):
        md = _read_pak_metadata(p) or {}
        modname = md.get("name") or md.get("friendlyName") or p.name
        mods_list.append({"path": str(p), "name": modname})
        try:
            with open(p, 'rb') as fh:
                mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
                pkg = SBAsset6(mm)
                pkg.read_index()
                for path in list(pkg.index.keys()):
                    if path.endswith(".material"):
                        try:
                            data = json.loads(pkg.get(path).decode('utf-8'))
                            mid = int(data.get("materialId"))
                            name = data.get("materialName")
                            prov_mats[mid] = {"name": name, "mod": modname}
                        except Exception:
                            continue
                    elif path.endswith(".object"):
                        try:
                            data = json.loads(pkg.get(path).decode('utf-8'))
                            name = data.get("objectName")
                            if isinstance(name, str) and name:
                                prov_objs[name] = {"mod": modname}
                        except Exception:
                            continue
        except Exception:
            pass

    if not assets_dir:
        return {"materials": prov_mats, "objects": prov_objs, "mods": mods_list}

    for raw in str(assets_dir).split(os.pathsep):
        raw = raw.strip()
        if not raw:
            continue
        p = Path(raw)
        if p.is_file() and p.suffix.lower() in (".pak", ".modpak"):
            scan_pak(p)
            continue
        if p.is_dir():
            # Case 1: the directory itself is a mod root
            md = _read_dir_metadata(p)
            if md:
                modname = md.get("name") or md.get("friendlyName") or p.name
                mods_list.append({"path": str(p), "name": modname})
                scan_dir_mod(p, modname)
            else:
                # Case 2: treat as container; scan immediate subdirs and any .pak inside
                try:
                    for child in p.iterdir():
                        if child.is_dir():
                            mdc = _read_dir_metadata(child)
                            if mdc:
                                modname = mdc.get("name") or mdc.get("friendlyName") or child.name
                                mods_list.append({"path": str(child), "name": modname})
                                scan_dir_mod(child, modname)
                        elif child.is_file() and child.suffix.lower() in (".pak", ".modpak"):
                            scan_pak(child)
                except Exception:
                    pass
                # Also catch nested .pak deeper in the tree
                for pak in list(p.rglob("*.pak")) + list(p.rglob("*.modpak")):
                    scan_pak(pak)
            continue
        # Unknown entry: skip
        continue

    return {"materials": prov_mats, "objects": prov_objs, "mods": mods_list}
