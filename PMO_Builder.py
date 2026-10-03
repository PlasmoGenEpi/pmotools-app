import os

import streamlit as st
from src.format_page import render_header
from src.template_builder import XLSX_MIME, build_full_template

MINIMUM_EXAMPLE_PATH = "example_data/minimum_pmo/minimum_pmo_template.xlsx"


def home() -> None:
    render_header()
    st.subheader("About the PMO Builder", divider="gray")
    st.markdown(
        """
        The **PMO Builder** is designed to help create and manage PMO
        (Portable Microhaplotype Object) files from your own data to organize
        and store information in a standardized format. This app simplifies the
        conversion of your data from multiple tabular files (CSV, TSV, EXCEL) into the relational PMO format.
        """
    )

    st.subheader("Components", divider="gray")

    st.markdown(
        "A PMO is built from the sections below. You only need the two required"
        " sections to build a valid PMO. The optional sections add context that"
        " makes your data easier to interpret and share."
    )

    with st.container(border=True):
        st.markdown(
            "##### :red-background[Required] The minimum PMO\n\n"
            "**Panel Information**: the targets in your panel and their primers.  \n"
            "Columns needed: `target_name`, `forward_primer_seq`,"
            " `reverse_primer_seq`. You will also give the panel a name.\n\n"
            "**Microhaplotype Information**: the microhaplotypes called in each"
            " sample.  \n"
            "Columns needed: `library_sample_name`, `target_name`, `seq`, `reads`.\n\n"
            "Every `target_name` in your microhaplotypes must also be in your panel."
        )
        if os.path.exists(MINIMUM_EXAMPLE_PATH):
            with open(MINIMUM_EXAMPLE_PATH, "rb") as f:
                st.download_button(
                    label="Download minimum PMO example",
                    data=f.read(),
                    file_name="minimum_pmo_example.xlsx",
                    mime=XLSX_MIME,
                    icon=":material/download:",
                    help="A filled-in template with just the two required sheets."
                    " Load it on the Load Full Template page and enter any panel"
                    " name.",
                )
        st.caption(
            "Uploaded a template with only the required sheets? You can still add"
            " any of the optional sections afterwards on their own pages in the"
            " sidebar, by typing them in or uploading a table."
        )
    with st.container(border=True):
        st.markdown(
            """
            ##### :blue-background[Optional] Add these if you have the information

            **Specimen Level Metadata** *(highly recommended)*: where and when
            each specimen was collected, and from whom.

            **Project Information**: the project this data belongs to.

            **Library Sample Level Metadata**: each library prepared from a specimen.

            **Sequencing Information**: how the samples were sequenced.

            **Bioinformatics Information**: the pipeline used to call the
            microhaplotypes.

            **Read Counts per Stage**: read counts per sample, and at each stage of
            the pipeline.
            """
        )
    st.markdown(
        "More information on the file format can be found"
        " [here](https://plasmogenepi.github.io/PMO_Docs/)."
    )

    st.subheader("How building your PMO will work", divider="gray")
    st.markdown(
        """
        There are two ways to put the components together:
        - **Fill in the full template**: Download the PMO Excel template, which has a sheet for each component, fill it in, and load it all at once. You can also upload the sheets as CSV/TSV files or a zipped folder.
        - **Build section by section**: Go through each component's page, typing information or uploading your own tables. When uploading a table you will...
            - **Enter Data**: Upload data as tables with your version of the information.
            - **Map Fields**: Map your data fields to match the PMO format.
            - **Save Progress (Optional)**: If you may reuse the section (e.g. Panel Information) you can save it for future PMO file generation.

        Either way, you can review or change any section on its page, then merge the parts and export your completed PMO file on the **Create Final PMO** page.
        """
    )

    st.markdown("---")
    st.markdown("### Ready to Get Started?")
    full_template, by_section = st.columns(2)
    with full_template.container(border=True):
        st.markdown(
            "**Fill in the full template**\n\n"
            "Download the template, fill in the sheets you have data for, then"
            " upload it to populate every section at once."
        )
        st.download_button(
            label="Download PMO Excel template",
            data=build_full_template(),
            file_name="PMO_building_template.xlsx",
            mime=XLSX_MIME,
            icon=":material/download:",
        )
        st.page_link(
            "app_pages/Load_Full_Template.py",
            label="Load Full Template",
            icon=":material/upload_file:",
        )
    with by_section.container(border=True):
        st.markdown(
            "**Build section by section**\n\n"
            "Start with Panel Information, then work through the pages in the"
            " sidebar."
        )
        st.page_link(
            "app_pages/Panel_Information.py",
            label="Panel Information",
            icon=":material/arrow_forward:",
        )


pages = {
    "Required (minimum PMO)": [
        st.Page("app_pages/Panel_Information.py", title="Panel Information"),
        st.Page(
            "app_pages/Microhaplotype_Information.py",
            title="Microhaplotype Information",
        ),
    ],
    "Optional": [
        st.Page(
            "app_pages/Specimen_Level_Metadata.py", title="Specimen Level Metadata"
        ),
        st.Page("app_pages/Project_Information.py", title="Project Information"),
        st.Page(
            "app_pages/Library_Sample_Level_Metadata.py",
            title="Library Sample Level Metadata",
        ),
        st.Page("app_pages/Sequencing_Information.py", title="Sequencing Information"),
        st.Page(
            "app_pages/Bioinformatics_Information.py",
            title="Bioinformatics Information",
        ),
        st.Page("app_pages/Read_Counts_per_Stage.py", title="Read Counts per Stage"),
    ],
    "Finalize": [
        st.Page("app_pages/Create_Final_PMO.py", title="Create Final PMO"),
    ],
}

pg = st.navigation(
    {
        "": [
            st.Page(home, title="Home", default=True),
            st.Page("app_pages/Load_Full_Template.py", title="Load Full Template"),
        ],
        **pages,
    }
)
pg.run()
