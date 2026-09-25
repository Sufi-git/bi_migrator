import sys
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


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

            <relation
                name="Customers"
                table="[Customers$]"
                type="table"
            />

            <relation
                type="join"
                join="inner"
            >
                <clause type="join">
                    <expression op="=">
                        <expression op="[Orders].[Customer ID]" />
                        <expression op="[Customers].[ID]" />
                    </expression>
                </clause>

                <relation
                    name="Orders"
                    table="[Orders$]"
                    type="table"
                />

                <relation
                    name="Customers"
                    table="[Customers$]"
                    type="table"
                />
            </relation>

            <column
                name="[Sales]"
                caption="Sales"
                datatype="real"
                role="measure"
                type="quantitative"
            />

            <column
                name="[Profit]"
                caption="Profit"
                datatype="real"
                role="measure"
                type="quantitative"
            />

            <column
                name="[Profit Ratio]"
                caption="Profit Ratio"
                datatype="real"
                role="measure"
                type="quantitative"
            >
                <calculation
                    class="tableau"
                    formula="SUM([Profit])/SUM([Sales])"
                />
            </column>

        </datasource>

    </datasources>

    <worksheets>
        <worksheet name="Sales by Region" />
        <worksheet name="Sales Trend" />
    </worksheets>

    <dashboards>
        <dashboard name="Sales Overview" />
    </dashboards>

</workbook>
"""


def test_inspect_twb():

    result = inspect_tableau_workbook(
        "sales.twb",
        SAMPLE_TWB,
    )

    assert result.extension == ".twb"

    assert result.worksheet_count == 2
    assert result.dashboard_count == 1
    assert result.datasource_count == 1

    assert result.table_count == 2
    assert result.field_count == 3
    assert result.calculated_field_count == 1
    assert result.join_count == 1

    datasource = result.datasources[0]

    assert datasource.name == "Sales Data"

    assert len(datasource.connections) == 1
    assert datasource.connections[0].connection_class == "sqlserver"
    assert datasource.connections[0].server == "sales-server"
    assert datasource.connections[0].database == "SalesDB"

    assert len(datasource.tables) == 2

    assert "Sales" in [
        field.name
        for field in datasource.fields
    ]

    assert (
        datasource.calculated_fields[0]
        .calculation_formula
        == "SUM([Profit])/SUM([Sales])"
    )


def test_inspect_twbx():

    buffer = BytesIO()

    with ZipFile(buffer, "w") as archive:

        archive.writestr(
            "Sales Workbook.twb",
            SAMPLE_TWB,
        )

        archive.writestr(
            "Data/sample.csv",
            "Region,Sales\nWest,100\nEast,200",
        )

    result = inspect_tableau_workbook(
        "sales.twbx",
        buffer.getvalue(),
    )

    assert result.extension == ".twbx"

    assert (
        result.twb_member_name
        == "Sales Workbook.twb"
    )

    assert result.worksheet_count == 2
    assert result.dashboard_count == 1
    assert result.datasource_count == 1

    assert result.table_count == 2
    assert result.field_count == 3
    assert result.calculated_field_count == 1
    assert result.join_count == 1

    assert result.packaged_file_count == 2
