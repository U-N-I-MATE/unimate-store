"""Paths for the code-pack tests of unimate.zalo, and server/ of UNI MATE on sys.path.

The plugins in this pack run INSIDE a UNI MATE server and import its modules (`zalo_cli`, `image_gen`,
`image_vision`, `conversations`), so their tests need a UNI MATE checkout next to this repo. CI clones it;
locally point UNIMATE_OS_DIR at yours (default: ../UNI-MATE next to this repo).

    UNIMATE_OS_DIR=/path/to/UNI-MATE python tests/unimate.zalo/test_zalo_read_images.py
"""
import os
import sys
from pathlib import Path

STORE = Path(__file__).resolve().parents[2]
PACK = STORE / "packs" / "unimate.zalo"
ROOT = Path(os.environ.get("UNIMATE_OS_DIR") or (STORE.parent / "UNI-MATE")).resolve()
SERVER = ROOT / "server"
if not (SERVER / "zalo_cli.py").is_file():
    raise SystemExit(f"UNI MATE checkout not found at {ROOT} (set UNIMATE_OS_DIR)")
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))
