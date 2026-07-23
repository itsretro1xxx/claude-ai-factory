"""Central entry point for the AI Factory.

Each room (etsy-print-on-demand, youtube-shorts-automation, ...) is a
self-contained pipeline with its own run.py and its own README checklist.
This just dispatches to the room you ask for and forwards any extra
arguments to that room's script unchanged — it doesn't import across rooms,
so each one stays independently runnable.

Usage:
    python -m factory.main etsy --audience "plant-obsessed cat owners" --theme gifts --count 5
    python -m factory.main youtube
    python -m factory.main --help
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

ROOMS = {
    "etsy": REPO_ROOT / "etsy-print-on-demand",
    "youtube": REPO_ROOT / "youtube-shorts-automation",
}


def main() -> None:
    # Dispatch by hand rather than with argparse: argparse's built-in -h/--help
    # would intercept `factory etsy --help` before it reaches the room's own
    # script, instead of forwarding it. Only the bare top-level invocation
    # gets factory's own help text; everything after the room name is passed
    # through to that room's run.py untouched.
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        print(f"Available rooms: {', '.join(sorted(ROOMS))}")
        sys.exit(0 if argv else 1)

    room, *room_args = argv
    if room not in ROOMS:
        print(f"Unknown room '{room}'. Available rooms: {', '.join(sorted(ROOMS))}")
        sys.exit(1)

    room_dir = ROOMS[room]
    run_script = room_dir / "run.py"

    if not run_script.exists():
        readme = room_dir / "README.md"
        print(f"'{room}' has no automated pipeline yet.")
        print(f"See {readme.relative_to(REPO_ROOT)} for its manual-pass checklist.")
        sys.exit(1)

    result = subprocess.run([sys.executable, str(run_script), *room_args], cwd=room_dir)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
