import streamlit as st

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
    help="Supported Tableau formats: .twb and .twbx",
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

        st.subheader("File Details")

        st.write(
            {
                "filename": workbook.filename,
                "format": workbook.extension,
                "uploaded_size_bytes": len(file_bytes),
                "workbook_xml_size_bytes": workbook.workbook_xml_size,
            }
        )

        if workbook.twb_member_name:
            st.write(
                {
                    "embedded_workbook": workbook.twb_member_name,
                    "packaged_file_count": workbook.packaged_file_count,
                }
            )

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Worksheets")

            if workbook.worksheet_names:
                st.dataframe(
                    {"Worksheet": workbook.worksheet_names},
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No worksheets found.")

        with col2:
            st.subheader("Dashboards")

            if workbook.dashboard_names:
                st.dataframe(
                    {"Dashboard": workbook.dashboard_names},
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No dashboards found.")

        with col3:
            st.subheader("Data Sources")

            if workbook.datasource_names:
                st.dataframe(
                    {"Data Source": workbook.datasource_names},
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No data sources found.")

        if workbook.packaged_files:
            st.divider()

            st.subheader("Packaged Files")

            st.caption(
                "Showing the first 50 files contained in the .twbx package."
            )

            st.dataframe(
                workbook.packaged_files[:50],
                use_container_width=True,
                hide_index=True,
            )

    except ValueError as exc:
        st.error(str(exc))

    except Exception as exc:
        st.error(
            "An unexpected error occurred while inspecting the workbook."
        )

        st.exception(exc)
