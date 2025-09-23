from __future__ import annotations

import json
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Optional

from tqdm import tqdm

from .discover import discover_manpaths, list_manfiles
from .render import render_candidate
from .utils import atomic_write


DEFAULT_CACHE = ".man2text_cache.json"


def _worker_render(args):
    '''
     helper to be picklable by ProcessPoolExecutor
    '''
    src, out_dir, timeout = args
    from pathlib import Path
    from .render import render_candidate

    src = Path(src)
    ok, text_or_err, method = render_candidate(src, timeout=timeout)
    if ok:
        # derive section and name
        name = src.name
        for ext in (".gz", ".bz2", ".xz"):
            if name.lower().endswith(ext):
                name = name[: -len(ext)]
                break
        section = None
        if "." in name:
            idx = name.rfind(".")
            candidate = name[idx + 1 :]
            if candidate and candidate[0].isdigit():
                section = candidate
                name = name[:idx]
        if section is None:
            section = "unknown"
        out_path = Path(out_dir) / section / f"{name}.txt"
        atomic_write(str(out_path), text_or_err)
        return (str(src), True, str(out_path), method, None)
    else:
        return (str(src), False, None, method, text_or_err)


def convert_all(
    output_dir: str | Path = "man-txt",
    workers: int | None = None,
    resume: bool = True,
    timeout: int = 30,
    sections: Optional[List[str]] = None,
) -> dict:
    """Discover and convert man pages.

    `sections` is an optional list of section strings (e.g. ['1','3']). If provided,
    only manfiles whose inferred section matches will be processed.

    Returns a summary dict with counts and details.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manpaths = discover_manpaths()
    manfiles = list_manfiles(manpaths)

    if workers is None:
        workers = max(1, (os.cpu_count() or 2) - 1)

    cache_path = output_dir / DEFAULT_CACHE
    processed = set()
    if resume and cache_path.exists():
        try:
            with open(cache_path, "r") as f:
                processed = set(json.load(f).get("processed", []))
        except Exception:
            processed = set()

    tasks = []
    for p in manfiles:
        # derive section to allow filtering
        name = p.name
        for ext in (".gz", ".bz2", ".xz"):
            if name.lower().endswith(ext):
                name = name[: -len(ext)]
                break
        section = None
        if "." in name:
            idx = name.rfind(".")
            cand = name[idx + 1 :]
            if cand and cand[0].isdigit():
                section = cand
        if sections and section not in sections:
            continue
        if str(p) in processed:
            continue
        tasks.append((str(p), str(output_dir), timeout))

    results = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_worker_render, t): t for t in tasks}
        
        progress_iterator = tqdm(as_completed(futures), total=len(tasks), desc="Converting man pages")
        
        for fut in progress_iterator:
            try:
                res = fut.result()
            except Exception as exc:
                results.append((None, False, None, "error", str(exc)))
            else:
                results.append(res)
                if res[1]: # if conversion was successful
                    processed.add(res[0])
                    try:
                        with open(cache_path, "w") as f:
                            json.dump({"processed": list(processed)}, f)
                    except Exception:
                        pass

    summary = {
        "total_found": len(manfiles),
        "attempted": len(tasks),
        "success": sum(1 for r in results if r[1]),
        "failed": sum(1 for r in results if not r[1]),
        "details": results,
    }
    return summary
