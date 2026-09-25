import sys
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile


# Make the repository root importable in every test environment.
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from src.bi_migrator.tableau.reader import (
    inspect_tableau_workbook,
)


SAMPLE_TWB = b"""<?xml version="1.0" encoding="utf-8"?>
<workbook>
    <datasources>
        <datasource name="sales" caption="Sales Data" />
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

    assert "Sales by Region" in result.worksheet_names
    assert "Sales Trend" in result.worksheet_names
    assert "Sales Overview" in result.dashboard_names
    assert "Sales Data" in result.datasource_names


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
    assert result.twb_member_name == "Sales Workbook.twb"

    assert result.worksheet_count == 2
    assert result.dashboard_count == 1
    assert result.datasource_count == 1
    assert result.packaged_file_count == 2
