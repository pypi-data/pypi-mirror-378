import sys
import argparse


from typing import List, Optional, Tuple

def _delegate_to(module_name: str, argv: List[str]) -> int:
    # Delegate to optparse-based subcommand by adjusting sys.argv.
    import importlib
    mod = importlib.import_module(module_name)
    old_argv = sys.argv
    try:
        sys.argv = [f"pystarbound {module_name.split('.')[-1]}"] + argv
        return int(mod.main() or 0)
    finally:
        sys.argv = old_argv


def _render(argv: List[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="pystarbound render", description="Render a shipworld to PNG")
    p.add_argument("shipworld", help="Path to .shipworld file")
    p.add_argument("--assets", default=None, help="Path to unpacked Starbound assets directory (optional)")
    p.add_argument("-o", "--output", required=True, help="Output PNG path")
    p.add_argument("--tile-size", type=int, default=8, help="Pixels per tile (default 8)")
    args = p.parse_args(argv)
    try:
        from . import render as _render_mod
    except Exception as e:
        # Most likely due to missing Pillow
        sys.stderr.write("Pillow not installed. Install optional extra: pip install 'py-starbound[ship]'\n")
        return 1
    _render_mod.render_shipworld(args.shipworld, assets_dir=args.assets, out_png=args.output, tile_size=args.tile_size)
    return 0


def _modgen(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="pystarbound modgen", description="Generate a minimal mod from shipworld")
    p.add_argument("shipworld", help="Path to .shipworld file")
    p.add_argument("--assets", default=None, help="Path(s) to unpacked assets directory. Use OS path separator to pass multiple roots (e.g. '/A:/B')")
    p.add_argument("-o", "--out-dir", required=True, help="Output mod directory")
    p.add_argument("--mod-id", default="export", help="Mod id")
    p.add_argument("--mod-name", default="SB Ship Export", help="Mod friendly name")
    p.add_argument("--background-overlay", action="store_true", help="Also bake a colored background overlay PNG and reference it in structure")
    p.add_argument("--material-map", default=None, help="JSON file mapping materialId to material name for unknown ids")
    p.add_argument("--objects", action="store_true", help="Also export objects detected in the shipworld")
    p.add_argument("--objects-only-known", action="store_true", help="When exporting objects, keep only those known in provided assets")
    p.add_argument("--objects-log-unknown", default=None, help="When exporting objects, write unknown object names and counts to this JSON")
    p.add_argument("--species", default="human", help="Species key to patch (default: human)")
    p.add_argument("--all-species", action="store_true", help="Patch all vanilla species")
    p.add_argument("--byos", action="store_true", help="BYOS mode: add BYOS keys instead of replacing vanilla ships")
    p.add_argument("--fu-broken", action="store_true", help="Replace vanilla 'shipengine' with FU 'fu_ftldrivesmall_broken' in exported objects")
    p.add_argument("--ship-tier", type=int, choices=range(0,9), default=8, help="Vanilla override: inject shipUpgrades for this tier (0-8)")
    p.add_argument("--per-tier-structures", action="store_true", help="Vanilla override: generate exported_T0..exported_T8.structure and patch each tier")
    p.add_argument("--thruster-overlays", action="store_true", help="Add simple blue thruster glow overlays by tier (if engine position can be detected)")
    p.add_argument("--ensure-core-objects", action="store_true", help="Ensure core ship objects exist by spawning safe defaults when missing")
    args = p.parse_args(argv)
    try:
        from . import modgen as _modgen_mod
    except Exception:
        sys.stderr.write("Pillow not installed. Install optional extra: pip install 'py-starbound[ship]'\n")
        return 1
    _modgen_mod.generate_mod(
        args.shipworld,
        assets_dir=args.assets,
        out_dir=args.out_dir,
        mod_id=args.mod_id,
        mod_name=args.mod_name,
        background_overlay=args.background_overlay,
        material_map_path=args.material_map,
        include_objects=args.objects,
        objects_only_known=args.objects_only_known,
        objects_log_unknown=args.objects_log_unknown,
        species=args.species,
        all_species=args.all_species,
        byos=args.byos,
        fu_broken=args.fu_broken,
        ship_tier=args.ship_tier,
        per_tier_structures=args.per_tier_structures,
        thruster_overlays=args.thruster_overlays,
        ensure_core_objects=args.ensure_core_objects,
    )
    return 0


def _asset_pack(argv: List[str]) -> int:
    import fnmatch, json, os
    from pathlib import Path
    p = argparse.ArgumentParser(prog="pystarbound publish", description="Create SBAsset6 package from directory")
    p.add_argument("input_dir", help="Directory to pack")
    p.add_argument("-o", "--output", required=True, help="Output .pak path")
    p.add_argument("--metadata", default=None, help="Optional JSON file with metadata map for package")
    p.add_argument("--meta", action="append", default=None, help="Inline metadata key=value (repeatable)")
    p.add_argument("--strip-prefix", default="", help="Strip this leading path segment from stored paths")
    p.add_argument("--only", action="append", default=None, help="Only include files matching glob (repeatable)")
    p.add_argument("--exclude", action="append", default=None, help="Exclude files matching glob (repeatable)")
    args = p.parse_args(argv)
    meta = {}
    if args.metadata:
        if not os.path.exists(args.metadata):
            sys.stderr.write(f"Metadata file not found: {args.metadata}\n")
            return 2
        with open(args.metadata, 'r') as f:
            meta.update(json.load(f))
    if args.meta:
        for kv in args.meta:
            if '=' not in kv:
                sys.stderr.write(f"Invalid --meta '{kv}', expected key=value\n")
                return 2
            k,v = kv.split('=',1)
            meta[k] = v
    root = Path(args.input_dir)
    if not root.is_dir():
        sys.stderr.write(f"Not a directory: {args.input_dir}\n")
        return 2
    only = args.only or []
    exclude = args.exclude or []
    strip = args.strip_prefix
    def keep(rel: str) -> bool:
        if only:
            ok = any(fnmatch.fnmatch(rel, pat) for pat in only)
            if not ok:
                return False
        if exclude:
            if any(fnmatch.fnmatch(rel, pat) for pat in exclude):
                return False
        return True
    files = {}
    for fp in root.rglob('*'):
        if fp.is_file():
            rel = str(fp.relative_to(root)).replace('\\','/')
            if strip and rel.startswith(strip):
                rel2 = rel[len(strip):]
                if rel2.startswith('/'):
                    rel2 = rel2[1:]
            else:
                rel2 = rel
            if not keep(rel2):
                continue
            with open(fp, 'rb') as f:
                files[rel2] = f.read()
    from .sbasset6 import write_sbasset6
    try:
        with open(args.output, 'wb') as out:
            write_sbasset6(out, files, metadata=meta)
    except Exception as e:
        sys.stderr.write(f"publish failed: {e}\n")
        return 1
    return 0


def _export_list(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="pystarbound export --list", add_help=False)
    p.add_argument("pak", nargs=1)
    p.add_argument("-d", "--destination", dest="path", default=None)
    p.add_argument("--list", action="store_true")
    args, _ = p.parse_known_args(argv)
    pak = args.pak[0]
    from .sbasset6 import SBAsset6
    import mmap
    with open(pak, 'rb') as fh:
        mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
        pkg = SBAsset6(mm)
        pkg.read_index()
        for path in pkg.index.keys():
            sys.stdout.write(f"{path}\n")
    return 0


def _vjson_dump(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="pystarbound vjson-dump", description="Dump SBVJ01 to JSON")
    p.add_argument("input", help="Input SBVJ01 file")
    p.add_argument("-o", "--output", default=None, help="Output JSON path (default stdout)")
    p.add_argument("--indent", type=int, default=2, help="JSON indent (default 2)")
    args = p.parse_args(argv)
    import json
    with open(args.input, 'rb') as f:
        from . import read_sbvj01
        name, ver, data = read_sbvj01(f)
    out_obj = {"name": name, "version": ver, "data": data}
    if args.output:
        with open(args.output, 'w') as out:
            json.dump(out_obj, out, indent=args.indent)
    else:
        sys.stdout.write(json.dumps(out_obj, indent=args.indent) + "\n")
    return 0


def _vjson_make(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="pystarbound vjson-make", description="Create SBVJ01 from JSON")
    p.add_argument("input", help="Input JSON file with keys: name, data, [version]")
    p.add_argument("-o", "--output", required=True, help="Output SBVJ01 file path")
    args = p.parse_args(argv)
    import json
    with open(args.input, 'r') as f:
        obj = json.load(f)
    name = obj.get('name')
    data = obj.get('data')
    ver = obj.get('version')
    if not isinstance(name, str):
        sys.stderr.write("JSON must contain string 'name'\n")
        return 2
    from . import VersionedJSON, write_sbvj01
    vj = VersionedJSON(name=name, version=ver, data=data)
    with open(args.output, 'wb') as out:
        write_sbvj01(out, vj)
    return 0


def _vjson_edit(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="pystarbound vjson-edit", description="Edit SBVJ01 using dotted-path assignments (applies to data payload)")
    p.add_argument("input", help="Input SBVJ01 file")
    p.add_argument("-o", "--output", required=True, help="Output SBVJ01 file path")
    p.add_argument("--set", dest="sets", action="append", default=None, help="Set key.path=value (repeatable)")
    p.add_argument("--delete", dest="deletes", action="append", default=None, help="Delete key.path (repeatable)")
    p.add_argument("--patch", dest="patches", action="append", default=None, help="Apply JSON patch file(s) merged into data (repeatable)")
    p.add_argument("--append", dest="appends", action="append", default=None, help="Append JSON value to list at key.path (repeatable)")
    p.add_argument("--name", dest="vjname", default=None, help="Override versioned JSON name")
    p.add_argument("--version", dest="vjver", type=int, default=None, help="Override versioned JSON version (int)")
    args = p.parse_args(argv)
    from . import read_sbvj01, write_sbvj01, VersionedJSON
    import json as _json

    def parse_value(s: str):
        try:
            return _json.loads(s)
        except Exception:
            return s

    def set_path(obj: dict, path: str, value):
        parts = [p for p in path.split('.') if p]
        if not parts:
            return
        cur = obj
        for k in parts[:-1]:
            if k not in cur or not isinstance(cur.get(k), dict):
                cur[k] = {}
            cur = cur[k]
        cur[parts[-1]] = value

    def del_path(obj: dict, path: str):
        parts = [p for p in path.split('.') if p]
        if not parts:
            return
        cur = obj
        for k in parts[:-1]:
            if not isinstance(cur, dict) or k not in cur:
                return
            cur = cur[k]
        if isinstance(cur, dict):
            cur.pop(parts[-1], None)

    def append_path(obj: dict, path: str, value):
        parts = [p for p in path.split('.') if p]
        if not parts:
            return
        cur = obj
        for k in parts[:-1]:
            if k not in cur or not isinstance(cur.get(k), dict):
                cur[k] = {}
            cur = cur[k]
        last = parts[-1]
        if last not in cur or not isinstance(cur[last], list):
            cur[last] = []
        cur[last].append(value)

    def deep_merge(dst, src):
        if not isinstance(src, dict):
            return src
        for k, v in src.items():
            if isinstance(v, dict) and isinstance(dst.get(k), dict):
                deep_merge(dst[k], v)
            else:
                dst[k] = v
        return dst

    with open(args.input, 'rb') as f:
        vj = read_sbvj01(f)
    name = args.vjname if args.vjname is not None else vj.name
    ver = args.vjver if args.vjver is not None else vj.version
    data = vj.data if isinstance(vj.data, dict) else {}

    # Apply JSON patch files (deep merge)
    if args.patches:
        for pp in args.patches:
            try:
                with open(pp, 'r') as pf:
                    patch_obj = _json.load(pf)
                if isinstance(patch_obj, dict):
                    deep_merge(data, patch_obj)
            except Exception as e:
                sys.stderr.write(f"Failed to apply patch {pp}: {e}\n")
                return 2

    if args.sets:
        for s in args.sets:
            if '=' not in s:
                sys.stderr.write(f"Invalid --set '{s}', expected key.path=value\n")
                return 2
            k, v = s.split('=', 1)
            set_path(data, k.strip(), parse_value(v))
    if args.deletes:
        for d in args.deletes:
            del_path(data, d.strip())
    if args.appends:
        for s in args.appends:
            if '=' not in s:
                sys.stderr.write(f"Invalid --append '{s}', expected key.path=value\n")
                return 2
            k, v = s.split('=', 1)
            append_path(data, k.strip(), parse_value(v))

    with open(args.output, 'wb') as out:
        write_sbvj01(out, VersionedJSON(name=name, version=ver, data=data))
    return 0


def _player_info(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="pystarbound player-info", description="Show basic info from a .player SBVJ01 file")
    p.add_argument("player", help="Path to .player file (SBVJ01)")
    p.add_argument("--json", action="store_true", help="Output JSON")
    args = p.parse_args(argv)
    from . import read_sbvj01
    import json as _json
    with open(args.player, 'rb') as f:
        vj = read_sbvj01(f)
    d = vj.data if isinstance(vj.data, dict) else {}
    ident = d.get('identity', {}) if isinstance(d.get('identity'), dict) else {}
    info = {
        'name': ident.get('name'),
        'species': ident.get('species') or d.get('species'),
        'uuid': d.get('uuid'),
        'vj_name': vj.name,
        'vj_version': vj.version,
    }
    if args.json:
        sys.stdout.write(_json.dumps(info, indent=2) + "\n")
    else:
        for k in ('name','species','uuid','vj_name','vj_version'):
            sys.stdout.write(f"{k}: {info.get(k)}\n")
    return 0


def _detect_install(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="pystarbound detect-install", description="Detect Starbound install directories via Steam")
    p.add_argument("--steam-dir", default=None, help="Path to Steam base directory (optional)")
    p.add_argument("--appid", type=int, default=211820, help="Steam AppID (default 211820)")
    p.add_argument("--json", action="store_true", help="Output JSON")
    args = p.parse_args(argv)
    try:
        from . import workshop as ws
        inst = ws.find_install_dir(appid=args.appid, steam_dir=args.steam_dir)
        mods = ws.find_mods_dir(appid=args.appid, steam_dir=args.steam_dir)
        wshop = ws.find_workshop_dir(appid=args.appid, steam_dir=args.steam_dir)
        obj = {"install": str(inst) if inst else None, "mods": str(mods) if mods else None, "workshop": str(wshop) if wshop else None}
        if args.json:
            import json
            sys.stdout.write(json.dumps(obj, indent=2) + "\n")
        else:
            for k,v in obj.items():
                sys.stdout.write(f"{k}: {v}\n")
        return 0
    except Exception as e:
        sys.stderr.write(f"detect-install failed: {e}\n")
        return 1


def _verify(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="pystarbound verify", description="Verify SBAsset6 structure")
    p.add_argument("pak", help="Path to .pak/.modpak")
    args = p.parse_args(argv)
    from .sbasset6 import verify_sbasset6
    res = verify_sbasset6(args.pak)
    if res["ok"]:
        sys.stdout.write(f"OK: files={res['files']}\n")
        return 0
    else:
        sys.stderr.write("ERRORS:\n" + "\n".join(str(x) for x in res["issues"]) + "\n")
        return 1


def _world_extract(argv: List[str]) -> int:
    # Extract a structure from a .world by building blockImage+blockKey (requires Pillow)
    p = argparse.ArgumentParser(prog="pystarbound world-extract", description="Extract a structure from a .world (optionally a specific dungeon/area) and write a mod")
    p.add_argument("world", help="Path to .world file")
    p.add_argument("--assets", default=None, help="Path(s) to unpacked assets directory. Use OS path separator to pass multiple roots (e.g. '/A:/B')")
    p.add_argument("-o", "--out-dir", required=True, help="Output mod directory")
    p.add_argument("--mod-id", default=None, help="Mod id (default: derived from world file name)")
    p.add_argument("--mod-name", default="SB World Export", help="Mod friendly name")
    p.add_argument("--dungeon-id", type=int, default=None, help="Only include tiles belonging to this dungeon id")
    p.add_argument("--rect", default=None, help="Crop to rectangle 'x0,y0,x1,y1' (tile coords)")
    p.add_argument("--seed", default=None, help="Seed tile 'x,y' to extract a connected component of occupied tiles")
    p.add_argument("--seed-mode", choices=["any","fg","bg"], default="any", help="Connectivity considers fg, bg, or either (default any)")
    p.add_argument("--pad", type=int, default=0, help="Expand the final bounds by this many tiles on all sides (after selection)")
    p.add_argument("--seed-connectivity", choices=["four","eight"], default="four", help="Connectivity for seed selection (default: four)")
    # Common modgen options we expose here as pass-through
    p.add_argument("--background-overlay", action="store_true", help="Also bake a colored background overlay PNG and reference it in structure")
    p.add_argument("--material-map", default=None, help="JSON file mapping materialId to material name for unknown ids")
    p.add_argument("--objects", action="store_true", help="Also export objects detected in the world")
    p.add_argument("--objects-only-known", action="store_true", help="When exporting objects, keep only those known in provided assets")
    p.add_argument("--objects-log-unknown", default=None, help="When exporting objects, write unknown object names and counts to this JSON")
    p.add_argument("--object-map", default=None, help="JSON file mapping objectName to replacement name (applied before known-only filtering)")
    p.add_argument("--requires-into-metadata", action="store_true", help="Also write a simple 'requires' array into _metadata based on provenance")
    p.add_argument("--report", default=None, help="Write a JSON report with counts and provenance summary to this path")
    p.add_argument("--pack", action="store_true", help="After export, pack the out-dir into a .pak next to it")
    p.add_argument("--pack-out", default=None, help="Explicit output .pak path (non-batch)")
    p.add_argument("--combined-patch", default=None, help="When batching dungeons, write a combined universe_server.config.patch to this path")
    # Filters and positioning
    p.add_argument("--materials-include", default=None, help="Comma-separated material IDs to include (others zeroed)")
    p.add_argument("--materials-exclude", default=None, help="Comma-separated material IDs to exclude (zeroed)")
    p.add_argument("--objects-include", default=None, help="Comma-separated object names to include")
    p.add_argument("--objects-exclude", default=None, help="Comma-separated glob patterns of object names to exclude")
    p.add_argument("--blocks-position", default=None, help="blocksPosition override 'x,y' for structure")
    # Batch dungeons
    p.add_argument("--dungeon-ids", default=None, help="Comma-separated dungeon ids to export (overrides rect/seed selection)")
    p.add_argument("--top-dungeons", type=int, default=None, help="Export top N dungeons by tile count (overrides rect/seed)")
    p.add_argument("--min-tiles", type=int, default=1, help="Minimum tiles for a dungeon to be considered when using --top-dungeons")
    p.add_argument("--species", default="human", help="Species key to patch (default: human)")
    p.add_argument("--all-species", action="store_true", help="Patch all vanilla species")
    p.add_argument("--byos", action="store_true", help="BYOS mode: add BYOS keys instead of replacing vanilla ships")
    p.add_argument("--fu-broken", action="store_true", help="Replace vanilla 'shipengine' with FU 'fu_ftldrivesmall_broken' in exported objects")
    p.add_argument("--ship-tier", type=int, choices=range(0,9), default=8, help="Vanilla override: inject shipUpgrades for this tier (0-8)")
    p.add_argument("--per-tier-structures", action="store_true", help="Vanilla override: generate exported_T0..exported_T8.structure and patch each tier")
    p.add_argument("--thruster-overlays", action="store_true", help="Add simple blue thruster glow overlays by tier (if engine position can be detected)")
    p.add_argument("--ensure-core-objects", action="store_true", help="Ensure core ship objects exist by spawning safe defaults when missing")
    args = p.parse_args(argv)
    try:
        from . import modgen as _modgen_mod
        from .shipworld import load_world_grid, compute_nonzero_bounds, crop_shipworld, extract_component_bounds, apply_mask
        from .shipworld import ShipWorld as _SW
    except Exception:
        sys.stderr.write("Pillow not installed. Install optional extra: pip install 'py-starbound[ship]'\n")
        return 1
    # Base grid (optionally filtered by dungeon id first)
    base = load_world_grid(args.world, dungeon_id=args.dungeon_id)

    # Derive default mod id/name if missing
    def _derive_mod_id() -> str:
        import os
        stem = os.path.splitext(os.path.basename(args.world))[0]
        safe = ''.join(ch if ch.isalnum() or ch in ('-','_') else '_' for ch in stem)
        return (safe or 'export').lower()
    if not args.mod_id:
        args.mod_id = _derive_mod_id()
    # Selection
    sel_bounds: Optional[Tuple[int,int,int,int]] = None
    sel_grid: _SW = base
    # Batch by dungeons takes precedence
    dungeon_list: Optional[List[int]] = None
    if args.dungeon_ids:
        try:
            dungeon_list = [int(x.strip()) for x in args.dungeon_ids.split(',') if x.strip()]
        except Exception:
            sys.stderr.write("Invalid --dungeon-ids. Expected comma-separated integers\n")
            return 2
    elif args.top_dungeons is not None:
        from .shipworld import dungeon_tile_counts
        counts = dungeon_tile_counts(args.world)
        items = [(did, cnt) for did, cnt in counts.items() if cnt >= max(1, args.min_tiles)]
        items.sort(key=lambda x: x[1], reverse=True)
        dungeon_list = [did for did, _ in items[: max(0, args.top_dungeons)]]

    # Rect/seed selection if not batch
    if args.rect and not dungeon_list:
        try:
            x0,y0,x1,y1 = [int(x.strip()) for x in args.rect.split(',')]
            sel_bounds = (x0,y0,x1,y1)
        except Exception:
            sys.stderr.write("Invalid --rect. Expected 'x0,y0,x1,y1'\n")
            return 2
    # Seed component selection
    elif args.seed:
        try:
            sx,sy = [int(x.strip()) for x in args.seed.split(',')]
        except Exception:
            sys.stderr.write("Invalid --seed. Expected 'x,y'\n")
            return 2
        bounds, mask = extract_component_bounds(base, sx, sy, mode=args.seed_mode, connectivity=args.seed_connectivity)
        sel_grid = apply_mask(base, mask)
        sel_bounds = bounds
    # Default: auto-bounds of non-zero tiles
    else:
        sel_bounds = compute_nonzero_bounds(base)
    # Apply padding
    if args.pad and sel_bounds:
        x0,y0,x1,y1 = sel_bounds
        x0 = max(0, x0 - args.pad)
        y0 = max(0, y0 - args.pad)
        x1 = min(base.width - 1, x1 + args.pad)
        y1 = min(base.height - 1, y1 + args.pad)
        sel_bounds = (x0,y0,x1,y1)
    # Crop grid to selection bounds
    # Helper to parse comma lists
    def _parse_int_list(s: Optional[str]) -> Optional[List[int]]:
        if not s:
            return None
        try:
            return [int(x.strip()) for x in s.split(',') if x.strip()]
        except Exception:
            return None
    def _parse_str_list(s: Optional[str]) -> Optional[List[str]]:
        if not s:
            return None
        return [x.strip() for x in s.split(',') if x.strip()]

    mats_inc = _parse_int_list(args.materials_include)
    mats_exc = _parse_int_list(args.materials_exclude)
    objs_inc = _parse_str_list(args.objects_include)
    objs_exc = _parse_str_list(args.objects_exclude)
    blocks_pos = None
    if args.blocks_position:
        try:
            bx, by = [int(x.strip()) for x in args.blocks_position.split(',')]
            blocks_pos = (bx, by)
        except Exception:
            sys.stderr.write("Invalid --blocks-position. Expected 'x,y'\n")
            return 2

    # If batching dungeons, iterate; else single
    if dungeon_list:
        combined_us_patch = []
        for did in dungeon_list:
            grid_d = load_world_grid(args.world, dungeon_id=did)
            ret = _modgen_mod.generate_mod(
                args.world,
                assets_dir=args.assets,
                out_dir=f"{args.out_dir}_{did}",
                mod_id=f"{args.mod_id}_{did}",
                mod_name=f"{args.mod_name} (did {did})",
                background_overlay=args.background_overlay,
                material_map_path=args.material_map,
                include_objects=args.objects,
                objects_only_known=args.objects_only_known,
                objects_log_unknown=args.objects_log_unknown,
                species=args.species,
                all_species=args.all_species,
                byos=args.byos,
                fu_broken=args.fu_broken,
                ship_tier=args.ship_tier,
                per_tier_structures=args.per_tier_structures,
                thruster_overlays=args.thruster_overlays,
                ensure_core_objects=args.ensure_core_objects,
                grid=grid_d,
                objects_bounds=None,
                object_map_path=args.object_map,
                requires_into_metadata=args.requires_into_metadata,
                report_path=args.report,
                materials_include=mats_inc,
                materials_exclude=mats_exc,
                objects_include=objs_inc,
                objects_exclude=objs_exc,
                blocks_position=blocks_pos,
            )
            # Append to combined patch if requested
            if args.combined_patch:
                paths = ret.get("structure_paths", []) if isinstance(ret, dict) else []
                if args.byos:
                    for spc in ([args.species] if not args.all_species else ["human","apex","avian","floran","glitch","hylotl","novakid"]):
                        combined_us_patch.append({"op":"add","path":f"/byosShips/{spc}","value": paths})
                        combined_us_patch.append({"op":"add","path":f"/fu_byosShips/{spc}","value": paths})
                else:
                    for spc in ([args.species] if not args.all_species else ["human","apex","avian","floran","glitch","hylotl","novakid"]):
                        combined_us_patch.append({"op":"add","path":f"/speciesShips/{spc}","value": paths})
        if args.combined_patch and combined_us_patch:
            try:
                import json
                with open(args.combined_patch, 'w') as f:
                    json.dump(combined_us_patch, f, indent=2)
            except Exception as e:
                sys.stderr.write(f"failed to write combined patch: {e}\n")
        if args.pack:
            try:
                from pathlib import Path
                from .sbasset6 import write_sbasset6_from_dir
                for did in dungeon_list:
                    outdir = Path(f"{args.out_dir}_{did}")
                    pack_path = outdir.parent / f"{outdir.name}.pak"
                    write_sbasset6_from_dir(str(outdir), str(pack_path))
                    sys.stdout.write(f"Packed to {pack_path}\n")
            except Exception as e:
                sys.stderr.write(f"pack failed: {e}\n")
                return 1
        return 0

    grid = crop_shipworld(sel_grid, sel_bounds)
    # Generate
    ret = _modgen_mod.generate_mod(
        args.world,
        assets_dir=args.assets,
        out_dir=args.out_dir,
        mod_id=args.mod_id,
        mod_name=args.mod_name,
        background_overlay=args.background_overlay,
        material_map_path=args.material_map,
        include_objects=args.objects,
        objects_only_known=args.objects_only_known,
        objects_log_unknown=args.objects_log_unknown,
        species=args.species,
        all_species=args.all_species,
        byos=args.byos,
        fu_broken=args.fu_broken,
        ship_tier=args.ship_tier,
        per_tier_structures=args.per_tier_structures,
        thruster_overlays=args.thruster_overlays,
        ensure_core_objects=args.ensure_core_objects,
        grid=grid,
        objects_bounds=sel_bounds if args.objects else None,
        object_map_path=args.object_map,
        requires_into_metadata=args.requires_into_metadata,
        report_path=args.report,
        materials_include=mats_inc,
        materials_exclude=mats_exc,
        objects_include=objs_inc,
        objects_exclude=objs_exc,
        blocks_position=blocks_pos,
    )
    # Optional pack
    if args.pack:
        try:
            from pathlib import Path
            from .sbasset6 import write_sbasset6_from_dir
            outdir = Path(args.out_dir)
            pack_path = Path(args.pack_out) if args.pack_out else (outdir.parent / f"{outdir.name}.pak")
            write_sbasset6_from_dir(str(outdir), str(pack_path))
            sys.stdout.write(f"Packed to {pack_path}\n")
        except Exception as e:
            sys.stderr.write(f"pack failed: {e}\n")
            return 1
    return 0


def _world_preview(argv: List[str]) -> int:
    # Render a PNG preview of a selected area from a .world (uses flat colors)
    p = argparse.ArgumentParser(prog="pystarbound world-preview", description="Render a PNG preview of a selected area from a .world")
    p.add_argument("world", help="Path to .world file")
    p.add_argument("-o", "--output", required=True, help="Output PNG path")
    p.add_argument("--assets", default=None, help="Path(s) to unpacked assets directory (optional; improves colors)")
    p.add_argument("--tile-size", type=int, default=8, help="Pixels per tile (default 8)")
    p.add_argument("--textured", action="store_true", help="Experimental: attempt textured preview for materials (fallback to flat colors)")
    p.add_argument("--no-crop", action="store_true", help="Do not crop automatically; render full world extents")
    p.add_argument("-v", "--debug", action="store_true", help="Verbose output about selection and output path")
    p.add_argument("--dungeon-id", type=int, default=None, help="Only include tiles belonging to this dungeon id")
    p.add_argument("--rect", default=None, help="Crop to rectangle 'x0,y0,x1,y1' (tile coords)")
    p.add_argument("--seed", default=None, help="Seed tile 'x,y' to extract a connected component of occupied tiles")
    p.add_argument("--seed-mode", choices=["any","fg","bg"], default="any", help="Connectivity considers fg, bg, or either (default any)")
    p.add_argument("--pad", type=int, default=0, help="Expand the final bounds by this many tiles on all sides (after selection)")
    p.add_argument("--seed-connectivity", choices=["four","eight"], default="four", help="Connectivity for seed selection (default: four)")
    # New options: layers, dungeon overlays, legend
    p.add_argument("--layers", choices=["both","fg","bg"], default="both", help="Which tile layers to render (default both)")
    p.add_argument("--overlay-dungeons", action="store_true", help="Overlay dungeon bounding boxes on the preview")
    p.add_argument("--overlay-dungeon-labels", action="store_true", help="Label dungeon ids when overlaying dungeons")
    p.add_argument("--overlay-objects", action="store_true", help="Overlay object anchor dots inside selection (if any)")
    p.add_argument("--legend", default=None, help="Write a JSON legend mapping used material ids to RGBA colors")
    args = p.parse_args(argv)
    try:
        from .shipworld import load_world_grid, compute_nonzero_bounds, crop_shipworld, extract_component_bounds, apply_mask, ShipWorld as _SW
        from . import render as _render
    except Exception:
        sys.stderr.write("Pillow not installed. Install optional extra: pip install 'py-starbound[ship]'\n")
        return 1
    base = load_world_grid(args.world, dungeon_id=args.dungeon_id)
    # Normalize output path and ensure parent exists
    import os
    out_path = os.path.abspath(args.output)
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.isdir(out_dir):
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            sys.stderr.write(f"Failed to create output directory '{out_dir}': {e}\n")
            return 1
    sel_bounds: Optional[Tuple[int,int,int,int]] = None
    sel_grid: _SW = base
    if args.rect:
        try:
            x0,y0,x1,y1 = [int(x.strip()) for x in args.rect.split(',')]
            sel_bounds = (x0,y0,x1,y1)
        except Exception:
            sys.stderr.write("Invalid --rect. Expected 'x0,y0,x1,y1'\n")
            return 2
    elif args.seed:
        try:
            sx,sy = [int(x.strip()) for x in args.seed.split(',')]
        except Exception:
            sys.stderr.write("Invalid --seed. Expected 'x,y'\n")
            return 2
        bounds, mask = extract_component_bounds(base, sx, sy, mode=args.seed_mode, connectivity=args.seed_connectivity)
        sel_grid = apply_mask(base, mask)
        sel_bounds = bounds
    else:
        sel_bounds = (0,0,base.width-1,base.height-1) if args.no_crop else compute_nonzero_bounds(base)
    if args.pad and sel_bounds:
        x0,y0,x1,y1 = sel_bounds
        x0 = max(0, x0 - args.pad)
        y0 = max(0, y0 - args.pad)
        x1 = min(base.width - 1, x1 + args.pad)
        y1 = min(base.height - 1, y1 + args.pad)
        sel_bounds = (x0,y0,x1,y1)
    grid = crop_shipworld(sel_grid, sel_bounds)

    # Honor --layers by zeroing out unwanted tiles
    if args.layers != "both":
        from copy import deepcopy
        if args.layers == "fg":
            grid = _SW(width=grid.width, height=grid.height, fg=list(grid.fg), bg=[0]*(grid.width*grid.height))
        elif args.layers == "bg":
            grid = _SW(width=grid.width, height=grid.height, fg=[0]*(grid.width*grid.height), bg=list(grid.bg))

    if args.debug:
        sys.stdout.write(f"world-preview: size={base.width}x{base.height} bounds={sel_bounds} tile={args.tile_size} textured={args.textured} layers={args.layers} out={out_path}\n")
    try:
        _render.render_shipworld(args.world, assets_dir=args.assets, out_png=out_path, tile_size=args.tile_size, grid=grid, textured=args.textured)
    except Exception as e:
        sys.stderr.write(f"world-preview failed: {e}\n")
        return 1

    # Optional: overlay dungeons and labels, and/or write legend
    try:
        import os
        if args.overlay_dungeons or args.legend or args.overlay_objects:
            from PIL import Image, ImageDraw, ImageFont
            from .shipworld import dungeon_bounding_boxes, extract_objects
            from .materials import MaterialRegistry
            # Verify output exists and open
            if not os.path.isfile(out_path):
                sys.stderr.write(f"world-preview: output file not found after render: {out_path}\n")
                return 1
            img = Image.open(out_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            font = None
            try:
                from PIL import ImageFont as _IF
                font = _IF.load_default()
            except Exception:
                font = None

            x0,y0,x1,y1 = sel_bounds
            # Overlays
            if args.overlay_dungeons:
                boxes = dungeon_bounding_boxes(args.world)
                # Draw each bbox if it intersects selection
                for did, (bx0,by0,bx1,by1) in boxes.items():
                    # Intersection check
                    if bx1 < x0 or by1 < y0 or bx0 > x1 or by0 > y1:
                        continue
                    # Clamp to selection and shift to local tile coords
                    rx0, ry0 = max(bx0, x0) - x0, max(by0, y0) - y0
                    rx1, ry1 = min(bx1, x1) - x0, min(by1, y1) - y0
                    # Convert to pixel coords (account for y-flip)
                    ts = args.tile_size
                    Ht = grid.height
                    px0 = rx0 * ts
                    py0 = (Ht - 1 - ry1) * ts
                    px1 = (rx1 + 1) * ts - 1
                    py1 = (Ht - 1 - ry0) * ts - 1
                    draw.rectangle([px0, py0, px1, py1], outline=(255,0,0,255))
                    if args.overlay_dungeon_labels:
                        label = str(did)
                        tx = px0 + 2
                        ty = py0 + 2
                        if font:
                            draw.text((tx, ty), label, fill=(255,255,0,255), font=font)
                        else:
                            draw.text((tx, ty), label, fill=(255,255,0,255))
                # Save overlay result back to file
                img.save(out_path)

            # Object dots
            if args.overlay_objects:
                try:
                    objs = extract_objects(args.world)
                    sx0,sy0,sx1,sy1 = sel_bounds
                    ts = args.tile_size
                    Ht = grid.height
                    for o in objs:
                        pos = o.get('position')
                        if isinstance(pos, list) and len(pos) >= 2:
                            ox, oy = int(pos[0]), int(pos[1])
                            if sx0 <= ox <= sx1 and sy0 <= oy <= sy1:
                                lx = (ox - sx0) * ts
                                ly = (Ht - 1 - (oy - sy0)) * ts
                                # Draw a 2x2 bright dot
                                draw.rectangle([lx, ly, lx+1, ly+1], fill=(0,255,0,255))
                except Exception:
                    pass
            # Legend mapping (material id -> RGBA actually used)
            if args.legend:
                try:
                    reg = MaterialRegistry(args.assets)
                    used = sorted(set([m for m in (grid.fg + grid.bg) if 0 < m < 65000]))
                    legend = {str(mid): list(reg.get_color(mid)) for mid in used}
                    with open(args.legend, 'w') as lf:
                        import json
                        json.dump({"materials": legend}, lf, indent=2)
                except Exception:
                    pass
    except Exception as e:
        if args.debug:
            sys.stderr.write(f"world-preview overlay/legend step failed: {e}\n")

    if args.debug:
        sys.stdout.write(f"world-preview: wrote {out_path}\n")
    return 0


def _world_requires(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="pystarbound world-requires", description="Analyze which mods provide materials/objects used by a .world selection")
    p.add_argument("world", help="Path to .world file")
    p.add_argument("--assets", default=None, help="Path(s) to unpacked assets directory. Use OS path separator to pass multiple roots (e.g. '/A:/B')")
    p.add_argument("--dungeon-id", type=int, default=None, help="Only include tiles belonging to this dungeon id")
    p.add_argument("--rect", default=None, help="Crop to rectangle 'x0,y0,x1,y1' (tile coords)")
    p.add_argument("--seed", default=None, help="Seed tile 'x,y' to extract a connected component of occupied tiles")
    p.add_argument("--seed-mode", choices=["any","fg","bg"], default="any", help="Connectivity considers fg, bg, or either (default any)")
    p.add_argument("--pad", type=int, default=0, help="Expand the final bounds by this many tiles on all sides (after selection)")
    p.add_argument("--objects", action="store_true", help="Also analyze objects in the selection (entity regions)")
    p.add_argument("--objects-only-known", action="store_true", help="When analyzing objects, keep only those known in provided assets")
    p.add_argument("--json", action="store_true", help="Output JSON (default: plain list of mod names)")
    args = p.parse_args(argv)
    try:
        from .shipworld import load_world_grid, compute_nonzero_bounds, crop_shipworld, extract_component_bounds, apply_mask
        from .materials import MaterialRegistry, build_provenance
        from .shipworld import extract_objects
    except Exception:
        sys.stderr.write("Pillow not installed. Install optional extra: pip install 'py-starbound[ship]'\n")
        return 1
    # Build selection grid
    base = load_world_grid(args.world, dungeon_id=args.dungeon_id)
    if args.rect:
        try:
            x0,y0,x1,y1 = [int(x.strip()) for x in args.rect.split(',')]
            sel_bounds = (x0,y0,x1,y1)
            sel_grid = base
        except Exception:
            sys.stderr.write("Invalid --rect. Expected 'x0,y0,x1,y1'\n")
            return 2
    elif args.seed:
        try:
            sx,sy = [int(x.strip()) for x in args.seed.split(',')]
        except Exception:
            sys.stderr.write("Invalid --seed. Expected 'x,y'\n")
            return 2
        bounds, mask = extract_component_bounds(base, sx, sy, mode=args.seed_mode)
        sel_grid = apply_mask(base, mask)
        sel_bounds = bounds
    else:
        sel_bounds = compute_nonzero_bounds(base)
        sel_grid = base
    if args.pad and sel_bounds:
        x0,y0,x1,y1 = sel_bounds
        x0 = max(0, x0 - args.pad)
        y0 = max(0, y0 - args.pad)
        x1 = min(base.width - 1, x1 + args.pad)
        y1 = min(base.height - 1, y1 + args.pad)
        sel_bounds = (x0,y0,x1,y1)
    grid = crop_shipworld(sel_grid, sel_bounds)

    # Collect used materials
    used_mats = sorted(set([m for m in (grid.fg + grid.bg) if 0 < m < 65000]))
    reg = MaterialRegistry(args.assets)

    # Build provenance from assets
    prov = build_provenance(args.assets) if args.assets else {"materials": {}, "objects": {}, "mods": []}
    mats_prov = prov.get("materials", {})
    objs_prov = prov.get("objects", {})

    mods = {}
    det_mats = {}
    for mid in used_mats:
        entry = mats_prov.get(mid)
        name = reg.get_name(mid)
        modsrc = entry.get("mod") if entry else None
        det_mats[str(mid)] = {"name": name, "mod": modsrc}
        if modsrc:
            mods[modsrc] = 1

    det_objs = {}
    if args.objects:
        objs = extract_objects(args.world)
        # Filter objects to selection bounds
        x0,y0,x1,y1 = sel_bounds
        filtered = []
        for o in objs:
            pos = o.get("position")
            if isinstance(pos, list) and len(pos) >= 2:
                ox, oy = int(pos[0]), int(pos[1])
                if x0 <= ox <= x1 and y0 <= oy <= y1:
                    filtered.append(o)
        # Optionally restrict to known-only
        if args.objects_only_known and args.assets:
            filtered2 = []
            for o in filtered:
                nm = o.get("name")
                if isinstance(nm, str) and nm in objs_prov:
                    filtered2.append(o)
            filtered = filtered2
        for o in filtered:
            nm = o.get("name")
            if not isinstance(nm, str):
                continue
            entry = objs_prov.get(nm)
            modsrc = entry.get("mod") if entry else None
            det_objs[nm] = {"mod": modsrc}
            if modsrc:
                mods[modsrc] = 1

    result = {"mods": sorted(mods.keys()), "details": {"materials": det_mats, "objects": det_objs}}

    if args.json:
        import json
        sys.stdout.write(json.dumps(result, indent=2) + "\n")
    else:
        if not result["mods"]:
            sys.stdout.write("(no mods detected)\n")
        else:
            for m in result["mods"]:
                sys.stdout.write(m + "\n")
    return 0


def _world_dungeons(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="pystarbound world-dungeons", description="List dungeon ids present in a .world with tile counts")
    p.add_argument("world", help="Path to .world file")
    p.add_argument("--min-tiles", type=int, default=1, help="Only show dungeon ids with at least this many tiles")
    p.add_argument("--json", action="store_true", help="Output JSON instead of plain text")
    p.add_argument("--bbox", action="store_true", help="Include bounding boxes for each dungeon id")
    args = p.parse_args(argv)
    from .shipworld import dungeon_tile_counts, dungeon_bounding_boxes
    counts = dungeon_tile_counts(args.world)
    boxes = dungeon_bounding_boxes(args.world) if args.bbox else {}
    items = [(did, cnt) for did, cnt in counts.items() if cnt >= max(1, args.min_tiles)]
    items.sort(key=lambda x: x[1], reverse=True)
    if args.json:
        import json
        obj = {"dungeons": [{"id": did, "tiles": cnt, "bbox": list(boxes.get(did)) if did in boxes else None} for (did, cnt) in items]}
        sys.stdout.write(json.dumps(obj, indent=2) + "\n")
    else:
        if not items:
            sys.stdout.write("(no dungeons)\n")
        else:
            for did, cnt in items:
                if args.bbox and did in boxes:
                    x0,y0,x1,y1 = boxes[did]
                    sys.stdout.write(f"{did}\t{cnt}\t({x0},{y0})-({x1},{y1})\n")
                else:
                    sys.stdout.write(f"{did}\t{cnt}\n")
    return 0


def _workshop(argv: List[str]) -> int:
    # Workshop utilities: list, info, sync, prepare, pack
    if not argv or argv[0] in ("-h","--help"):
        sys.stdout.write(
            "Usage: pystarbound workshop <list|info|sync|prepare|pack> [options]\n\n"
            "Subcommands:\n"
            "  list     List installed Workshop items for Starbound (211820)\n"
            "  info     Fetch public metadata for item IDs\n"
            "  sync     Copy or symlink contents.pak into Starbound mods dir\n"
            "  prepare  Filter by id/title and symlink/copy into a target dir\n"
            "  pack     Pack a directory into a .pak using SBAsset6\n"
        )
        return 0
    sub, rest = argv[0], argv[1:]
    if sub == "list":
        import argparse
        p = argparse.ArgumentParser(prog="pystarbound workshop list")
        p.add_argument("--steam-dir", default=None, help="Path to Steam base directory (optional)")
        p.add_argument("--appid", type=int, default=211820, help="Steam AppID (default 211820)")
        p.add_argument("--json", action="store_true", help="Output JSON")
        args = p.parse_args(rest)
        try:
            from . import workshop as ws
            items = ws.list_installed(appid=args.appid, steam_dir=args.steam_dir)
            if args.json:
                import json
                sys.stdout.write(json.dumps([i.__dict__ for i in items], indent=2) + "\n")
            else:
                if not items:
                    sys.stdout.write("(no workshop items found)\n")
                else:
                    for it in items:
                        path = it.path if it.path else "(missing contents.pak)"
                        sys.stdout.write(f"{it.id}\t{it.title or ''}\t{path}\n")
            return 0
        except Exception as e:
            sys.stderr.write(f"workshop list failed: {e}\n")
            return 1
    if sub == "info":
        import argparse
        p = argparse.ArgumentParser(prog="pystarbound workshop info")
        p.add_argument("--id", required=True, help="Comma-separated Workshop IDs")
        p.add_argument("--json", action="store_true", help="Output JSON")
        args = p.parse_args(rest)
        try:
            from . import workshop as ws
            ids = [s.strip() for s in args.id.split(',') if s.strip()]
            details = ws.get_metadata(ids)
            if args.json:
                import json
                sys.stdout.write(json.dumps(details, indent=2) + "\n")
            else:
                for d in details:
                    line = f"{d.get('publishedfileid')}\t{d.get('title','')}\t{d.get('file_size','')}\t{d.get('time_updated','')}"
                    sys.stdout.write(line + "\n")
            return 0
        except Exception as e:
            sys.stderr.write(f"workshop info failed: {e}\n")
            return 1
    if sub == "sync":
        import argparse
        p = argparse.ArgumentParser(prog="pystarbound workshop sync")
        p.add_argument("--steam-dir", default=None, help="Path to Steam base directory (optional)")
        p.add_argument("--mods-dir", default=None, help="Destination Starbound mods directory (optional; auto-detected if possible)")
        p.add_argument("--appid", type=int, default=211820, help="Steam AppID (default 211820)")
        p.add_argument("--link", action="store_true", help="Create symlinks instead of copying (falls back to copy if unsupported)")
        p.add_argument("--dry-run", action="store_true", help="Do not write changes; print planned actions")
        args = p.parse_args(rest)
        try:
            from . import workshop as ws
            actions = ws.sync_contents_pak(appid=args.appid, steam_dir=args.steam_dir, mods_dir=args.mods_dir, use_symlink=args.link, dry_run=args.dry_run)
            for a in actions:
                sys.stdout.write(a + "\n")
            return 0
        except Exception as e:
            sys.stderr.write(f"workshop sync failed: {e}\n")
            return 1
    if sub == "prepare":
        import argparse
        p = argparse.ArgumentParser(prog="pystarbound workshop prepare")
        p.add_argument("--steam-dir", default=None, help="Path to Steam base directory (optional)")
        p.add_argument("--appid", type=int, default=211820, help="Steam AppID (default 211820)")
        p.add_argument("--out-dir", required=True, help="Output directory to place selected .pak files")
        p.add_argument("--ids", default=None, help="Comma-separated Workshop IDs to include")
        p.add_argument("--titles", default=None, help="Comma-separated title substrings to include (case-insensitive; uses public metadata)")
        p.add_argument("--titles-file", default=None, help="File with title substrings to include, one per line (case-insensitive)")
        p.add_argument("--only", default=None, help="Comma-separated glob patterns to include (match id or title)")
        p.add_argument("--only-file", default=None, help="File with glob patterns to include; one per line")
        p.add_argument("--exclude", default=None, help="Comma-separated glob patterns to exclude (match id or title)")
        p.add_argument("--exclude-file", default=None, help="File with glob patterns to exclude; one per line")
        p.add_argument("--manifest", default=None, help="Write a manifest JSON of included items to this path")
        p.add_argument("--link", action="store_true", help="Create symlinks instead of copying (falls back to copy if unsupported)")
        p.add_argument("--dry-run", action="store_true", help="Do not write changes; print planned actions")
        args = p.parse_args(rest)
        try:
            from . import workshop as ws
            ids = [s.strip() for s in (args.ids.split(',') if args.ids else []) if s.strip()]
            titles = [s.strip() for s in (args.titles.split(',') if args.titles else []) if s.strip()]
            # Read titles from file if provided
            if args.titles_file:
                try:
                    with open(args.titles_file, 'r') as tf:
                        for line in tf:
                            s = line.strip()
                            if s and not s.startswith('#'):
                                titles.append(s)
                except Exception as e:
                    sys.stderr.write(f"Failed to read --titles-file: {e}\n")
                    return 2
            def read_patterns(path: str) -> list[str]:
                out = []
                with open(path, 'r') as f:
                    for line in f:
                        s = line.strip()
                        if s and not s.startswith('#'):
                            out.append(s)
                return out
            only_pats = [s.strip() for s in (args.only.split(',') if args.only else []) if s.strip()]
            if args.only_file:
                try:
                    only_pats.extend(read_patterns(args.only_file))
                except Exception as e:
                    sys.stderr.write(f"Failed to read --only-file: {e}\n")
                    return 2
            excl_pats = [s.strip() for s in (args.exclude.split(',') if args.exclude else []) if s.strip()]
            if args.exclude_file:
                try:
                    excl_pats.extend(read_patterns(args.exclude_file))
                except Exception as e:
                    sys.stderr.write(f"Failed to read --exclude-file: {e}\n")
                    return 2
            actions = ws.prepare_modset(out_dir=args.out_dir, steam_dir=args.steam_dir, appid=args.appid, ids=ids or None, titles=titles or None, only_patterns=only_pats or None, exclude_patterns=excl_pats or None, use_symlink=args.link, dry_run=args.dry_run)
            for a in actions:
                sys.stdout.write(a + "\n")
            # Optional manifest
            if args.manifest:
                try:
                    from pathlib import Path as _P
                    import json as _json
                    outp = _P(args.out_dir)
                    items = []
                    for fp in sorted(outp.glob('*.pak')):
                        pid = fp.stem
                        items.append({"id": pid, "file": str(fp), "size": fp.stat().st_size})
                    # Try to enrich with titles
                    try:
                        dets = ws.get_metadata([it["id"] for it in items])
                        title_map = {str(d.get('publishedfileid')): d.get('title') for d in dets}
                        for it in items:
                            it["title"] = title_map.get(it["id"]) or None
                    except Exception:
                        pass
                    with open(args.manifest, 'w') as mf:
                        _json.dump({"items": items}, mf, indent=2)
                    sys.stdout.write(f"Wrote manifest {args.manifest}\n")
                except Exception as e:
                    sys.stderr.write(f"Failed to write manifest: {e}\n")
                    return 1
            return 0
        except Exception as e:
            sys.stderr.write(f"workshop prepare failed: {e}\n")
            return 1
    if sub == "pack":
        import argparse
        p = argparse.ArgumentParser(prog="pystarbound workshop pack")
        p.add_argument("--dir", required=True, help="Directory to pack (.pak files inside will be included)")
        p.add_argument("-o", "--out", required=True, help="Output .pak path")
        p.add_argument("--metadata", default=None, help="Optional JSON metadata file for package")
        p.add_argument("--meta", action="append", default=None, help="Inline key=value to add to metadata (repeatable)")
        args = p.parse_args(rest)
        try:
            import json
            meta = {}
            if args.metadata:
                with open(args.metadata, 'r') as jf:
                    meta.update(json.load(jf))
            if args.meta:
                for kv in args.meta:
                    if '=' in kv:
                        k,v = kv.split('=',1)
                        meta[k]=v
            from .sbasset6 import write_sbasset6_from_dir
            write_sbasset6_from_dir(args.dir, args.out, metadata=meta)
            sys.stdout.write(f"Packed to {args.out}\n")
            return 0
        except Exception as e:
            sys.stderr.write(f"workshop pack failed: {e}\n")
            return 1
    if sub == "verify":
        import argparse, json
        p = argparse.ArgumentParser(prog="pystarbound workshop verify")
        p.add_argument("--dir", required=True, help="Directory containing .pak files to verify")
        p.add_argument("--json", action="store_true", help="Output JSON")
        p.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
        args = p.parse_args(rest)
        try:
            from .sbasset6 import verify_sbasset6
            from pathlib import Path
            d = Path(args.dir)
            results = []
            all_ok = True
            for fp in sorted(d.glob("*.pak")):
                res = verify_sbasset6(str(fp))
                entry = {"file": str(fp), **res}
                results.append(entry)
                if not res.get("ok"):
                    all_ok = False
                    if args.fail_fast:
                        break
            if args.json:
                sys.stdout.write(json.dumps(results, indent=2) + "\n")
            else:
                total = len(results)
                fails = sum(1 for r in results if not r.get("ok"))
                for r in results:
                    if r.get("ok"):
                        sys.stdout.write(f"OK: {r['file']} files={r['files']}\n")
                    else:
                        sys.stdout.write(f"FAIL: {r['file']} issues={len(r['issues'])}\n")
                sys.stdout.write(f"Summary: {total} checked, {fails} failed\n")
            return 0 if all_ok else 1
        except Exception as e:
            sys.stderr.write(f"workshop verify failed: {e}\n")
            return 1
    sys.stderr.write(f"Unknown workshop subcommand: {sub}\n")
    return 2


def _csv_from_array(arr: List[int], w: int, h: int) -> str:
    # Row-major from top-left: flip vertically from our bottom-left origin
    rows: List[str] = []
    for yy in range(h - 1, -1, -1):
        base_off = yy * w
        row = arr[base_off: base_off + w]
        rows.append(','.join(str(int(x)) for x in row))
    return '\n'.join(rows)

def _world_export_tiled(argv: List[str]) -> int:
    # Export a selection to a Tiled-like JSON (no tilesets; stores material IDs directly)
    p = argparse.ArgumentParser(prog="pystarbound world-export-tiled", description="Export a .world selection to a Tiled-like JSON (experimental)")
    p.add_argument("world", help="Path to .world file")
    p.add_argument("-o", "--output", required=True, help="Output JSON path")
    p.add_argument("--assets", default=None, help="Path(s) to assets (optional; unused for now)")
    p.add_argument("--dungeon-id", type=int, default=None, help="Only include tiles belonging to this dungeon id")
    p.add_argument("--rect", default=None, help="Crop to rectangle 'x0,y0,x1,y1' (tile coords)")
    p.add_argument("--seed", default=None, help="Seed tile 'x,y' to extract a connected component of occupied tiles")
    p.add_argument("--seed-mode", choices=["any","fg","bg"], default="any", help="Connectivity considers fg, bg, or either (default any)")
    p.add_argument("--pad", type=int, default=0, help="Expand the final bounds by this many tiles on all sides (after selection)")
    p.add_argument("--seed-connectivity", choices=["four","eight"], default="four", help="Connectivity for seed selection (default: four)")
    p.add_argument("--layers", choices=["both","fg","bg"], default="both", help="Which layers to export (default both)")
    args = p.parse_args(argv)
    try:
        from .shipworld import load_world_grid, compute_nonzero_bounds, crop_shipworld, extract_component_bounds, apply_mask, ShipWorld as _SW
    except Exception as e:
        sys.stderr.write(f"failed to load world utils: {e}\n")
        return 1
    # Build selection
    base = load_world_grid(args.world, dungeon_id=args.dungeon_id)
    sel_bounds: Optional[Tuple[int,int,int,int]] = None
    sel_grid: _SW = base
    if args.rect:
        try:
            x0,y0,x1,y1 = [int(x.strip()) for x in args.rect.split(',')]
            sel_bounds = (x0,y0,x1,y1)
        except Exception:
            sys.stderr.write("Invalid --rect. Expected 'x0,y0,x1,y1'\n")
            return 2
    elif args.seed:
        try:
            sx,sy = [int(x.strip()) for x in args.seed.split(',')]
        except Exception:
            sys.stderr.write("Invalid --seed. Expected 'x,y'\n")
            return 2
        bounds, mask = extract_component_bounds(base, sx, sy, mode=args.seed_mode, connectivity=args.seed_connectivity)
        sel_grid = apply_mask(base, mask)
        sel_bounds = bounds
    else:
        sel_bounds = compute_nonzero_bounds(base)
    if args.pad and sel_bounds:
        x0,y0,x1,y1 = sel_bounds
        x0 = max(0, x0 - args.pad)
        y0 = max(0, y0 - args.pad)
        x1 = min(base.width - 1, x1 + args.pad)
        y1 = min(base.height - 1, y1 + args.pad)
        sel_bounds = (x0,y0,x1,y1)
    grid = crop_shipworld(sel_grid, sel_bounds)
    # Honor --layers
    if args.layers != "both":
        if args.layers == "fg":
            grid = _SW(width=grid.width, height=grid.height, fg=list(grid.fg), bg=[0]*(grid.width*grid.height))
        elif args.layers == "bg":
            grid = _SW(width=grid.width, height=grid.height, fg=[0]*(grid.width*grid.height), bg=list(grid.bg))
    # Build Tiled-like JSON (CSV encoding with material IDs; tilesets empty)
    import json, os
    out_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    layers = []
    layers.append({
        "type": "tilelayer",
        "name": "bg",
        "width": grid.width,
        "height": grid.height,
        "encoding": "csv",
        "data": _csv_from_array(grid.bg, grid.width, grid.height),
    })
    layers.append({
        "type": "tilelayer",
        "name": "fg",
        "width": grid.width,
        "height": grid.height,
        "encoding": "csv",
        "data": _csv_from_array(grid.fg, grid.width, grid.height),
    })
    x0,y0,x1,y1 = sel_bounds
    obj = {
        "type": "map",
        "tiledversion": "1.10.0",
        "orientation": "orthogonal",
        "renderorder": "right-down",
        "width": grid.width,
        "height": grid.height,
        "tilewidth": 1,
        "tileheight": 1,
        "infinite": False,
        "tilesets": [],
        "layers": layers,
        "properties": {
            "format": "SB-Tiled-JSON-Experimental",
            "worldSelection": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
            "materialIdSemantics": "GIDs are material ids; tilesets omitted",
        },
    }
    with open(out_path, 'w') as f:
        json.dump(obj, f, indent=2)
    sys.stdout.write(f"wrote {out_path}\n")
    return 0

def _dungeon_index(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="pystarbound dungeon-index", description="Scan assets for dungeon/ship parts and write a basic index (experimental)")
    p.add_argument("--assets", required=True, help="Path(s) to assets directories (use OS path separator to pass multiple roots)")
    p.add_argument("--out", required=True, help="Output directory (index.json written here)")
    p.add_argument("--format", choices=["json","csv"], default="json", help="Output format (default json)")
    args = p.parse_args(argv)
    import os, json, csv
    from pathlib import Path
    roots = [Path(r) for r in str(args.assets).split(os.pathsep) if r]
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    entries = []
    for root in roots:
        if not root.exists():
            continue
        # .structure
        for fp in root.rglob("*.structure"):
            try:
                data = json.loads(fp.read_text())
                rel = fp.relative_to(root).as_posix()
                obj = {
                    "path": "/" + rel,
                    "type": "structure",
                    "blockImage": data.get("blockImage"),
                    "objects": len(data.get("objects", [])) if isinstance(data.get("objects"), list) else 0,
                }
                entries.append(obj)
            except Exception:
                rel = fp.relative_to(root).as_posix()
                entries.append({"path": "/" + rel, "type": "structure"})
        # .dungeon (list only)
        for fp in root.rglob("*.dungeon"):
            rel = fp.relative_to(root).as_posix()
            entries.append({
                "path": "/" + rel,
                "type": "dungeon",
            })
        # Tiled parts (tmx/json/png under dungeons/)
        for fp in root.rglob("dungeons/*"):
            pass
    if args.format == "json":
        with open(outdir/"index.json", 'w') as f:
            json.dump({"entries": entries}, f, indent=2)
    else:
        with open(outdir/"index.csv", 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(["path","type","blockImage","objects"])
            for e in entries:
                w.writerow([e.get("path"), e.get("type"), e.get("blockImage"), e.get("objects")])
    sys.stdout.write(f"indexed {len(entries)} entries into {outdir}\n")
    return 0

def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = list(sys.argv[1:])
    if not argv or argv[0] in ("-h", "--help"):
        msg = (
            "Usage: pystarbound <command> [options]\n\n"
            "Commands:\n"
            "  export        Extract files from a .pak/.modpak (add --list to list without extracting)\n"
            "  publish       Create a .pak from a directory\n"
            "  verify        Verify SBAsset6 integrity\n"
            "  region        Print world region info\n"
            "  repair        Repair .fail world files\n"
            "  vjson-dump    Dump SBVJ01 to JSON\n"
            "  vjson-make    Create SBVJ01 from JSON\n"
            "  vjson-edit    Edit SBVJ01 using dotted-path assignments (experimental)\n"
            "  player-info   Show basic info from a .player SBVJ01 file\n"
            "  render        Render a shipworld to PNG (requires Pillow)\n"
            "  modgen        Generate a ship mod from a shipworld (requires Pillow)\n"
            "  world-extract Extract a structure from a .world (requires Pillow)\n"
            "  world-preview Render a PNG preview of a .world selection (requires Pillow)\n"
            "  world-dungeons List dungeon ids in a .world (tile counts)\n"
            "  world-requires Analyze which mods provide materials/objects in a .world selection\n"
            "  detect-install Detect Starbound install/mods/workshop dirs (Steam)\n"
            "  workshop      List/info/sync/prepare/pack/verify Workshop mods (no login; optional vdf dep)\n"
            "  world-export-tiled Export a selection to a Tiled-like JSON (experimental)\n"
        )
        sys.stdout.write(msg)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "export":
        if "--list" in rest:
            return _export_list(rest)
        return _delegate_to("starbound.cliexport", rest)
    if cmd == "region":
        return _delegate_to("starbound.cliregion", rest)
    if cmd == "repair":
        return _delegate_to("starbound.clirepair", rest)
    if cmd == "render":
        return _render(rest)
    if cmd == "modgen":
        return _modgen(rest)
    if cmd == "publish":
        return _asset_pack(rest)
    if cmd == "vjson-dump":
        return _vjson_dump(rest)
    if cmd == "vjson-make":
        return _vjson_make(rest)
    if cmd == "vjson-edit":
        return _vjson_edit(rest)
    if cmd == "player-info":
        return _player_info(rest)
    if cmd == "verify":
        return _verify(rest)
    if cmd == "world-extract":
        return _world_extract(rest)
    if cmd == "world-preview":
        return _world_preview(rest)
    if cmd == "world-dungeons":
        return _world_dungeons(rest)
    if cmd == "world-requires":
        return _world_requires(rest)
    if cmd == "workshop":
        return _workshop(rest)
    if cmd == "detect-install":
        return _detect_install(rest)
    if cmd == "world-export-tiled":
        return _world_export_tiled(rest)
    if cmd == "dungeon-index":
        return _dungeon_index(rest)
    sys.stderr.write(f"Unknown command: {cmd}\n")
    return 2
