import io
import sys
import os
import streamlit as st
import fitz  # pymupdf

sys.path.insert(0, os.path.dirname(__file__))
from pdf_notebook import PDFHyperlinkedNotebookGenerator

st.set_page_config(page_title="Notebook Generator", page_icon="📓", layout="centered")

st.title("📓 PDF Notebook Generator")
st.caption("Generate custom notebooks for reMarkable, Onyx Boox, and standard paper sizes.")

st.markdown("""
Each notebook starts with a **title page** followed by a **table of contents**, then your chosen number of pages.
Every entry in the table of contents links directly to its corresponding page in the notebook,
and every page number links back to the table of contents.

Because the links are page-based rather than bookmark-based, **inserting pages inside the notebook
preserves all navigation** — just update the TOC entries to match the new page numbers.
""")

# --- Device options ---
DEVICES = {
    "reMarkable": {
        "reMarkable 2":             "remarkable2",
        "reMarkable 1":             "remarkable1",
        "reMarkable Paper Pro":     "remarkablepro",
        "reMarkable Paper Pro Move":"remarkablemove",
    },
    "Onyx Boox": {
        "Note Air":     "booxnoteair",
        "Note Air 3":   "booxnoteair3",
        "Note Air 3C":  "booxnoteair3c",
        "Note Air 4C":  "booxnoteair4c",
        "Note Max":     "booxnotemax",
        "Max Lumi":     "booxmaxlumi",
        "Tab Mini C":   "booxtabminic",
        "Go 10.3":      "booxgo103",
    },
    "Standard Paper": {
        "A4":     "a4",
        "A5":     "a5",
        "Letter": "letter",
        "Legal":  "legal",
    },
}

PATTERNS = {
    "Dots":  "dots",
    "Lines": "lines",
    "Grid":  "grid",
    "Blank": "blank",
}

PAGE_NUMBER_POSITIONS = {
    "Lower Left":   "lower-left",
    "Lower Right":  "lower-right",
    "Lower Middle": "lower-middle",
    "Upper Right":  "upper-right",
    "Upper Middle": "upper-middle",
    "None":         None,
}

# --- Layout ---
col1, col2 = st.columns(2)

with col1:
    device_group = st.selectbox("Device type", list(DEVICES.keys()))
    device_display = st.selectbox("Device", list(DEVICES[device_group].keys()))
    device_key = DEVICES[device_group][device_display]

    pattern_display = st.selectbox("Page pattern", list(PATTERNS.keys()))
    pattern_key = PATTERNS[pattern_display]

    num_pages = st.number_input("Number of pages", min_value=1, max_value=1000, value=100, step=10)

with col2:
    spacing_mm = st.number_input("Spacing (mm)", min_value=2.0, max_value=20.0, value=5.0, step=0.5,
                                  help="Spacing between dots, lines, or grid cells")
    pos_display = st.selectbox("Page number position", list(PAGE_NUMBER_POSITIONS.keys()))
    page_number_position = PAGE_NUMBER_POSITIONS[pos_display]

    include_title_page = st.checkbox("Include title page", value=True)
    include_toc = st.checkbox("Include table of contents", value=True)

with st.expander("Margins (mm)"):
    mc1, mc2 = st.columns(2)
    with mc1:
        margin_left   = st.number_input("Left",   min_value=0, max_value=50, value=5)
        margin_top    = st.number_input("Top",    min_value=0, max_value=50, value=5)
    with mc2:
        margin_right  = st.number_input("Right",  min_value=0, max_value=50, value=5)
        margin_bottom = st.number_input("Bottom", min_value=0, max_value=50, value=5)

st.divider()

if st.button("Generate PDF", type="primary", use_container_width=True):
    with st.spinner("Generating your notebook..."):
        try:
            buffer = io.BytesIO()
            generator = PDFHyperlinkedNotebookGenerator(
                filename=buffer,
                num_pages=num_pages,
                page_size=device_key,
                page_pattern=pattern_key,
                spacing_mm=spacing_mm,
                page_number_position=page_number_position,
                include_title_page=include_title_page,
                include_toc=include_toc,
                margins={
                    "left":   margin_left,
                    "right":  margin_right,
                    "top":    margin_top,
                    "bottom": margin_bottom,
                },
            )
            num_toc_pages = generator._calculate_toc_pages() if include_toc else 0
            title_pages = 1 if include_title_page else 0
            first_content_idx = title_pages + num_toc_pages

            generator.generate()
            buffer.seek(0)
            pdf_bytes = buffer.read()

            filename = f"{device_display} - {pattern_display} - {num_pages}p.pdf"
            st.success("Notebook generated!")
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
            )

            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            preview_indices = []
            preview_labels = []
            if include_title_page:
                preview_indices.append(0)
                preview_labels.append("Title page")
            if include_toc:
                preview_indices.append(title_pages)
                preview_labels.append("Table of contents")
            if first_content_idx < len(doc):
                preview_indices.append(first_content_idx)
                preview_labels.append("Content page")

            if preview_indices:
                st.markdown("**Preview:**")
                cols = st.columns(len(preview_indices))
                for col, idx, label in zip(cols, preview_indices, preview_labels):
                    pix = doc[idx].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                    col.image(pix.tobytes("png"), use_container_width=True)
                    col.caption(label)
        except Exception as e:
            st.error(f"Error generating notebook: {e}")
