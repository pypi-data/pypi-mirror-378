from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import os
import re
import shutil
import json
import urllib.parse
import urllib.request


@dataclass
class WorkshopItem:
    id: str
    title: Optional[str]
    path: Optional[str]  # path to contents.pak if present


# Default Steam base directories per platform
_DEF_STEAM_DIRS = [
    # macOS
    os.path.expanduser('~/Library/Application Support/Steam'),
    # Linux
    os.path.expanduser('~/.local/share/Steam'),
    os.path.expanduser('~/.steam/steam'),  # some distros symlink here
    # Windows (common default)
    os.path.expandvars(r'%ProgramFiles(x86)%/Steam').replace('\\','/'),
]


def _read_libraryfolders(steam_dir: Path) -> List[Path]:
    """Return a list of Steam library roots by reading libraryfolders.vdf when possible.
    Falls back to [steam_dir] only when parsing fails or file missing.
    """
    vdf_path = steam_dir / 'steamapps' / 'libraryfolders.vdf'
    roots: List[Path] = []
    if vdf_path.is_file():
        try:
            # Try using the optional 'vdf' package if available
            try:
                import vdf  # type: ignore
                data = vdf.load(open(vdf_path, 'r', encoding='utf-8', errors='ignore'))
                libs = data.get('libraryfolders') or data.get('LibraryFolders') or {}
                for k, v in libs.items():
                    if isinstance(v, dict) and 'path' in v:
                        roots.append(Path(v['path']))
                    elif isinstance(v, str):
                        roots.append(Path(v))
            except Exception:
                # Fallback: simple regex-based extraction of path lines
                txt = open(vdf_path, 'r', encoding='utf-8', errors='ignore').read()
                for m in re.finditer(r'"path"\s+"([^"]+)"', txt):
                    roots.append(Path(m.group(1)))
        except Exception:
            pass
    if not roots:
        roots = [steam_dir]
    # Ensure main steam_dir first
    uniq = []
    seen = set()
    for r in [steam_dir] + roots:
        p = str(Path(r))
        if p not in seen:
            seen.add(p)
            uniq.append(Path(r))
    return uniq


def find_workshop_dir(appid: int = 211820, steam_dir: Optional[str] = None) -> Optional[Path]:
    """Return the workshop content dir for appid, if found."""
    cand_dirs = []
    if steam_dir:
        cand_dirs.append(Path(steam_dir))
    for d in _DEF_STEAM_DIRS:
        if d and os.path.isdir(d):
            cand_dirs.append(Path(d))
    for sdir in cand_dirs:
        for lib in _read_libraryfolders(sdir):
            p = lib / 'steamapps' / 'workshop' / 'content' / str(appid)
            if p.is_dir():
                return p
    return None


def find_mods_dir(appid: int = 211820, steam_dir: Optional[str] = None) -> Optional[Path]:
    """Return the Starbound mods dir if found via Steam libraries."""
    cand_dirs = []
    if steam_dir:
        cand_dirs.append(Path(steam_dir))
    for d in _DEF_STEAM_DIRS:
        if d and os.path.isdir(d):
            cand_dirs.append(Path(d))
    for sdir in cand_dirs:
        for lib in _read_libraryfolders(sdir):
            p = lib / 'steamapps' / 'common' / 'Starbound' / 'mods'
            if p.is_dir():
                return p
    return None


def find_install_dir(appid: int = 211820, steam_dir: Optional[str] = None) -> Optional[Path]:
    """Return the Starbound install dir if found via Steam libraries."""
    cand_dirs = []
    if steam_dir:
        cand_dirs.append(Path(steam_dir))
    for d in _DEF_STEAM_DIRS:
        if d and os.path.isdir(d):
            cand_dirs.append(Path(d))
    for sdir in cand_dirs:
        for lib in _read_libraryfolders(sdir):
            p = lib / 'steamapps' / 'common' / 'Starbound'
            if p.is_dir():
                return p
    return None


def list_installed(appid: int = 211820, steam_dir: Optional[str] = None) -> List[WorkshopItem]:
    """List installed workshop items (folders under workshop/content/appid)."""
    base = find_workshop_dir(appid=appid, steam_dir=steam_dir)
    items: List[WorkshopItem] = []
    if not base:
        return items
    for child in sorted(base.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        pak = child / 'contents.pak'
        title = None
        # try to fetch title from steam meta .acf next to the folder (optional, best-effort)
        # We avoid network calls; metadata is optional here.
        items.append(WorkshopItem(id=child.name, title=title, path=str(pak) if pak.is_file() else None))
    return items


def get_metadata(ids: List[str]) -> List[Dict[str, Any]]:
    """Fetch Workshop metadata via public Web API (no key required).
    Returns a list of detail dicts.
    """
    if not ids:
        return []
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
    data = {"itemcount": str(len(ids))}
    for i, pid in enumerate(ids):
        data[f"publishedfileids[{i}]"] = str(pid)
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode("utf-8"))
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read()
    obj = json.loads(raw.decode("utf-8"))
    details = obj.get("response", {}).get("publishedfiledetails", [])
    return details


def sync_contents_pak(appid: int = 211820, steam_dir: Optional[str] = None, mods_dir: Optional[str] = None, *, use_symlink: bool = False, dry_run: bool = False) -> List[str]:
    """Copy or symlink workshop contents.pak files into the Starbound mods directory.
    Returns a list of action strings performed/planned.
    """
    actions: List[str] = []
    wdir = find_workshop_dir(appid=appid, steam_dir=steam_dir)
    if not wdir:
        raise RuntimeError("Workshop directory not found. Specify --steam-dir if needed.")
    mdir = Path(mods_dir) if mods_dir else find_mods_dir(appid=appid, steam_dir=steam_dir)
    if not mdir:
        raise RuntimeError("Starbound mods directory not found. Specify --mods-dir explicitly.")
    mdir.mkdir(parents=True, exist_ok=True)
    for child in sorted(wdir.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        src = child / 'contents.pak'
        if not src.is_file():
            actions.append(f"skip {child.name}: contents.pak missing")
            continue
        dst = mdir / f"{child.name}.pak"
        if dst.exists():
            # If already correct size, skip silently
            try:
                if dst.stat().st_size == src.stat().st_size:
                    actions.append(f"ok {dst} (up-to-date)")
                    continue
            except Exception:
                pass
        if dry_run:
            actions.append(("link" if use_symlink else "copy") + f" {src} -> {dst}")
            continue
        try:
            if use_symlink:
                try:
                    if dst.exists() or dst.is_symlink():
                        try:
                            dst.unlink()
                        except Exception:
                            pass
                    os.symlink(os.fspath(src), os.fspath(dst))
                    actions.append(f"linked {dst}")
                    continue
                except Exception:
                    # fallback to copy
                    pass
            # Copy
            shutil.copy2(os.fspath(src), os.fspath(dst))
            actions.append(f"copied {dst}")
        except Exception as e:
            actions.append(f"error {dst}: {e}")
    return actions


def prepare_modset(out_dir: str, *, steam_dir: Optional[str] = None, appid: int = 211820, ids: Optional[List[str]] = None, titles: Optional[List[str]] = None, only_patterns: Optional[List[str]] = None, exclude_patterns: Optional[List[str]] = None, use_symlink: bool = False, dry_run: bool = False) -> List[str]:
    """Prepare a filtered modset by copying/symlinking selected workshop contents.pak into out_dir.
    Filters by explicit ids and/or title substrings (case-insensitive). Title matching uses public metadata.
    Additional filters: only_patterns/exclude_patterns (glob) apply to id or title (case-insensitive).
    """
    import fnmatch
    actions: List[str] = []
    base = find_workshop_dir(appid=appid, steam_dir=steam_dir)
    if not base:
        raise RuntimeError("Workshop directory not found")
    outp = Path(out_dir)
    outp.mkdir(parents=True, exist_ok=True)
    installed = [p for p in sorted(base.iterdir(), key=lambda p: p.name) if p.is_dir()]
    want_ids: Optional[set[str]] = set(ids) if ids else None
    want_titles: Optional[List[str]] = [t.lower() for t in titles] if titles else None
    only_pats = [s.lower() for s in (only_patterns or [])]
    excl_pats = [s.lower() for s in (exclude_patterns or [])]

    # Gather title metadata if needed
    need_titles = bool(want_titles or only_pats or excl_pats)
    meta_map: Dict[str, str] = {}
    if need_titles:
        try:
            dets = get_metadata([p.name for p in installed])
            for d in dets:
                pid = str(d.get('publishedfileid'))
                title = d.get('title') or ''
                if pid:
                    meta_map[pid] = title
        except Exception:
            # Fallback to empty titles
            meta_map = {}

    def pat_match(pid: str, title: str, pats: List[str]) -> bool:
        lid = pid.lower()
        lt = (title or '').lower()
        for pat in pats:
            if fnmatch.fnmatch(lid, pat) or fnmatch.fnmatch(lt, pat):
                return True
        return False

    def select(pid: str) -> bool:
        title = meta_map.get(pid, '')
        # Explicit IDs filter
        if want_ids is not None and pid not in want_ids:
            return False
        # Title substring filter
        if want_titles is not None:
            lt = title.lower()
            if not any(t in lt for t in want_titles):
                return False
        # Only/exclude patterns
        if only_pats and not pat_match(pid, title, only_pats):
            return False
        if excl_pats and pat_match(pid, title, excl_pats):
            return False
        # If no filters provided, allow all
        if not (want_ids or want_titles or only_pats or excl_pats):
            return True
        return True

    for child in installed:
        pid = child.name
        if not select(pid):
            continue
        src = child / 'contents.pak'
        if not src.is_file():
            actions.append(f"skip {pid}: contents.pak missing")
            continue
        dst = outp / f"{pid}.pak"
        if dry_run:
            actions.append(("link" if use_symlink else "copy") + f" {src} -> {dst}")
            continue
        try:
            if use_symlink:
                try:
                    if dst.exists() or dst.is_symlink():
                        try:
                            dst.unlink()
                        except Exception:
                            pass
                    os.symlink(os.fspath(src), os.fspath(dst))
                    actions.append(f"linked {dst}")
                    continue
                except Exception:
                    pass
            shutil.copy2(os.fspath(src), os.fspath(dst))
            actions.append(f"copied {dst}")
        except Exception as e:
            actions.append(f"error {dst}: {e}")
    return actions
