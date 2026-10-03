import streamlit as st
from src.format_page import render_header

if __name__ in ("__main__", "__page__"):
    render_header()
    st.subheader("Build a PMO", divider="gray")
    st.markdown(
        """
        Build a PMO (Portable Microhaplotype Object) file from your own data.
        This part of the app converts your data from tabular files (CSV, TSV,
        Excel) into the relational PMO format.
        """
    )

    st.subheader("Components", divider="gray")

    st.markdown(
        """
        As you move through the pages you will put together the following information. Together these will make a complete PMO:
        - **Panel Information**: A table including data on the targets that make up the panel, at minimum the panel name, target names and their primer pairs
        - **Microhaplotype Information**: A table containing the alleles called for each of the samples for each of the targets and the read counts associated.


        **Optionally, you can also add the following:**
        - **Specimen Information (highly recommended)**: Metadata describing the biological specimens.
        - **Project Information**: Information describing the project this data belongs to.
        - **Library Sample Information**: Metadata describing each library created from a specimen.
        - **Bioinformatics Information**: Information on the bioinformatics pipeline used to generate the allele data.
        - **Sequencing Information**: Information on how the samples were sequenced.
        - **Read Counts per Stage**: A table containing the raw read counts per sample and a table containing the read counts for each stage of the bioinformatics pipeline per sample per target.

        More information on the file format can be found [here](https://plasmogenepi.github.io/PMO_Docs/)
        """
    )

    st.markdown(
        "If unfamiliar with the PMO format, you can download a template Excel file below to get started"
    )
    with open("example_data/PMO_building_template.xlsx", "rb") as f:
        st.download_button(
            label="Download PMO Excel template",
            data=f,
            file_name="PMO_building_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            icon=":material/download:",  # optional
        )

    st.subheader("How building your PMO will work", divider="gray")
    st.markdown(
        """
        For each of the components above you will either type information or upload it as a table. When uploading as a table you will...
        - **Enter Data**: Upload data as tables with your version of the information.
        - **Map Fields**: Map your data fields to match the PMO format.
        - **Save Progress (Optional)**: If you may reuse the section (e.g. Panel Information) you can save it for future PMO file generation.

        Once you have all of the parts together you can merge the parts and export your completed PMO file.
        """
    )

    st.markdown(
        """
            ---
            ### Ready to Get Started?
            Select **Panel Information** from the sidebar (or click link below) to begin building your PMO file!
            """
    )
    st.page_link("app_pages/Panel_Information.py", label="Panel Information")
