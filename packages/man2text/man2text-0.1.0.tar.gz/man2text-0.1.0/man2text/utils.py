import os
import shutil
import tempfile

def atomic_write(path: str | bytes, data: str | bytes, mode: str = 'w') -> None:
    """Atomically write `data` to `path`."""
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dirpath)
    try:
        with os.fdopen(fd, mode) as f:
            f.write(data)
        shutil.move(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
            