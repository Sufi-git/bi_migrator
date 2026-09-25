from dataclasses import dataclass
from io import BytesIO
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET


@dataclass
class TableauWorkbookInfo:
    filename: str
    extension: str
    workbook_xml_size: int
    worksheet_names: list[str]
    dashboard_names: list[str]
    datasource_names: list[str]
    packaged_files: list[dict[str, int]]
    twb_member_name: str | None = None

    @property
    def worksheet_count(self) -> int:
        return len(self.worksheet_names)

    @property
    def dashboard_count(self) -> int:
        return len(self.dashboard_names)

    @property
    def datasource_count(self) -> int:
        return len(self.datasource_names)

    @property
    def packaged_file_count(self) -> int:
        return len(self.packaged_files)


def _local_name(tag: str) -> str:
    """Return an XML tag name without a namespace."""
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]

    return tag


def _parse_twb_xml(xml_bytes: bytes) -> tuple[
    list[str],
    list[str],
    list[str],
]:
    """Parse Tableau workbook XML and extract basic workbook objects."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(
            f"The Tableau workbook XML could not be parsed: {exc}"
        ) from exc

    worksheets: list[str] = []
    dashboards: list[str] = []
    datasources: list[str] = []

    for element in root.iter():
        tag = _local_name(element.tag)

        if tag == "worksheet":
            name = element.attrib.get("name")
            if name:
                worksheets.append(name)

        elif tag == "dashboard":
            name = element.attrib.get("name")
            if name:
                dashboards.append(name)

        elif tag == "datasource":
            name = (
                element.attrib.get("caption")
                or element.attrib.get("name")
            )

            if name:
                datasources.append(name)

    return worksheets, dashboards, datasources


def inspect_tableau_workbook(
    filename: str,
    file_bytes: bytes,
) -> TableauWorkbookInfo:
    """
    Inspect a .twb or .twbx Tableau workbook.

    For .twb:
        Parse the workbook XML directly.

    For .twbx:
        Read the ZIP package in memory, locate the embedded .twb,
        and parse that workbook XML.
    """
    extension = filename.rsplit(".", 1)[-1].lower()

    if extension not in {"twb", "twbx"}:
        raise ValueError(
            "Unsupported file type. Please upload a .twb or .twbx file."
        )

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    packaged_files: list[dict[str, int]] = []
    twb_member_name: str | None = None
    workbook_xml: bytes

    if extension == "twb":
        workbook_xml = file_bytes

    else:
        try:
            with ZipFile(BytesIO(file_bytes)) as archive:
                members = archive.infolist()

                packaged_files = [
                    {
                        "name": member.filename,
                        "size_bytes": member.file_size,
                    }
                    for member in members
                ]

                twb_members = [
                    member
                    for member in members
                    if member.filename.lower().endswith(".twb")
                ]

                if not twb_members:
                    raise ValueError(
                        "The .twbx package does not contain a .twb workbook."
                    )

                twb_member = twb_members[0]
                twb_member_name = twb_member.filename
                workbook_xml = archive.read(twb_member)

        except BadZipFile as exc:
            raise ValueError(
                "The uploaded .twbx file is not a valid ZIP package."
            ) from exc

    (
        worksheet_names,
        dashboard_names,
        datasource_names,
    ) = _parse_twb_xml(workbook_xml)

    return TableauWorkbookInfo(
        filename=filename,
        extension=f".{extension}",
        workbook_xml_size=len(workbook_xml),
        worksheet_names=worksheet_names,
        dashboard_names=dashboard_names,
        datasource_names=datasource_names,
        packaged_files=packaged_files,
        twb_member_name=twb_member_name,
    )
