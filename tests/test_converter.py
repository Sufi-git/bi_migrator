from src.bi_migrator.tableau.converter import (
    convert_tableau_workbook,
)
from src.bi_migrator.tableau.reader import (
    inspect_tableau_workbook,
)


SAMPLE_TWB = b"""<?xml version="1.0" encoding="utf-8"?>
<workbook>
    <datasources>
        <datasource
            name="sales"
            caption="Sales Data"
        >
            <connection
                class="sqlserver"
                server="sales-server"
                dbname="SalesDB"
                schema="dbo"
                port="1433"
            />

            <relation
                name="Orders"
                table="[Orders$]"
                type="table"
            />

            <column
                name="[Sales]"
                caption="Sales"
                datatype="real"
                role="measure"
                type="quantitative"
            />
        </datasource>
    </datasources>

    <worksheets>
        <worksheet name="Sales by Region" />
    </worksheets>

    <dashboards>
        <dashboard name="Sales Overview" />
    </dashboards>
</workbook>
"""


def test_convert_tableau_workbook():

    tableau_workbook = inspect_tableau_workbook(
        "sales.twb",
        SAMPLE_TWB,
    )

    migration_workbook = convert_tableau_workbook(
        tableau_workbook
    )

    assert migration_workbook.filename == "sales.twb"
    assert migration_workbook.extension == ".twb"

    assert migration_workbook.worksheets == [
        "Sales by Region"
    ]

    assert migration_workbook.dashboards == [
        "Sales Overview"
    ]

    datasource = migration_workbook.datasources[0]

    assert datasource.name == "Sales Data"

    assert datasource.connections[0].server == (
        "sales-server"
    )

    assert datasource.tables[0].name == "Orders"

    assert datasource.fields[0].name == "Sales"
