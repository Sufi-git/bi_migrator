from dataclasses import dataclass, field


@dataclass
class MigrationField:
    name: str
    caption: str | None = None
    datatype: str | None = None
    role: str | None = None
    field_type: str | None = None
    calculation_formula: str | None = None


@dataclass
class MigrationTable:
    name: str | None = None
    table: str | None = None
    relation_type: str | None = None


@dataclass
class MigrationConnection:
    connection_class: str | None = None
    server: str | None = None
    database: str | None = None
    schema: str | None = None
    port: str | None = None
    filename: str | None = None


@dataclass
class MigrationJoin:
    join_type: str | None = None
    conditions: list[str] = field(
        default_factory=list
    )


@dataclass
class MigrationDatasource:
    name: str
    connections: list[MigrationConnection] = field(
        default_factory=list
    )
    tables: list[MigrationTable] = field(
        default_factory=list
    )
    fields: list[MigrationField] = field(
        default_factory=list
    )
    joins: list[MigrationJoin] = field(
        default_factory=list
    )


@dataclass
class MigrationWorkbook:
    filename: str
    extension: str
    worksheets: list[str] = field(default_factory=list)
    dashboards: list[str] = field(default_factory=list)
    datasources: list[MigrationDatasource] = field(
        default_factory=list
    )
