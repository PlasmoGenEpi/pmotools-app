import streamlit as st
from src.format_page import render_header


def home() -> None:
    render_header()
    st.subheader("About PMO Tools", divider="gray")
    st.markdown(
        """
        PMO (Portable Microhaplotype Object) is a standard format for storing
        targeted amplicon sequencing data, together with the metadata needed
        to interpret and share it. This app helps you create and work with PMO
        files without writing any code. It uses
        [pmotools-python](https://github.com/PlasmoGenEpi/pmotools-python)
        behind the scenes.

        More information on the file format can be found
        [here](https://plasmogenepi.github.io/PMO_Docs/).
        """
    )

    st.subheader("What would you like to do?", divider="gray")
    with st.container(border=True):
        st.markdown(
            "##### Build a PMO\n\n"
            "Convert your own tables (panel, microhaplotypes and optional"
            " metadata) into a PMO file."
        )
        st.page_link(
            "app_pages/Build_a_PMO.py",
            label="Get started building a PMO",
            icon=":material/arrow_forward:",
        )
    with st.container(border=True):
        st.markdown(
            "##### Merge PMOs\n\n"
            "Combine several PMO files, for example from different sequencing"
            " runs or sites using the same panel, into a single PMO."
        )
        st.page_link(
            "app_pages/Merge_PMOs.py",
            label="Merge PMO files",
            icon=":material/arrow_forward:",
        )


pages = {
    "Build a PMO": [
        st.Page("app_pages/Build_a_PMO.py", title="Getting Started"),
    ],
    "Required": [
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
    "Merge PMOs": [
        st.Page("app_pages/Merge_PMOs.py", title="Merge PMO Files"),
    ],
}

pg = st.navigation(
    {
        "": [st.Page(home, title="Home", default=True)],
        **pages,
    }
)
pg.run()
