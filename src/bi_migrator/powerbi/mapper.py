from dataclasses import dataclass

from src.bi_migrator.model import (
    MigrationTable,
)


@dataclass
class PowerBITableMapping:
    tableau_name: str
    powerbi_name: str
    status: str


def map_table(
    table: MigrationTable,
) -> PowerBITableMapping:
    """Create a basic Tableau table to Power BI table mapping."""

    powerbi_name = (
        table.name
        or table.table
        or "Unnamed Table"
    )

    return PowerBITableMapping(
        tableau_name=(
            table.name
            or table.table
            or "Unnamed Table"
        ),
        powerbi_name=powerbi_name,
        status="Ready",
    )


def map_tables(
    tables: list[MigrationTable],
) -> list[PowerBITableMapping]:
    """Map all Tableau tables to Power BI tables."""

    return [
        map_table(table)
        for table in tables
    ]
