from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import List, Iterable


SECTION_DIR_RE = re.compile(r'^man(\d|n|0p|[1-8].*)')


def manpath_from_man() -> List[str]:
    """Try `manpath` or `man -w` to get the active manpath list."""
    candidates = []
    for cmd in (("manpath",), ("man", "-w")):
        try:
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
            if out:
                # manpath typically returns colon-separated
                parts = out.split(os.pathsep)
                for p in parts:
                    if p:
                        candidates.append(p)
                break
        except Exception:
            continue
    return candidates


def parse_man_db_conf(conf_path: Path = Path('/etc/man_db.conf')) -> List[str]:
    if not conf_path.exists():
        return []
    paths = []
    try:
        for line in conf_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('MANDATORY_MANPATH'):
                parts = line.split()
                if len(parts) >= 2:
                    paths.append(parts[1])
            elif line.startswith('MANDB_MAP'):
                parts = line.split()
                if len(parts) >= 2:
                    paths.append(parts[1])
    except Exception:
        return []
    return paths


DEFAULT_MANPATHS = [
    '/usr/share/man',
    '/usr/local/share/man',
    '/usr/man',
    '/usr/local/man',
    '/opt/man',
    '/var/lib/snapd/snap/man',
    '/usr/X11R6/man',
]


def discover_manpaths() -> List[Path]:
    """Return a deduplicated, ordered list of manpath directories (Path)."""
    seen = []
    def add(p: str):
        p = os.path.expanduser(p)
        if p and p not in seen:
            seen.append(p)

    # 1. From man / manpath
    for p in manpath_from_man():
        add(p)

    # 2. From config
    for p in parse_man_db_conf():
        add(p)

    # 3. defaults
    for p in DEFAULT_MANPATHS:
        add(p)

    # normalize to Path and keep only existing paths
    result = [Path(p) for p in seen if Path(p).exists()]
    return result


def section_dirs(manpath: Path) -> Iterable[Path]:
    """Yield section directories inside a manpath (English-only selection)."""
    if not manpath.exists():
        return
    for child in manpath.iterdir():
        if child.is_dir() and SECTION_DIR_RE.match(child.name):
            yield child


def list_manfiles(manpaths: List[Path]) -> List[Path]:
    """List candidate manfiles under section dirs, including compressed files.

    Returns a list of Path objects to files like 'ls.1.gz', 'open.2.xz', or plain 'intro.1'.
    """
    files = []
    seen = set()
    for mp in manpaths:
        for sd in section_dirs(mp):
            for path in sd.rglob('*'):
                if path.is_file():
                    # include compressed or uncompressed man files
                    if path.suffix in ('.gz', '.bz2', '.xz') or re.search(r'\.\d', path.name):
                        real = path.resolve()
                        if real in seen:
                            continue
                        seen.add(real)
                        files.append(path)
    return files
