import json
import tempfile
from pathlib import Path

import streamlit as st

from src.bi_migrator.analyzer import (
    analyze_tableau_file,
)
from src.bi_migrator.tableau.reader import (
    inspect_tableau_workbook,
)


st.set_page_config(
    page_title="BI Migrator",
    page_icon="🔄",
    layout="wide",
)


st.title("🔄 BI Migrator")

st.write(
    "Migrate dashboards and reports between Tableau and Power BI."
)

st.divider()

st.subheader("Tableau → Power BI")

uploaded_file = st.file_uploader(
    "Upload a Tableau workbook",
    type=["twb", "twbx"],
    help="Supported formats: .twb and .twbx",
)


if uploaded_file is None:

    st.info(
        "Upload a .twb or .twbx Tableau workbook to begin."
    )

else:

    file_bytes = uploaded_file.getvalue()

    try:

        workbook = inspect_tableau_workbook(
            filename=uploaded_file.name,
            file_bytes=file_bytes,
        )

        st.success(
            f"Successfully inspected {workbook.filename}"
        )

        # ----------------------------------------------------------
        # Workbook summary
        # ----------------------------------------------------------

        st.subheader("Workbook Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Format",
                workbook.extension,
            )

        with col2:
            st.metric(
                "Worksheets",
                workbook.worksheet_count,
            )

        with col3:
            st.metric(
                "Dashboards",
                workbook.dashboard_count,
            )

        with col4:
            st.metric(
                "Data Sources",
                workbook.datasource_count,
            )

        st.divider()

        # ----------------------------------------------------------
        # Data model summary
        # ----------------------------------------------------------

        st.subheader("Data Model")

        model_col1, model_col2, model_col3, model_col4 = (
            st.columns(4)
        )

        with model_col1:
            st.metric(
                "Tables",
                workbook.table_count,
            )

        with model_col2:
            st.metric(
                "Fields",
                workbook.field_count,
            )

        with model_col3:
            st.metric(
                "Calculated Fields",
                workbook.calculated_field_count,
            )

        with model_col4:
            st.metric(
                "Joins",
                workbook.join_count,
            )

        st.divider()

        # ----------------------------------------------------------
        # File details
        # ----------------------------------------------------------

        st.subheader("File Details")

        st.write(
            {
                "filename": workbook.filename,
                "format": workbook.extension,
                "uploaded_size_bytes": len(file_bytes),
                "workbook_xml_size_bytes": (
                    workbook.workbook_xml_size
                ),
            }
        )

        if workbook.twb_member_name:

            st.write(
                {
                    "embedded_workbook": (
                        workbook.twb_member_name
                    ),
                    "packaged_file_count": (
                        workbook.packaged_file_count
                    ),
                }
            )

        st.divider()

        # ----------------------------------------------------------
        # Workbook objects
        # ----------------------------------------------------------

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "Worksheets",
                "Dashboards",
                "Data Sources",
                "Data Model",
            ]
        )

        with tab1:

            if workbook.worksheet_names:

                st.dataframe(
                    {
                        "Worksheet": (
                            workbook.worksheet_names
                        )
                    },
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No worksheets found."
                )

        with tab2:

            if workbook.dashboard_names:

                st.dataframe(
                    {
                        "Dashboard": (
                            workbook.dashboard_names
                        )
                    },
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No dashboards found."
                )

        with tab3:

            if workbook.datasources:

                datasource_rows = []

                for datasource in workbook.datasources:

                    datasource_rows.append(
                        {
                            "Data Source": datasource.name,
                            "Connections": len(
                                datasource.connections
                            ),
                            "Tables": len(
                                datasource.tables
                            ),
                            "Fields": len(
                                datasource.fields
                            ),
                            "Calculated Fields": len(
                                datasource.calculated_fields
                            ),
                            "Joins": len(
                                datasource.joins
                            ),
                        }
                    )

                st.dataframe(
                    datasource_rows,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No data sources found."
                )

        with tab4:

            for datasource in workbook.datasources:

                st.markdown(
                    f"### {datasource.name}"
                )

                st.markdown("**Connections**")

                if datasource.connections:

                    connection_rows = []

                    for connection in datasource.connections:

                        connection_rows.append(
                            {
                                "Class": (
                                    connection.connection_class
                                    or ""
                                ),
                                "Server": (
                                    connection.server
                                    or ""
                                ),
                                "Database": (
                                    connection.database
                                    or ""
                                ),
                                "Schema": (
                                    connection.schema
                                    or ""
                                ),
                                "Port": (
                                    connection.port
                                    or ""
                                ),
                                "Filename": (
                                    connection.filename
                                    or ""
                                ),
                            }
                        )

                    st.dataframe(
                        connection_rows,
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.info(
                        "No connection metadata found."
                    )

                st.markdown("**Tables / Relations**")

                if datasource.tables:

                    table_rows = []

                    for table in datasource.tables:

                        table_rows.append(
                            {
                                "Name": (
                                    table.name
                                    or ""
                                ),
                                "Table": (
                                    table.table
                                    or ""
                                ),
                                "Type": (
                                    table.relation_type
                                    or ""
                                ),
                            }
                        )

                    st.dataframe(
                        table_rows,
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.info(
                        "No tables or relations found."
                    )

                st.markdown("**Fields**")

                if datasource.fields:

                    field_rows = []

                    for field in datasource.fields:

                        field_rows.append(
                            {
                                "Name": field.name,
                                "Caption": (
                                    field.caption
                                    or ""
                                ),
                                "Data Type": (
                                    field.datatype
                                    or ""
                                ),
                                "Role": (
                                    field.role
                                    or ""
                                ),
                                "Type": (
                                    field.field_type
                                    or ""
                                ),
                                "Calculated": (
                                    "Yes"
                                    if field.calculation_formula
                                    else "No"
                                ),
                            }
                        )

                    st.dataframe(
                        field_rows,
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.info(
                        "No fields found."
                    )

                if datasource.calculated_fields:

                    st.markdown(
                        "**Calculated Fields**"
                    )

                    calculation_rows = []

                    for calculated_field in (
                        datasource.calculated_fields
                    ):

                        calculation_rows.append(
                            {
                                "Field": (
                                    calculated_field.caption
                                    or calculated_field.name
                                ),
                                "Formula": (
                                    calculated_field.calculation_formula
                                    or ""
                                ),
                            }
                        )

                    st.dataframe(
                        calculation_rows,
                        use_container_width=True,
                        hide_index=True,
                    )

                st.divider()

        # ----------------------------------------------------------
        # TWBX package contents
        # ----------------------------------------------------------

        if workbook.packaged_files:

            st.subheader(
                "Packaged Files"
            )

            st.dataframe(
                workbook.packaged_files[:50],
                use_container_width=True,
                hide_index=True,
            )

    except ValueError as exc:

        st.error(
            str(exc)
        )

    except Exception as exc:

        st.error(
            "An unexpected error occurred while "
            "inspecting the workbook."
        )

        st.exception(exc)
