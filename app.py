import streamlit as st


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


# -------------------------------------------------------------------
# Migration direction
# -------------------------------------------------------------------

st.subheader("Migration")

col1, col2 = st.columns(2)

with col1:
    source = st.selectbox(
        "Source platform",
        ["Tableau", "Power BI"],
    )

with col2:
    target = "Power BI" if source == "Tableau" else "Tableau"

    st.text_input(
        "Target platform",
        value=target,
        disabled=True,
    )


st.divider()


# -------------------------------------------------------------------
# Tableau workbook upload
# -------------------------------------------------------------------

st.subheader("Upload Tableau Workbook")

uploaded_file = st.file_uploader(
    "Upload a Tableau workbook",
    type=["twb", "twbx"],
    help="Supported formats: .twb and .twbx",
)


if uploaded_file is not None:
    st.success("Tableau workbook uploaded successfully.")

    file_name = uploaded_file.name
    file_size_bytes = uploaded_file.size
    file_type = uploaded_file.type

    # Determine extension
    file_extension = (
        file_name.rsplit(".", 1)[-1].lower()
        if "." in file_name
        else "unknown"
    )

    # Convert size to KB / MB for display
    file_size_kb = file_size_bytes / 1024
    file_size_mb = file_size_bytes / (1024 * 1024)

    st.subheader("File Details")

    detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)

    with detail_col1:
        st.metric("Filename", file_name)

    with detail_col2:
        st.metric("Extension", f".{file_extension}")

    with detail_col3:
        st.metric("Size", f"{file_size_kb:.2f} KB")

    with detail_col4:
        st.metric("Type", file_type or "Unknown")

    st.divider()

    st.write("### File Information")

    st.write(
        {
            "filename": file_name,
            "extension": f".{file_extension}",
            "size_bytes": file_size_bytes,
            "size_kb": round(file_size_kb, 2),
            "size_mb": round(file_size_mb, 4),
            "content_type": file_type or "Unknown",
        }
    )

else:
    st.info(
        "Upload a Tableau .twb or .twbx workbook to view its file details."
    )
