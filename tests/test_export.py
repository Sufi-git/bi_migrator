import json

from src.bi_migrator.export import (
    export_migration_json,
)
from src.bi_migrator.model import (
    MigrationConnection,
    MigrationDatasource,
    MigrationField,
    MigrationTable,
    MigrationWorkbook,
)


def test_export_migration_json(tmp_path):

    workbook = MigrationWorkbook(
        filename="sales.twb",
        extension=".twb",
        worksheets=["Sales by Region"],
        dashboards=["Sales Overview"],
        datasources=[
            MigrationDatasource(
                name="Sales Data",
                connections=[
                    MigrationConnection(
                        connection_class="sqlserver",
                        server="sales-server",
                        database="SalesDB",
                    )
                ],
                tables=[
                    MigrationTable(
                        name="Orders",
                        table="[Orders$]",
                        relation_type="table",
                    )
                ],
                fields=[
                    MigrationField(
                        name="Sales",
                        caption="Sales",
                        datatype="real",
                        role="measure",
                        field_type="quantitative",
                    )
                ],
            )
        ],
    )

    output_path = tmp_path / "migration.json"

    result = export_migration_json(
        workbook,
        output_path,
    )

    assert result == output_path
    assert output_path.exists()

    data = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert data["filename"] == "sales.twb"
    assert data["extension"] == ".twb"

    assert data["worksheets"] == [
        "Sales by Region"
    ]

    assert data["dashboards"] == [
        "Sales Overview"
    ]

    assert data["datasources"][0]["name"] == (
        "Sales Data"
    )

    assert (
        data["datasources"][0]["fields"][0]["name"]
        == "Sales"
    )
