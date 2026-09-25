from pathlib import Path

from src.bi_migrator.analyzer import (
    analyze_tableau_file,
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


def test_analyze_tableau_file(tmp_path):

    input_path = tmp_path / "sales.twb"
    output_path = tmp_path / "migration.json"

    input_path.write_bytes(SAMPLE_TWB)

    result = analyze_tableau_file(
        input_path,
        output_path,
    )

    assert result == output_path
    assert output_path.exists()

    data = output_path.read_text(
        encoding="utf-8"
    )

    assert '"filename": "sales.twb"' in data
    assert '"Sales Data"' in data
    assert '"Sales"' in data
