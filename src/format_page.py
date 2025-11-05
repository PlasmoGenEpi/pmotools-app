"""
Format page utilities for the PMO Builder application.

This module provides common UI components and utilities for formatting pages
in the PMO Builder Streamlit application.
"""
import streamlit as st
import os

# Constants
PGE_LOGO_PATH = "images/PGE_logo.png"
PMO_LOGO_PATH = "images/PMO_logo.png"
PAGE_TITLE = "PMO Builder"
PAGE_ICON = "📂"
LAYOUT = "wide"
LOGO_COLUMN_RATIO = [1, 4]


def render_header() -> None:
    """
    Render a header with a logo alongside text.

    Sets up the page configuration and displays the PMO Builder header
    with the PGE logo and title information.
    """
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
    )

    # Create two columns for layout: logo + text
    col1, col2 = st.columns(LOGO_COLUMN_RATIO)

    with col1:
        _render_logo()

    with col2:
        _render_title_section()


def _render_logo() -> None:
    """Render the PGE logo with error handling."""
    try:
        if os.path.exists(PGE_LOGO_PATH):
            st.image(PGE_LOGO_PATH)
        else:
            st.warning(f"Logo not found at {PGE_LOGO_PATH}")
    except Exception as e:
        st.error(f"Error loading logo: {e}")


def _render_title_section() -> None:
    """Render the title and subtitle section."""
    st.title("PMO File Builder")
    st.markdown("**Streamlined Workflow for Generating PMO Files**")


def render_section_header(title: str, divider: str = "gray") -> None:
    """
    Render a standardized section header.

    Args:
        title: The title for the section
        divider: The divider style (default: "gray")
    """
    st.subheader(title, divider=divider)


def render_info_box(message: str, message_type: str = "info") -> None:
    """
    Render an information box with different styles.

    Args:
        message: The message to display
        message_type: Type of message ("info", "success", "warning", "error")
    """
    if message_type == "info":
        st.info(message)
    elif message_type == "success":
        st.success(message)
    elif message_type == "warning":
        st.warning(message)
    elif message_type == "error":
        st.error(message)
    else:
        st.info(message)  # Default to info


def render_centered_content(content: str, content_type: str = "markdown") -> None:
    """
    Render content in a centered column layout.

    Args:
        content: The content to display
        content_type: Type of content ("markdown", "text", "code")
    """
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if content_type == "markdown":
            st.markdown(content)
        elif content_type == "text":
            st.text(content)
        elif content_type == "code":
            st.code(content)
        else:
            st.markdown(content)  # Default to markdown
