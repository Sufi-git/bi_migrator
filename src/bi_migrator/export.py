import json
from dataclasses import asdict
from pathlib import Path

from src.bi_migrator.model import MigrationWorkbook


def export_migration_json(
    workbook: MigrationWorkbook,
    output_path: str | Path,
) -> Path:
    """Write the canonical migration model to JSON."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            asdict(workbook),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return path
