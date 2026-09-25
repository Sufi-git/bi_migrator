from src.bi_migrator.model import (
    MigrationTable,
)
from src.bi_migrator.powerbi.mapper import (
    map_table,
    map_tables,
)


def test_map_table():

    table = MigrationTable(
        name="Orders",
        table="[Orders$]",
        relation_type="table",
    )

    result = map_table(table)

    assert result.tableau_name == "Orders"
    assert result.powerbi_name == "Orders"
    assert result.status == "Ready"


def test_map_tables():

    tables = [
        MigrationTable(
            name="Orders",
            table="[Orders$]",
            relation_type="table",
        ),
        MigrationTable(
            name="Customers",
            table="[Customers$]",
            relation_type="table",
        ),
    ]

    result = map_tables(tables)

    assert len(result) == 2

    assert result[0].tableau_name == "Orders"
    assert result[0].powerbi_name == "Orders"

    assert result[1].tableau_name == "Customers"
    assert result[1].powerbi_name == "Customers"

    assert all(
        mapping.status == "Ready"
        for mapping in result
    )
