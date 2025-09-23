import argparse
import sys
from pathlib import Path

from .core import convert_all


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="man2text",
        description="Convert system man pages to plain text files.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="man-txt",
        help="Output directory for txt files (default: man-txt/)",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=None,
        help="Number of worker processes (default: CPU count - 1)",
    )
    parser.add_argument(
        "-s",
        "--sections",
        nargs="+",
        help="Restrict to specific man sections (e.g., 1 3 5)",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Do not resume from cache; reprocess everything",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout (in seconds) for each render attempt (default: 30)",
    )

    args = parser.parse_args(argv)

    summary = convert_all(
        output_dir=Path(args.output),
        workers=args.jobs,
        resume=not args.no_resume,
        timeout=args.timeout,
        sections=args.sections,
    )

    print("Summary:")
    print(f"  Total found: {summary['total_found']}")
    print(f"  Attempted:   {summary['attempted']}")
    print(f"  Success:     {summary['success']}")
    print(f"  Failed:      {summary['failed']}")

    if summary["failed"]:
        print("\nSome pages failed to convert. See details in summary['details'].")

    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
