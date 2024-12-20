# utils.py
import streamlit as st


def render_header():
    """
    Render a header with a logo alongside text.
    """
    st.set_page_config(
        page_title="PMO Builder",
        page_icon="📂",
        layout="wide",
    )

    # Create two columns for layout: logo + text
    col1, col2 = st.columns([1, 4])

    with col1:
        st.image(
            "images/PGE_logo.png"
        )

    with col2:
        # Add title and subtitle
        st.title("PMO File Builder")
        st.markdown("**Streamlined Workflow for Generating PMO Files**")
