from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Tuple, Optional


def run_col(input_text: str, timeout: int = 30) -> str:
    """Run the `col -bx` filter on the provided text and return the result."""
    proc = subprocess.run(
        ["col", "-bx"],
        input=input_text,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.stdout


def render_with_man(name: str, section: Optional[str] = None, timeout: int = 30) -> Tuple[bool, str]:
    """Attempt to render a manpage using the `man` command."""
    cmd = ["man"]
    if section:
        cmd.append(section)
    cmd.append(name)
    try:
        env = os.environ.copy()
        env["LC_ALL"] = "C"
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=timeout)
        if proc.returncode == 0 and proc.stdout:
            return True, run_col(proc.stdout, timeout=timeout)
        return False, (proc.stderr or proc.stdout or f"man returned {proc.returncode}")
    except FileNotFoundError as exc:
        return False, f"man not found: {exc}"
    except Exception as exc:
        return False, str(exc)


def _decompress_bytes(path: Path) -> bytes:
    """Return the decompressed bytes for the given path using stdlib modules."""
    import gzip
    import bz2
    import lzma

    if not path.exists():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()
    if suffix == ".gz":
        with gzip.open(path, "rb") as f:
            return f.read()
    if suffix == ".bz2":
        with bz2.open(path, "rb") as f:
            return f.read()
    if suffix == ".xz":
        with lzma.open(path, "rb") as f:
            return f.read()
    return path.read_bytes()


def decompress_and_groff(path: Path, timeout: int = 30) -> Tuple[bool, str]:
    """Decompress `path` and try to format with `groff`."""
    try:
        data = _decompress_bytes(path)
    except Exception as exc:
        return False, f"decompress failed: {exc}"

    env = os.environ.copy()
    env["LC_ALL"] = "C"

    last_err = ""
    for macro in ("-mandoc", "-mdoc"):
        try:
            p = subprocess.run(
                ["groff", macro, "-Tutf8"],
                input=data,
                capture_output=True,
                timeout=timeout,
                env=env,
            )
            if p.returncode == 0 and p.stdout:
                text = p.stdout.decode("utf-8", errors="replace")
                return True, run_col(text, timeout=timeout)
            last_err = (
                p.stderr.decode("utf-8", errors="replace")
                if p.stderr
                else f"groff exit {p.returncode}"
            )
        except FileNotFoundError:
            return False, "groff not found on system"
        except Exception as exc:
            last_err = str(exc)
            continue

    return False, f"groff failed: {last_err}"


def _extract_name_section_from_path(path: Path) -> Tuple[str, Optional[str]]:
    """Given a manfile path, return `(name, section)`."""
    name = path.name
    for ext in (".gz", ".bz2", ".xz"):
        if name.lower().endswith(ext):
            name = name[: -len(ext)]
            break
    if "." in name:
        idx = name.rfind(".")
        candidate = name[idx + 1 :]
        if candidate and candidate[0].isdigit():
            return name[:idx], candidate
    return name, None


def render_candidate(path: Path, timeout: int = 30) -> Tuple[bool, str, str]:
    """Render a candidate man file."""
    path = Path(path)
    name, section = _extract_name_section_from_path(path)

    ok, out = render_with_man(name, section=section, timeout=timeout)
    if ok:
        return True, out, "man"

    if section is not None:
        ok2, out2 = render_with_man(name, section=None, timeout=timeout)
        if ok2:
            return True, out2, "man"

    ok3, out3 = decompress_and_groff(path, timeout=timeout)
    if ok3:
        return True, out3, "groff"

    err_msg = f"man: {out}; groff: {out3 if 'out3' in locals() else 'unknown'}"
    return False, err_msg, "error"
