from dataclasses import dataclass, field
from io import BytesIO
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET


@dataclass
class TableauConnectionInfo:
    connection_class: str | None = None
    server: str | None = None
    database: str | None = None
    schema: str | None = None
    port: str | None = None
    filename: str | None = None


@dataclass
class TableauTableInfo:
    name: str | None = None
    table: str | None = None
    relation_type: str | None = None


@dataclass
class TableauFieldInfo:
    name: str
    caption: str | None = None
    datatype: str | None = None
    role: str | None = None
    field_type: str | None = None
    hidden: str | None = None
    default_format: str | None = None
    calculation_formula: str | None = None


@dataclass
class TableauJoinInfo:
    join_type: str | None = None
    conditions: list[str] = field(default_factory=list)


@dataclass
class TableauDatasourceInfo:
    name: str
    connections: list[TableauConnectionInfo] = field(default_factory=list)
    tables: list[TableauTableInfo] = field(default_factory=list)
    fields: list[TableauFieldInfo] = field(default_factory=list)
    joins: list[TableauJoinInfo] = field(default_factory=list)

    @property
    def calculated_fields(self) -> list[TableauFieldInfo]:
        return [
            field
            for field in self.fields
            if field.calculation_formula
        ]


@dataclass
class TableauWorkbookInfo:
    filename: str
    extension: str
    workbook_xml_size: int
    worksheet_names: list[str]
    dashboard_names: list[str]
    datasource_names: list[str]
    packaged_files: list[dict[str, int]]
    datasources: list[TableauDatasourceInfo] = field(
        default_factory=list
    )
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

    @property
    def table_count(self) -> int:
        return sum(
            len(datasource.tables)
            for datasource in self.datasources
        )

    @property
    def field_count(self) -> int:
        return sum(
            len(datasource.fields)
            for datasource in self.datasources
        )

    @property
    def calculated_field_count(self) -> int:
        return sum(
            len(datasource.calculated_fields)
            for datasource in self.datasources
        )

    @property
    def join_count(self) -> int:
        return sum(
            len(datasource.joins)
            for datasource in self.datasources
        )


def _local_name(tag: str) -> str:
    """Return the XML tag name without a namespace."""
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]

    return tag


def _parse_join(element: ET.Element) -> TableauJoinInfo:
    """Extract basic information from a Tableau join relation."""
    conditions: list[str] = []

    for expression in element.iter():
        if _local_name(expression.tag) != "expression":
            continue

        value = expression.attrib.get("op")

        if value:
            conditions.append(value)

    return TableauJoinInfo(
        join_type=element.attrib.get("join"),
        conditions=conditions,
    )


def _parse_datasource(
    datasource_element: ET.Element,
) -> TableauDatasourceInfo:
    """Extract a basic Tableau datasource model."""
    datasource_name = (
        datasource_element.attrib.get("caption")
        or datasource_element.attrib.get("name")
        or "Unnamed Data Source"
    )

    datasource = TableauDatasourceInfo(
        name=datasource_name
    )

    # Direct datasource connections.
    for child in datasource_element.iter():
        if _local_name(child.tag) != "connection":
            continue

        connection = TableauConnectionInfo(
            connection_class=child.attrib.get("class"),
            server=child.attrib.get("server"),
            database=child.attrib.get("dbname"),
            schema=child.attrib.get("schema"),
            port=child.attrib.get("port"),
            filename=child.attrib.get("filename"),
        )

        datasource.connections.append(connection)

    # Relations represent physical tables, custom SQL, joins, etc.
    for relation in datasource_element.iter():
        if _local_name(relation.tag) != "relation":
            continue

        relation_type = relation.attrib.get("type")

        if relation_type == "join":
            datasource.joins.append(
                _parse_join(relation)
            )
            continue

        if relation_type in {"table", "text"}:
            table_name = (
                relation.attrib.get("name")
                or relation.attrib.get("table")
            )

            datasource.tables.append(
                TableauTableInfo(
                    name=relation.attrib.get("name"),
                    table=relation.attrib.get("table"),
                    relation_type=relation_type,
                )
            )

    # Tableau fields are generally represented as column elements.
    # We only inspect direct datasource children to avoid treating
    # relation-level raw column definitions as duplicate fields.
    for child in list(datasource_element):
        if _local_name(child.tag) != "column":
            continue

        calculation_formula = None

        for nested in child:
            if _local_name(nested.tag) == "calculation":
                calculation_formula = nested.attrib.get("formula")
                break

        field_info = TableauFieldInfo(
            name=child.attrib.get("name", "Unnamed Field"),
            caption=child.attrib.get("caption"),
            datatype=child.attrib.get("datatype"),
            role=child.attrib.get("role"),
            field_type=child.attrib.get("type"),
            hidden=child.attrib.get("hidden"),
            default_format=child.attrib.get("default-format"),
            calculation_formula=calculation_formula,
        )

        datasource.fields.append(field_info)

    return datasource


def _parse_twb_xml(
    xml_bytes: bytes,
) -> tuple[
    list[str],
    list[str],
    list[str],
    list[TableauDatasourceInfo],
]:
    """Extract workbook structure and basic data-model metadata."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(
            f"The Tableau workbook XML could not be parsed: {exc}"
        ) from exc

    worksheets: list[str] = []
    dashboards: list[str] = []
    datasource_names: list[str] = []
    datasources: list[TableauDatasourceInfo] = []

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
                datasource_names.append(name)

            # Ignore Tableau's special Parameters datasource for now.
            if name != "Parameters":
                datasources.append(
                    _parse_datasource(element)
                )

    return (
        worksheets,
        dashboards,
        datasource_names,
        datasources,
    )


def inspect_tableau_workbook(
    filename: str,
    file_bytes: bytes,
) -> TableauWorkbookInfo:
    """
    Inspect a Tableau .twb or .twbx workbook.

    .twb  -> parse XML directly

    .twbx -> open ZIP package and locate the embedded .twb
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

                workbook_xml = archive.read(
                    twb_member
                )

        except BadZipFile as exc:
            raise ValueError(
                "The uploaded .twbx file is not a valid ZIP package."
            ) from exc

    (
        worksheet_names,
        dashboard_names,
        datasource_names,
        datasources,
    ) = _parse_twb_xml(workbook_xml)

    return TableauWorkbookInfo(
        filename=filename,
        extension=f".{extension}",
        workbook_xml_size=len(workbook_xml),
        worksheet_names=worksheet_names,
        dashboard_names=dashboard_names,
        datasource_names=datasource_names,
        packaged_files=packaged_files,
        datasources=datasources,
        twb_member_name=twb_member_name,
    )
