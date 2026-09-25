from src.bi_migrator.model import (
    MigrationConnection,
    MigrationDatasource,
    MigrationField,
    MigrationTable,
    MigrationWorkbook,
)


def test_migration_model():

    connection = MigrationConnection(
        connection_class="sqlserver",
        server="sales-server",
        database="SalesDB",
    )

    table = MigrationTable(
        name="Orders",
        table="[Orders$]",
        relation_type="table",
    )

    field = MigrationField(
        name="Sales",
        caption="Sales",
        datatype="real",
        role="measure",
        field_type="quantitative",
    )

    datasource = MigrationDatasource(
        name="Sales Data",
        connections=[connection],
        tables=[table],
        fields=[field],
    )

    workbook = MigrationWorkbook(
        filename="sales.twb",
        extension=".twb",
        worksheets=["Sales by Region"],
        dashboards=["Sales Overview"],
        datasources=[datasource],
    )

    assert workbook.filename == "sales.twb"
    assert workbook.extension == ".twb"

    assert workbook.worksheets == [
        "Sales by Region"
    ]

    assert workbook.dashboards == [
        "Sales Overview"
    ]

    assert workbook.datasources[0].name == "Sales Data"

    assert (
        workbook.datasources[0]
        .connections[0]
        .server
        == "sales-server"
    )

    assert (
        workbook.datasources[0]
        .fields[0]
        .name
        == "Sales"
    )
