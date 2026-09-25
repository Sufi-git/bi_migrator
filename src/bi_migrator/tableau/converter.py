from src.bi_migrator.model import (
    MigrationConnection,
    MigrationDatasource,
    MigrationField,
    MigrationJoin,
    MigrationTable,
    MigrationWorkbook,
)
from src.bi_migrator.tableau.reader import (
    TableauWorkbookInfo,
)


def convert_tableau_workbook(
    workbook: TableauWorkbookInfo,
) -> MigrationWorkbook:
    """Convert Tableau reader output into the canonical migration model."""

    datasources: list[MigrationDatasource] = []

    for datasource in workbook.datasources:

        connections = [
            MigrationConnection(
                connection_class=connection.connection_class,
                server=connection.server,
                database=connection.database,
                schema=connection.schema,
                port=connection.port,
                filename=connection.filename,
            )
            for connection in datasource.connections
        ]

        tables = [
            MigrationTable(
                name=table.name,
                table=table.table,
                relation_type=table.relation_type,
            )
            for table in datasource.tables
        ]

        fields = [
            MigrationField(
                name=field.name,
                caption=field.caption,
                datatype=field.datatype,
                role=field.role,
                field_type=field.field_type,
                calculation_formula=field.calculation_formula,
            )
            for field in datasource.fields
        ]

        joins = [
            MigrationJoin(
                join_type=join.join_type,
                conditions=list(join.conditions),
            )
            for join in datasource.joins
        ]

        datasources.append(
            MigrationDatasource(
                name=datasource.name,
                connections=connections,
                tables=tables,
                fields=fields,
                joins=joins,
            )
        )

    return MigrationWorkbook(
        filename=workbook.filename,
        extension=workbook.extension,
        worksheets=list(workbook.worksheet_names),
        dashboards=list(workbook.dashboard_names),
        datasources=datasources,
    )
