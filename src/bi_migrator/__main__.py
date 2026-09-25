import argparse
from pathlib import Path

from src.bi_migrator.analyzer import (
    analyze_tableau_file,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="BI Migrator"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a Tableau workbook.",
    )

    analyze_parser.add_argument(
        "input",
        help="Path to a .twb or .twbx file.",
    )

    analyze_parser.add_argument(
        "--output",
        default="out",
        help="Output directory.",
    )

    args = parser.parse_args()

    if args.command == "analyze":

        input_path = Path(args.input)
        output_dir = Path(args.output)

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            output_dir / "migration.json"
        )

        result = analyze_tableau_file(
            input_path,
            output_path,
        )

        print(
            f"Migration JSON: {result}"
        )

        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
