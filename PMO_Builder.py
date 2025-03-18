import streamlit as st
from src.format_page import render_header

def main():
    render_header()
    # Introduction Section
    st.subheader("About the PMO Builder", divider="gray")
    st.markdown(
        """
        The **PMO Builder** is designed to help create and manage PMO 
        (Portable Microhaplotype Object) files from your own data to organize 
        and store information in a standardized format. This app simplifies the 
        conversion of your data from multiple CSV files into the relational PMO format.
        """
    )

    # Key Features
    st.subheader("Components", divider="gray")
    st.markdown(
        """
        As you move through the app you will put together the following information. Together these will make a complete PMO:
        - **Panel Information**: A table including data on the targets that make up the panel.
        - **Sequencing Information**: Information on how the samples were sequenced.
        - **Bioinformatics Information**: Information on the bioinformatics pipeline used to generate the allele data.
        - **Allele table**: A table containing the alleles called for each of the samples for each of the targets and the reads associated.
        - **Demultiplexed reads**: A table containing the raw reads for each sample, for each target after demultiplexing, before any filtering.
        - **Experimental metadata**: Information on the sequencing run, for example where each sample was located on the plate.
        - **Specimen Information**: metadata on the biological samples.

        More information on the file format can be found [here](https://plasmogenepi.github.io/PMO_Docs/format/FormatOverview.html)
        """
    )

    # How this will work
    st.subheader("How building your PMO will work", divider="gray")
    st.markdown(
        """
        For each of the components above you will...
        - **Upload Data**: Upload your version of the information.
        - **Map Fields**: Map your data fields to match the PMO format.
        - **Save Progress (Optional)**: If you may reuse the section (e.g. Panel Information) you can save it for future PMO file generation.

        Once you have all of the parts together you can merge the parts and export your completed PMO file in JSON format.
        """
    )

    # Call to Action
    st.markdown(
        """
            ---
            ### Ready to Get Started?
            Select **Panel Information** from the sidebar to begin building your PMO file!
            """
    )


if __name__ == "__main__":
    main()
