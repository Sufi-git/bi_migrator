from pathlib import Path

from src.bi_migrator.export import (
    export_migration_json,
)
from src.bi_migrator.tableau.converter import (
    convert_tableau_workbook,
)
from src.bi_migrator.tableau.reader import (
    inspect_tableau_workbook,
)


def analyze_tableau_file(
    input_path: str | Path,
    output_path: str | Path,
):
    """Analyze a Tableau workbook and export migration.json."""

    input_file = Path(input_path)

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )

    file_bytes = input_file.read_bytes()

    tableau_workbook = inspect_tableau_workbook(
        input_file.name,
        file_bytes,
    )

    migration_workbook = convert_tableau_workbook(
        tableau_workbook
    )

    return export_migration_json(
        migration_workbook,
        output_path,
    )
