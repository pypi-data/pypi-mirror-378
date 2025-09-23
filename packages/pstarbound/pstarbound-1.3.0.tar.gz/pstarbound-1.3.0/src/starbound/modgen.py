from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Set
import fnmatch
from PIL import Image, ImageDraw
from .shipworld import load_shipworld, extract_objects, ShipWorld
from .materials import MaterialRegistry, build_provenance


Color = Tuple[int, int, int, int]


def _color_for_index(idx: int) -> Color:
    # Encode idx into RGBA with full alpha
    return (idx & 0xFF, (idx >> 8) & 0xFF, (idx >> 16) & 0xFF, 255)


def _build_pair_keys(reg: MaterialRegistry, pairs: List[Tuple[int, int]], id_override: Dict[int, str]) -> List[Dict]:
    # Build entries for blockKey array. Each entry maps a color value to FG/BG placement.
    entries: List[Dict] = []
    for idx, (bg_id, fg_id) in enumerate(pairs):
        fg_name = None
        if 0 < fg_id < 65000:
            fg_name = id_override.get(fg_id) or reg.get_name(fg_id)
        bg_name = None
        if 0 < bg_id < 65000:
            bg_name = id_override.get(bg_id) or reg.get_name(bg_id)
        entry = {
            "anchor": False,
            "foregroundBlock": bool(fg_name),
            "foregroundMat": fg_name or "",
            "foregroundResidual": False,
            "backgroundBlock": bool(bg_name),
            "backgroundMat": bg_name or "",
            "backgroundResidual": False,
            "object": "",
            "objectDirection": "left",
            "objectParameters": {},
            "objectResidual": False,
            "flags": [],
            "value": list(_color_for_index(idx)),
        }
        entries.append(entry)
    return entries


def generate_mod(
    shipworld_path: str,
    assets_dir: Optional[str],
    out_dir: str,
    mod_id: str,
    mod_name: str,
    *,
    background_overlay: bool = False,
    material_map_path: Optional[str] = None,
    include_objects: bool = False,
    objects_only_known: bool = False,
    objects_log_unknown: Optional[str] = None,
    species: str = "human",
    all_species: bool = False,
    byos: bool = False,
    fu_broken: bool = False,
    ship_tier: int = 8,
    per_tier_structures: bool = False,
    thruster_overlays: bool = False,
    ensure_core_objects: bool = False,
    grid: Optional[ShipWorld] = None,
    objects_bounds: Optional[Tuple[int,int,int,int]] = None,
    object_map_path: Optional[str] = None,
    requires_into_metadata: bool = False,
    report_path: Optional[str] = None,
    materials_include: Optional[List[int]] = None,
    materials_exclude: Optional[List[int]] = None,
    objects_include: Optional[List[str]] = None,
    objects_exclude: Optional[List[str]] = None,
    blocks_position: Optional[Tuple[int,int]] = None,
) -> None:
    # Export a functional .structure that places tiles via blockImage + blockKey (and optional overlay)
    sw = grid if grid is not None else load_shipworld(shipworld_path)
    reg = MaterialRegistry(assets_dir)

    # Apply material include/exclude filters (zero tiles not allowed)
    if materials_include or materials_exclude:
        allow_set = set(int(x) for x in (materials_include or [])) if materials_include else None
        deny_set = set(int(x) for x in (materials_exclude or [])) if materials_exclude else set()
        total = sw.width * sw.height
        for arr in (sw.fg, sw.bg):
            for i in range(total):
                mid = arr[i]
                if not (0 < mid < 65000):
                    continue
                if allow_set is not None and mid not in allow_set:
                    arr[i] = 0
                    continue
                if mid in deny_set:
                    arr[i] = 0
                    continue

    # Optional custom mapping for unknown material ids
    id_override: Dict[int, str] = {}
    if material_map_path:
        p = Path(material_map_path)
        if p.exists():
            raw = json.loads(p.read_text())
            # keys may be strings or ints
            for k, v in raw.items():
                try:
                    kid = int(k)
                except Exception:
                    continue
                id_override[kid] = str(v)

    # Optional object name mapping (before known-only filtering)
    obj_name_map: Dict[str, str] = {}
    if object_map_path:
        p = Path(object_map_path)
        try:
            if p.exists():
                raw = json.loads(p.read_text())
                for k, v in raw.items():
                    if isinstance(k, str) and isinstance(v, str) and k:
                        obj_name_map[k] = v
        except Exception:
            pass

    out = Path(out_dir)
    ship_dir = out / "ships" / "export"
    ship_dir.mkdir(parents=True, exist_ok=True)

    # Build unique (bg, fg) pairs in scanline order to get stable indices/colors
    uniq_pairs: List[Tuple[int, int]] = []
    pair_to_index: Dict[Tuple[int, int], int] = {}
    for y in range(sw.height):
        for x in range(sw.width):
            idx = y * sw.width + x
            p = (sw.bg[idx], sw.fg[idx])
            if p not in pair_to_index:
                pair_to_index[p] = len(uniq_pairs)
                uniq_pairs.append(p)

    # Build blockKey entries and write blockKey.config
    entries = _build_pair_keys(reg, uniq_pairs, id_override)
    blockkey_obj = {"blockKey": entries}
    (ship_dir / "blockKey.config").write_text(json.dumps(blockkey_obj, indent=2))

    # Compute ship bounds (min/max tile containing any material)
    def compute_bounds() -> Tuple[int,int,int,int]:
        min_x, min_y = sw.width, sw.height
        max_x, max_y = -1, -1
        for y in range(sw.height):
            row = y * sw.width
            for x in range(sw.width):
                if (sw.bg[row+x] > 0) or (sw.fg[row+x] > 0):
                    if x < min_x: min_x = x
                    if y < min_y: min_y = y
                    if x > max_x: max_x = x
                    if y > max_y: max_y = y
        if max_x < 0:
            return (0,0,sw.width-1, sw.height-1)
        return (min_x, min_y, max_x, max_y)
    bounds = compute_bounds()

    # Create block image: one pixel per tile, color equals the mapped entry value
    img = Image.new("RGBA", (sw.width, sw.height), (0, 0, 0, 0))
    px = img.load()
    for y in range(sw.height):
        for x in range(sw.width):
            idx = y * sw.width + x
            p = (sw.bg[idx], sw.fg[idx])
            cidx = pair_to_index[p]
            px[x, y] = _color_for_index(cidx)
    blocks_png = ship_dir / "export_blocks.png"
    img.save(blocks_png)

    backgroundOverlays: List[Dict] = []
    if background_overlay:
        # bake a simple color overlay using mapColor and fallback colors
        tile_px = 8
        wpx, hpx = sw.width * tile_px, sw.height * tile_px
        ov = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
        dr = ImageDraw.Draw(ov)
        def draw(ix: int, iy: int, col: Tuple[int, int, int, int], alpha=255):
            x0 = ix * tile_px
            y0 = (sw.height - 1 - iy) * tile_px
            x1 = x0 + tile_px
            y1 = y0 + tile_px
            r,g,b,a = col
            dr.rectangle([x0, y0, x1-1, y1-1], fill=(r,g,b,min(a,alpha)))
        # Draw bg then fg
        for y in range(sw.height):
            row = y * sw.width
            for x in range(sw.width):
                mid = sw.bg[row + x]
                if 0 < mid < 65000:
                    draw(x, y, reg.get_color(mid), alpha=180)
        for y in range(sw.height):
            row = y * sw.width
            for x in range(sw.width):
                mid = sw.fg[row + x]
                if 0 < mid < 65000:
                    draw(x, y, reg.get_color(mid), alpha=255)
        overlay_path = ship_dir / "export_overlay.png"
        ov.save(overlay_path)
        backgroundOverlays.append({
            "image": "export_overlay.png",
            "position": [0, 0],
            "fullbright": True,
        })

    objects_list: List[Dict] = []
    if include_objects:
        objects_list = extract_objects(shipworld_path)
        # Object include/exclude filters (names)
        if objects_include:
            inc = set(s.strip() for s in objects_include if isinstance(s, str))
            objects_list = [o for o in objects_list if isinstance(o.get("name"), str) and o.get("name") in inc]
        if objects_exclude:
            pats = [p.strip() for p in objects_exclude if isinstance(p, str)]
            filtered = []
            for o in objects_list:
                nm = o.get("name")
                if not isinstance(nm, str):
                    continue
                if any(fnmatch.fnmatch(nm, pat) for pat in pats):
                    continue
                filtered.append(o)
            objects_list = filtered
        # Apply object mapping early
        if obj_name_map:
            for o in objects_list:
                try:
                    nm = o.get("name")
                    if isinstance(nm, str) and nm in obj_name_map:
                        o["name"] = obj_name_map[nm]
                except Exception:
                    continue
        if objects_bounds:
            try:
                x0,y0,x1,y1 = objects_bounds
                filtered: List[Dict] = []
                for obj in objects_list:
                    pos = obj.get("position")
                    if isinstance(pos, list) and len(pos) >= 2:
                        ox, oy = int(pos[0]), int(pos[1])
                        if x0 <= ox <= x1 and y0 <= oy <= y1:
                            filtered.append(obj)
                objects_list = filtered
            except Exception:
                pass
        # Optional FU broken engine mapping: replace vanilla 'shipengine' with FU broken engine
        if fu_broken:
            for obj in objects_list:
                try:
                    nm = obj.get("name")
                    if isinstance(nm, str) and nm == "shipengine":
                        obj["name"] = "fu_ftldrivesmall_broken"
                except Exception:
                    continue
        # Optionally ensure core ship objects exist
        if ensure_core_objects:
            def has_obj(substrs: List[str]) -> bool:
                for o in objects_list:
                    nm = str(o.get("name", ""))
                    for s in substrs:
                        if s in nm:
                            return True
                return False
            def find_object_by_substring(sub: str) -> Optional[str]:
                if not assets_dir:
                    return None
                for root in str(assets_dir).split(os.pathsep):
                    root = root.strip()
                    if not root:
                        continue
                    try:
                        for p in Path(root).rglob("*.object"):
                            try:
                                data = json.loads(p.read_text())
                                name = data.get("objectName") or p.stem
                                if isinstance(name, str) and sub in name:
                                    return name
                            except Exception:
                                continue
                    except Exception:
                        continue
                return None
            def clamp(v: int, lo: int, hi: int) -> int:
                return max(lo, min(hi, v))
            min_x, min_y, max_x, max_y = bounds
            cx = (min_x + max_x) // 2
            cy = min_y + 4
            # Helpers to ensure we don't place outside: prefer interior tiles (with background)
            def is_interior(tx: int, ty: int) -> bool:
                if tx < 0 or ty < 0 or tx >= sw.width or ty >= sw.height:
                    return False
                idx = ty * sw.width + tx
                return sw.bg[idx] > 0
            def nearest_interior(tx: int, ty: int, max_radius: int = 20) -> Tuple[int,int]:
                if is_interior(tx, ty):
                    return tx, ty
                for r in range(1, max_radius+1):
                    for dx in range(-r, r+1):
                        for dy in (-r, r):
                            x = clamp(tx+dx, min_x, max_x)
                            y = clamp(ty+dy, min_y, max_y)
                            if is_interior(x, y):
                                return x, y
                    for dy in range(-r+1, r):
                        for dx in (-r, r):
                            x = clamp(tx+dx, min_x, max_x)
                            y = clamp(ty+dy, min_y, max_y)
                            if is_interior(x, y):
                                return x, y
                return clamp(tx, min_x, max_x), clamp(ty, min_y, max_y)
            # Detect Mass Effect Normandy context (path or objects)
            lowered_path = str(shipworld_path).lower()
            is_normandy_me = ("mass effect" in lowered_path) or ("normandy" in lowered_path)
            if not is_normandy_me:
                for o in objects_list:
                    nm = str(o.get("name", "")).lower()
                    if "sr1" in nm or "galaxyconsole" in nm or "cicstation" in nm:
                        is_normandy_me = True
                        break
            # Build desired core set: concept -> (search substrings, default position, default direction)
            desired = [
                # Mass Effect nav console variants recognized alongside vanilla captainschair
                ("captainschair", ["captainschair", "galaxyconsole", "galaxystation", "cicstation", "cic"], [cx, cy], "left"),
                ("teleporter", ["teleporter"], [min_x + 4, cy], "right"),
                ("fuelhatch", ["fuelhatch"], [min_x + 6, cy], "right"),
                ("techstation", ["techstation", "sail"], [cx - 2, cy], "right"),
                ("shiplocker", ["shiplocker"], [min_x + 8, cy], "right"),
                ("engine", ["shipengine", "ftl"], [max_x - 4, cy], "left"),
            ]
            for concept, substrs, pos, direction in desired:
                if concept == "engine":
                    present = has_obj(["engine"]) or has_obj(["shipengine"]) or has_obj(["ftl"])
                else:
                    present = has_obj(substrs)
                if present:
                    continue
                # pick candidate
                cand = None
                if concept == "engine" and byos and fu_broken:
                    # Always place FU broken engine when BYOS + --fu-broken
                    cand = "fu_ftldrivesmall_broken"
                    target = [cx, cy]
                    if is_normandy_me:
                        # Prefer placement above the fuel hatch if available
                        fh_pos = None
                        for o in objects_list:
                            try:
                                nm_o = str(o.get("name", "")).lower()
                                if "fuelhatch" in nm_o:
                                    p_o = o.get("position")
                                    if isinstance(p_o, list) and len(p_o) >= 2:
                                        fh_pos = [int(p_o[0]), int(p_o[1])]
                                        break
                            except Exception:
                                continue
                        if fh_pos:
                            target = [fh_pos[0], fh_pos[1] + 6]
                    # Ensure interior placement (never outside). If not interior, find nearest interior; otherwise center
                    tx, ty = nearest_interior(int(target[0]), int(target[1]))
                    pos = [tx, ty]
                    direction = "left"
                else:
                    # lookup candidate name from assets
                    for s in substrs:
                        cand = find_object_by_substring(s)
                        if cand:
                            break
                if not cand:
                    continue
                x = clamp(int(pos[0]), min_x, max_x)
                y = clamp(int(pos[1]), min_y, max_y)
                # If this is engine and we did not run nearest_interior (non-BYOS case), still snap to interior near chosen pos
                if concept == "engine" and not (byos and fu_broken):
                    x, y = nearest_interior(x, y)
                objects_list.append({
                    "position": [x, y],
                    "name": cand,
                    "direction": direction,
                    "parameters": {},
                    "residual": False,
                })
        # Build known object names from assets roots (for filtering and reporting)
        known: Set[str] = set()
        if assets_dir:
            for root in str(assets_dir).split(os.pathsep):
                root = root.strip()
                if not root:
                    continue
                # Directory .object files
                for p in Path(root).rglob("*.object"):
                    try:
                        data = json.loads(p.read_text())
                        name = data.get("objectName") or p.stem
                        if isinstance(name, str) and name:
                            known.add(name)
                    except Exception:
                        try:
                            known.add(p.stem)
                        except Exception:
                            pass
                # .pak/.modpak contents
                try:
                    pak_files = list(Path(root).rglob("*.pak")) + list(Path(root).rglob("*.modpak"))
                    for pf in pak_files:
                        try:
                            from .sbasset6 import SBAsset6
                            with open(pf, 'rb') as fh:
                                pkg = SBAsset6(fh)
                                pkg.read_index()
                                for k in list(pkg.index.keys()):
                                    if not k.endswith('.object'):
                                        continue
                                    try:
                                        data = json.loads(pkg.get(k).decode('utf-8'))
                                        nm = data.get("objectName")
                                        if isinstance(nm, str) and nm:
                                            known.add(nm)
                                    except Exception:
                                        # as last resort, use stem
                                        nm = k.rsplit('/', 1)[-1].rsplit('.', 1)[0]
                                        if nm:
                                            known.add(nm)
                        except Exception:
                            continue
                except Exception:
                    pass
        # Unknown object counts (for report and optional filtering)
        unknown_counts: Dict[str, int] = {}
        for obj in objects_list:
            nm = obj.get("name")
            if isinstance(nm, str) and nm and (known and nm not in known):
                unknown_counts[nm] = unknown_counts.get(nm, 0) + 1

        if objects_only_known:
            filtered: List[Dict] = []
            for obj in objects_list:
                nm = obj.get("name")
                if isinstance(nm, str) and (not known or nm in known):
                    filtered.append(obj)
            objects_list = filtered
            # Log unknowns if requested
            log_path = objects_log_unknown
            if not log_path:
                log_path = str(ship_dir / "unknown_objects.json")
            if unknown_counts:
                try:
                    Path(log_path).write_text(json.dumps({"counts": unknown_counts, "total": sum(unknown_counts.values())}, indent=2))
                except Exception:
                    pass

    def ship_upgrades_for_tier(t: int) -> Dict:
        # Vanilla-like values without maxFuel
        if t <= 1:
            caps: List[str] = []
        elif t == 2:
            caps = ["teleport", "planetTravel"]
        else:
            caps = ["teleport", "planetTravel", "systemTravel"]
        crew = 2 if t <= 3 else min(12, 2 + 2 * (t - 3))
        return {"capabilities": caps, "crewSize": crew}

    def build_thruster_overlay_img(engine_positions: List[Tuple[int,int]], tier: int) -> Optional[str]:
        if not thruster_overlays or not engine_positions:
            return None
        tile_px = 8
        wpx, hpx = sw.width * tile_px, sw.height * tile_px
        ov = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
        dr = ImageDraw.Draw(ov)
        # radius grows with tier; tiers <2 have no overlay
        if tier < 2:
            return None
        r = max(3, min(10, 3 + tier))
        base_alpha = min(220, 80 + tier * 15)
        color = (120, 180, 255, base_alpha)
        for (tx, ty) in engine_positions:
            cx = tx * tile_px + tile_px // 2
            cy = (sw.height - 1 - ty) * tile_px + tile_px // 2
            bbox = [cx - r, cy - r, cx + r, cy + r]
            dr.ellipse(bbox, fill=color)
        fname = f"export_thrusters_t{tier}.png"
        (ship_dir / fname).write_text("")  # ensure path exists before save on some FS
        ov.save(ship_dir / fname)
        return fname

    # Determine engine positions for thruster overlays (if desired)
    engine_positions: List[Tuple[int,int]] = []
    for o in objects_list:
        nm = str(o.get("name", ""))
        if ("engine" in nm) or (nm == "shipengine") or (nm == "fu_ftldrivesmall_broken"):
            pos = o.get("position")
            if isinstance(pos, list) and len(pos) >= 2:
                engine_positions.append((int(pos[0]), int(pos[1])))

    def make_structure_for_tier(t: int) -> Dict:
        cfg = {}
        if byos:
            # FU BYOS minimal config; explicitly set shipLevel 0
            cfg = {"shipUpgrades": {"capabilities": [], "crewSize": 0, "shipLevel": 0}}
        else:
            cfg = {"shipUpgrades": ship_upgrades_for_tier(t)}
        bos: List[Dict] = list(backgroundOverlays)
        thr_png = build_thruster_overlay_img(engine_positions, t)
        if thr_png:
            bos.append({"image": thr_png, "position": [0, 0], "fullbright": True})
        return {
            "config": cfg,
            "backgroundOverlays": bos,
            "foregroundOverlays": [],
            "blocksPosition": list(blocks_position) if blocks_position else [0, 0],
            "blockKey": "blockKey.config:blockKey",
            "blockImage": "export_blocks.png",
            "objects": objects_list,
        }

    structure_paths: List[str] = []
    if per_tier_structures and not byos:
        tiers_paths: List[str] = []
        for t in range(0, 9):
            st = make_structure_for_tier(t)
            p = ship_dir / f"exported_T{t}.structure"
            p.write_text(json.dumps(st, indent=2))
            tiers_paths.append(f"/ships/export/exported_T{t}.structure")
        structure_paths = list(tiers_paths)
    else:
        # Single structure
        st = make_structure_for_tier(ship_tier if not byos else 0)
        (ship_dir / "exported.structure").write_text(json.dumps(st, indent=2))
        structure_paths = ["/ships/export/exported.structure"]

    # Report unresolved (likely modded) materials that were not found by name and not covered by override
    unresolved: List[int] = []
    used_mats: List[int] = sorted(set([m for m in (sw.fg + sw.bg) if 0 < m < 65000]))
    if assets_dir or id_override:
        for mid in used_mats:
            if id_override.get(mid):
                continue
            if not reg.get_name(mid):
                unresolved.append(mid)
    # Also write a ships/export/unresolved.json with counts
    if unresolved:
        counts: Dict[int, int] = {}
        for arr in (sw.fg, sw.bg):
            for mid in arr:
                if 0 < mid < 65000 and (id_override.get(mid) or reg.get_name(mid)):
                    continue
                if 0 < mid < 65000:
                    counts[mid] = counts.get(mid, 0) + 1
        (ship_dir / "unresolved.json").write_text(json.dumps({"counts": counts, "ids": unresolved}, indent=2))

    # Compute and write requires.json (mods providing materials/objects used)
    req = {"mods": [], "details": {"materials": {}, "objects": {}}}
    try:
        if assets_dir:
            prov = build_provenance(assets_dir)
            mats_prov: Dict[int, Dict] = prov.get("materials", {})
            objs_prov: Dict[str, Dict] = prov.get("objects", {})
            mods: Dict[str, int] = {}
            # materials
            det_mats: Dict[str, Dict[str, object]] = {}
            for mid in used_mats:
                entry = mats_prov.get(mid)
                name = id_override.get(mid) or reg.get_name(mid)
                modsrc = entry.get("mod") if entry else None
                det_mats[str(mid)] = {"name": name, "mod": modsrc}
                if modsrc:
                    mods[modsrc] = 1
            # objects
            det_objs: Dict[str, Dict[str, object]] = {}
            for obj in objects_list:
                nm = obj.get("name")
                if not isinstance(nm, str):
                    continue
                entry = objs_prov.get(nm)
                modsrc = entry.get("mod") if entry else None
                det_objs[nm] = {"mod": modsrc}
                if modsrc:
                    mods[modsrc] = 1
            req = {"mods": sorted(mods.keys()), "details": {"materials": det_mats, "objects": det_objs}}
        (out / "requires.json").write_text(json.dumps(req, indent=2))
    except Exception:
        pass

    # Optional report JSON with counts and provenance summary
    if report_path:
        try:
            mat_counts: Dict[int, int] = {}
            for arr in (sw.fg, sw.bg):
                for mid in arr:
                    if 0 < mid < 65000:
                        mat_counts[mid] = mat_counts.get(mid, 0) + 1
            obj_counts: Dict[str, int] = {}
            for o in objects_list:
                nm = o.get("name")
                if isinstance(nm, str) and nm:
                    obj_counts[nm] = obj_counts.get(nm, 0) + 1
            report = {
                "materials": {"counts": mat_counts, "unresolved": unresolved},
                "objects": {"counts": obj_counts},
                "provenance": {"mods": req.get("mods", [])},
            }
            Path(report_path).write_text(json.dumps(report, indent=2))
        except Exception:
            pass

    metadata = {
        "name": mod_id,
        "friendlyName": mod_name,
        "version": "0.1.0",
        "author": "py-starbound",
        "description": f"Exported from shipworld (size {sw.width}x{sw.height}). Unknown/modded materials require the corresponding assets present.",
        "_unresolvedMaterialIds": unresolved,
    }
    if requires_into_metadata and req.get("mods"):
        try:
            metadata["requires"] = list(req["mods"])  # simple mod name list
        except Exception:
            pass
    (out / "_metadata").write_text(json.dumps(metadata, indent=2))

    # Write universe_server.config.patch to make the structure playable
    # Choose per-tier paths if requested, else repeat single structure for all tiers.
    if per_tier_structures and not byos:
        tiers = [f"/ships/export/exported_T{t}.structure" for t in range(0,9)]
    else:
        tiers = ["/ships/export/exported.structure"] * 9
    if all_species:
        species_list = ["human", "apex", "avian", "floran", "glitch", "hylotl", "novakid"]
    else:
        species_list = [species]
    usp = []
    if byos:
        # BYOS mode: add BYOS keys commonly used by mods; we avoid replacing vanilla ships
        # Add both generic and FU-specific BYOS paths so either mod can pick it up.
        for spc in species_list:
            usp.append({
                "op": "add",
                "path": f"/byosShips/{spc}",
                "value": tiers,
            })
            usp.append({
                "op": "add",
                "path": f"/fu_byosShips/{spc}",
                "value": tiers,
            })
    else:
        # Vanilla override
        for spc in species_list:
            usp.append({
                "op": "replace",
                "path": f"/speciesShips/{spc}",
                "value": tiers,
            })
    (out / "universe_server.config.patch").write_text(json.dumps(usp, indent=2))

    # Return structure paths and context for combined patch usage
    return {"structure_paths": structure_paths, "byos": byos, "species_list": species_list}
