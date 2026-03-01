# PDF Notebook Templates

A Python-based PDF notebook generator designed specifically for e-ink tablets like reMarkable and Onyx Boox devices. Generate custom notebooks with dots, lines, grids, or blank pages, complete with hyperlinked table of contents and page numbers.

## Web App

Try it online: **[https://eink-notebook-templates.streamlit.app/](https://eink-notebook-templates.streamlit.app/)**

## Features

- 🎯 **Multiple Patterns**: Dots, lines, grid, or blank pages
- 📱 **Device-Specific Sizes**: Pre-configured for reMarkable and Onyx Boox tablets
- 🔗 **Hyperlinked Navigation**: Clickable page numbers and table of contents
- 📑 **Professional Layout**: Title page and TOC with customizable fields
- ⚙️ **Highly Customizable**: Margins, spacing, fonts, and page number positions
- 📦 **Batch Generation**: Create multiple PDFs at once for different devices and patterns
- 🎨 **Beautiful Typography**: Uses EB Garamond font for title and TOC pages

## Supported Devices

### reMarkable Tablets
- reMarkable 1 (10.3" - 157 × 210 mm)
- reMarkable 2 (10.3" - 157 × 210 mm)
- reMarkable Paper Pro (11.8" - 179 × 239 mm)
- reMarkable Paper Pro Move (7.3" - 91 × 162 mm)

### Onyx Boox Tablets
- Onyx Boox Go 10.3
- Onyx Boox Max Lumi (13.3")
- Onyx Boox Note Air series (10.3")
- Onyx Boox Note Air 3 (10.3")
- Onyx Boox Note Air 3C (10.3")
- Onyx Boox Note Air 4C (10.3")
- Onyx Boox Note Max (13.3")
- Onyx Boox Tab Mini C (7.8")

### Supernote Tablets
- Supernote A5X (10.3" - 158 × 210 mm)
- Supernote A6X (7.8" - 119 × 159 mm)
- Supernote A6X2 Nomad (7.8" - 119 × 159 mm)
- Supernote A5X2 Manta (10.7" - 163 × 217 mm)

### Standard Paper Sizes
- A4, A5, Letter, Legal

## Installation

### Requirements
- Python 3.7+
- reportlab

### Install Dependencies

```bash
pip install reportlab
```

### Clone the Repository

```bash
git clone https://github.com/yourusername/Notebook-Templates.git
cd Notebook-Templates
```

## Quick Start

### Single PDF Generation

```python
from pdf_notebook import PDFHyperlinkedNotebookGenerator

# Create a dot-grid notebook for reMarkable 2
generator = PDFHyperlinkedNotebookGenerator(
    filename="my_notebook.pdf",
    num_pages=100,
    page_size='remarkable2',
    page_pattern='dots'
)
generator.generate()
```

### Batch Generation

```python
from pdf_notebook import PDFNotebookBatchGenerator

# Generate all device/pattern combinations
batch = PDFNotebookBatchGenerator(
    num_pages=256,
    output_dir='toc-notebook'
)
stats = batch.generate_all()
print(f"Generated {stats['generated']} PDFs")
```

## Usage Examples

### Custom Margins

```python
generator = PDFHyperlinkedNotebookGenerator(
    filename="notebook.pdf",
    num_pages=100,
    page_size='remarkable2',
    margins={'left': 10, 'right': 10, 'top': 15, 'bottom': 15}
)
generator.generate()
```

### Different Patterns

```python
# Dot grid (default)
generator = PDFHyperlinkedNotebookGenerator(
    filename="dots.pdf",
    page_pattern='dots',
    spacing_mm=5,
    num_pages=50
)

# Horizontal lines
generator = PDFHyperlinkedNotebookGenerator(
    filename="lines.pdf",
    page_pattern='lines',
    spacing_mm=7,
    num_pages=50
)

# Grid
generator = PDFHyperlinkedNotebookGenerator(
    filename="grid.pdf",
    page_pattern='grid',
    spacing_mm=5,
    num_pages=50
)

# Blank pages
generator = PDFHyperlinkedNotebookGenerator(
    filename="blank.pdf",
    page_pattern='blank',
    num_pages=50
)
```

### Page Number Positions

```python
# Available positions: 'lower-left', 'lower-right', 'lower-middle',
# 'upper-right', 'upper-middle', or None
generator = PDFHyperlinkedNotebookGenerator(
    filename="notebook.pdf",
    num_pages=100,
    page_number_position='lower-left'  # Default
)
```

### Without Title Page or TOC

```python
generator = PDFHyperlinkedNotebookGenerator(
    filename="simple_notebook.pdf",
    num_pages=100,
    include_title_page=False,
    include_toc=False
)
```

### Batch Generation for Specific Devices

```python
batch = PDFNotebookBatchGenerator(
    devices=['remarkable2', 'booxnoteair'],
    patterns=['dots', 'lines'],
    num_pages=100,
    output_dir='toc-notebook'
)
batch.generate_all()
```

## Configuration Options

### PDFHyperlinkedNotebookGenerator Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filename` | str | Required | Output PDF filename |
| `num_pages` | int | 1 | Number of content pages |
| `page_size` | str/tuple | A4 | Device name or (width, height) in points |
| `page_pattern` | str | 'dots' | Pattern: 'dots', 'lines', 'grid', 'blank' |
| `spacing_mm` | float | 5 | Spacing between dots/lines/grid in mm |
| `dot_radius` | float | 0.5 | Dot radius in points (for dot pattern) |
| `margins` | dict | See below | Margins in mm: {'left', 'right', 'top', 'bottom'} |
| `left_margin_mm` | float | 5 | Left margin in mm |
| `right_margin_mm` | float | 5 | Right margin in mm |
| `top_margin_mm` | float | 5 | Top margin in mm |
| `bottom_margin_mm` | float | 5 | Bottom margin in mm |
| `page_number_position` | str | 'lower-left' | Page number position or None |
| `include_title_page` | bool | True | Include title page |
| `include_toc` | bool | True | Include table of contents |
| `toc_line_spacing_mm` | float | 8 | TOC line spacing in mm |

### Device Name Aliases

You can use either full names or short aliases:
- `remarkable1` or `rm1`
- `remarkable2` or `rm2`
- `remarkablepro` or `pro`
- `remarkablemove` or `move`
- `booxnoteair`, `booxnoteair3`, `booxnoteair3c`, `booxnoteair4c`
- `booxgo`, `booxmaxlumi`, `booxnotemax`, `booxtabminic`
- `supernotea5x`, `supernotea6x`, `supernotea6x2`, `supernotemanta`

## Project Structure

```
Notebook-Templates/
├── pdf_notebook.py           # Main Python module
├── pdf-notebook.ipynb        # Jupyter notebook with examples
├── toc-notebook/             # Generated PDFs (created automatically)
├── .gitignore               # Git ignore rules
├── .vscode/                 # VSCode settings
└── README.md                # This file
```

## Advanced Usage

### Dynamic Margin Manipulation

```python
generator = PDFHyperlinkedNotebookGenerator(filename="notebook.pdf", num_pages=50)

# Get current margins
print(generator.get_margins())
# {'left': 5, 'right': 5, 'top': 5, 'bottom': 5}

# Update margins before generating
generator.set_margins(left=10, right=10)
generator.set_margins(margins={'top': 15, 'bottom': 15})
generator.generate()
```

### Custom Page Sizes

```python
from reportlab.lib.units import mm

# Custom size (width, height) in points
custom_size = (200 * mm, 250 * mm)
generator = PDFHyperlinkedNotebookGenerator(
    filename="custom.pdf",
    page_size=custom_size,
    num_pages=50
)
```

### List Supported Devices and Patterns

```python
batch = PDFNotebookBatchGenerator()

print("Devices:", batch.list_devices())
print("Patterns:", batch.list_patterns())
```

## Interactive Examples

Open `pdf-notebook.ipynb` in Jupyter Notebook to explore interactive examples:

```bash
jupyter notebook pdf-notebook.ipynb
```

The notebook includes examples for:
- Batch generation
- Selective device/pattern generation
- Custom single PDF creation
- Accessing class constants
- Dynamic margin manipulation

## Generated File Names

Batch generation creates files with the format:
```
[Device Name] - [Pattern].pdf
```

Examples:
- `reMarkable 2 - Dots.pdf`
- `Onyx Boox Note Air 3 - Lines.pdf`
- `reMarkable Paper Pro - Grid.pdf`

## Features in Detail

### Hyperlinked Navigation
- **Page Numbers**: Click any page number to jump to the TOC
- **Table of Contents**: Click any TOC entry to jump to that page
- **Bookmarks**: PDF bookmarks for easy navigation in PDF readers

### Title Page
Automatically generated title page includes fields for:
- Notebook title
- Description (purpose)
- Author
- Date From / Date To
- Tags

All fields are editable in the PDF after generation.

### Typography
- **Content Pages**: Arial font for clean, readable page numbers
- **Title & TOC**: EB Garamond serif font for elegant appearance
- **Fallback**: Uses Helvetica if EB Garamond is unavailable

## Performance

Typical generation times:
- 100 pages: ~2-3 seconds
- 256 pages: ~5-7 seconds
- Batch (all devices/patterns): ~2-3 minutes

## Troubleshooting

### Font Warnings
If you see warnings about EB Garamond font:
```
Could not find EB Garamond font, using Helvetica as fallback
```
This is normal. The generator will use Helvetica for title/TOC pages instead.

### Import Errors
```
ModuleNotFoundError: No module named 'reportlab'
```
Install reportlab: `pip install reportlab`

### Canvas Initialization
The canvas is automatically initialized when creating a generator instance. No manual setup required.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup

```bash
git clone https://github.com/yourusername/Notebook-Templates.git
cd Notebook-Templates
pip install reportlab
```

### Running Tests

```bash
python pdf_notebook.py
```

This will generate sample PDFs in the `toc-notebook/` directory.

## License

This project is available under the MIT License. See LICENSE file for details.

## Acknowledgments

- Built with [ReportLab](https://www.reportlab.com/) PDF library
- Typography uses [EB Garamond](https://fonts.google.com/specimen/EB+Garamond) font
- Designed for reMarkable and Onyx Boox e-ink tablets

## Support

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Made with ❤️ for the e-ink tablet community**

