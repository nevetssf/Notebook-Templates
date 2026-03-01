"""
PDF Notebook Generator Module

This module provides a class-based interface for generating PDF notebooks
with various patterns (dots, lines, grids, or blank pages) suitable for
e-ink tablets like reMarkable and Onyx Boox devices.

Classes
-------
PDFHyperlinkedNotebookGenerator : Main class for generating single PDF notebooks
PDFNotebookBatchGenerator : Class for batch generation of multiple PDFs

Usage Examples
--------------

Basic usage with defaults:
    >>> from pdf_notebook import PDFHyperlinkedNotebookGenerator
    >>> generator = PDFHyperlinkedNotebookGenerator(
    ...     filename="notebook.pdf",
    ...     num_pages=100,
    ...     page_size='remarkable2'
    ... )
    >>> generator.generate()

Using custom margins (as a dict):
    >>> margins = {'left': 10, 'right': 10, 'top': 15, 'bottom': 15}
    >>> generator = PDFHyperlinkedNotebookGenerator(
    ...     filename="notebook.pdf",
    ...     num_pages=100,
    ...     page_size='booxnoteair',
    ...     margins=margins,
    ...     page_pattern='lines'
    ... )
    >>> generator.generate()

Using individual margin parameters:
    >>> generator = PDFHyperlinkedNotebookGenerator(
    ...     filename="notebook.pdf",
    ...     num_pages=100,
    ...     left_margin_mm=8,
    ...     right_margin_mm=8,
    ...     page_pattern='grid'
    ... )
    >>> generator.generate()

Accessing class defaults:
    >>> print(PDFHyperlinkedNotebookGenerator.DEFAULT_MARGINS)
    {'left': 5, 'right': 5, 'top': 5, 'bottom': 5}
    >>> print(PDFHyperlinkedNotebookGenerator.DEFAULT_SPACING)
    5

Modifying margins after initialization:
    >>> generator = PDFHyperlinkedNotebookGenerator(filename="notebook.pdf", num_pages=50)
    >>> print(generator.get_margins())
    {'left': 5, 'right': 5, 'top': 5, 'bottom': 5}
    >>> generator.set_margins(left=10, right=10)
    >>> generator.set_margins(margins={'top': 15, 'bottom': 15})
    >>> generator.generate()

Batch generation for multiple devices and patterns:
    >>> from pdf_notebook import PDFNotebookBatchGenerator
    >>> batch = PDFNotebookBatchGenerator(
    ...     num_pages=256,
    ...     page_number_position='lower-left'
    ... )
    >>> stats = batch.generate_all()
    >>> print(f"Generated {stats['generated']} PDFs")

Generate for specific devices only:
    >>> batch = PDFNotebookBatchGenerator(
    ...     devices=['remarkable2', 'booxnoteair'],
    ...     patterns=['dots', 'lines'],
    ...     num_pages=100
    ... )
    >>> batch.generate_all()

Generate a single device/pattern combination:
    >>> batch = PDFNotebookBatchGenerator()
    >>> batch.generate_single('remarkable2', 'dots')
"""

import os
from reportlab.lib.pagesizes import A4, letter, A5, legal
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PDFHyperlinkedNotebookGenerator:
    """
    A class for generating PDF notebooks with customizable patterns and layouts.
    
    Supports multiple e-ink tablet formats including reMarkable and Onyx Boox devices,
    as well as standard paper sizes (A4, Letter, etc.).
    """
    
    # Device page sizes (width x height in mm, converted to points)
    DEVICE_SIZES = {
        # reMarkable devices
        'remarkable1': (157 * mm, 210 * mm),      # reMarkable 1: 10.3" display
        'remarkable2': (157 * mm, 210 * mm),      # reMarkable 2: 10.3" display
        'remarkablemove': (91 * mm, 162 * mm),    # reMarkable Paper Pro Move: 7.3" display
        'remarkablepro': (179 * mm, 239 * mm),    # reMarkable Paper Pro: 11.8" display
        # Aliases
        'rm1': (157 * mm, 210 * mm),
        'rm2': (157 * mm, 210 * mm),
        'move': (91 * mm, 162 * mm),
        'pro': (179 * mm, 239 * mm),
        # Onyx Boox devices
        'booxnoteair': (157 * mm, 209 * mm),      # Onyx Boox Note Air: 10.3" display
        'booxmaxlumi': (203 * mm, 270 * mm),      # Onyx Boox Max Lumi: 13.3" display
        'booxnoteair3c': (157 * mm, 209 * mm),    # Onyx Boox Note Air 3C: 10.3" display
        'booxnoteair3': (157 * mm, 209 * mm),     # Onyx Boox Note Air 3: 10.3" display
        'booxnoteair4c': (157 * mm, 209 * mm),    # Onyx Boox Note Air 4C: 10.3" display
        'booxtabminic': (119 * mm, 158 * mm),     # Onyx Boox Tab Mini C: 7.8" display
        'booxnotemax': (203 * mm, 270 * mm),      # Onyx Boox Note Max: 13.3" display
        'booxgo103': (157 * mm, 209 * mm),        # Onyx Boox Go 10.3: 10.3" display
        # Supernote devices
        'supernotea5x': (158 * mm, 210 * mm),     # Supernote A5X: 10.3" display, 226 PPI
        'supernotea6x': (119 * mm, 159 * mm),     # Supernote A6X: 7.8" display, 300 PPI
        'supernotea6x2': (119 * mm, 159 * mm),    # Supernote A6X2 (Nomad): 7.8" display, 300 PPI
        'supernotemanta': (163 * mm, 217 * mm),   # Supernote A5X2 (Manta): 10.7" display, 300 PPI
    }
    
    DEVICE_DISPLAY_NAMES = {
        'remarkable1': 'reMarkable 1',
        'rm1': 'reMarkable 1',
        'remarkable2': 'reMarkable 2',
        'rm2': 'reMarkable 2',
        'remarkablemove': 'reMarkable Paper Pro Move',
        'move': 'reMarkable Paper Pro Move',
        'remarkablepro': 'reMarkable Paper Pro',
        'pro': 'reMarkable Paper Pro',
        'booxnoteair': 'Onyx Boox Note Air',
        'booxmaxlumi': 'Onyx Boox Max Lumi',
        'booxnoteair3c': 'Onyx Boox Note Air 3C',
        'booxnoteair3': 'Onyx Boox Note Air 3',
        'booxnoteair4c': 'Onyx Boox Note Air 4C',
        'booxtabminic': 'Onyx Boox Tab Mini C',
        'booxnotemax': 'Onyx Boox Note Max',
        'booxgo103': 'Onyx Boox Go 10.3',
        'supernotea5x': 'Supernote A5X',
        'supernotea6x': 'Supernote A6X',
        'supernotea6x2': 'Supernote A6X2 (Nomad)',
        'supernotemanta': 'Supernote A5X2 (Manta)',
        'a4': 'A4',
        'letter': 'Letter',
        'a5': 'A5',
        'legal': 'Legal',
    }
    
    VALID_PAGE_POSITIONS = ['upper-right', 'upper-middle', 'lower-right', 
                           'lower-middle', 'lower-left', None]
    VALID_PATTERNS = ['dots', 'lines', 'grid', 'blank']
    
    # Default settings
    DEFAULT_MARGINS = {
        'left': 5,      # mm
        'right': 5,     # mm
        'top': 5,       # mm
        'bottom': 5     # mm
    }
    
    DEFAULT_SPACING = 5         # mm
    DEFAULT_DOT_RADIUS = 0.5    # points
    DEFAULT_TOC_LINE_SPACING = 8  # mm
    
    def __init__(self, filename, spacing_mm=None, num_pages=1, page_size=A4, 
                 dot_radius=None, page_number_position='lower-left',
                 margins=None, left_margin_mm=None, right_margin_mm=None, 
                 top_margin_mm=None, bottom_margin_mm=None, 
                 include_title_page=True, include_toc=True,
                 toc_line_spacing_mm=None, page_pattern='dots'):
        """
        Initialize the PDF Notebook Generator.
        
        Parameters:
        -----------
        filename : str
            Output PDF filename
        spacing_mm : float, optional
            Spacing between dots/lines/grid in millimeters (default: 5mm)
        num_pages : int
            Number of content pages to generate (default: 1)
        page_size : str or tuple
            Page size as device name string or (width, height) tuple in points
        dot_radius : float, optional
            Radius of each dot in points (default: 0.5)
        page_number_position : str or None
            Position of page numbers: 'upper-right', 'upper-middle', 'lower-right',
            'lower-middle', 'lower-left', or None to skip page numbering
        margins : dict, optional
            Dictionary with keys 'left', 'right', 'top', 'bottom' in mm.
            If provided, overrides individual margin parameters.
        left_margin_mm : float, optional
            Left margin in millimeters (default: 5mm)
        right_margin_mm : float, optional
            Right margin in millimeters (default: 5mm)
        top_margin_mm : float, optional
            Top margin in millimeters (default: 5mm)
        bottom_margin_mm : float, optional
            Bottom margin in millimeters (default: 5mm)
        include_title_page : bool
            Whether to include a title page (default: True)
        include_toc : bool
            Whether to include a table of contents (default: True)
        toc_line_spacing_mm : float, optional
            Line spacing for TOC entries in millimeters (default: 8mm)
        page_pattern : str
            Pattern to draw: 'dots', 'lines', 'grid', or 'blank' (default: 'dots')
        """
        self.filename = filename
        self.num_pages = num_pages
        self.page_number_position = page_number_position
        self.include_title_page = include_title_page
        self.include_toc = include_toc
        self.page_pattern = page_pattern
        
        # Set defaults for optional parameters
        self.spacing_mm = spacing_mm if spacing_mm is not None else self.DEFAULT_SPACING
        self.dot_radius = dot_radius if dot_radius is not None else self.DEFAULT_DOT_RADIUS
        self.toc_line_spacing_mm = (toc_line_spacing_mm if toc_line_spacing_mm is not None 
                                   else self.DEFAULT_TOC_LINE_SPACING)
        
        # Handle margins - prioritize margins dict, then individual params, then defaults
        if margins is not None:
            self.margins = margins.copy()
        else:
            self.margins = {}
            if left_margin_mm is not None:
                self.margins['left'] = left_margin_mm
            if right_margin_mm is not None:
                self.margins['right'] = right_margin_mm
            if top_margin_mm is not None:
                self.margins['top'] = top_margin_mm
            if bottom_margin_mm is not None:
                self.margins['bottom'] = bottom_margin_mm
        
        # Fill in any missing margins with defaults
        for key in ['left', 'right', 'top', 'bottom']:
            if key not in self.margins:
                self.margins[key] = self.DEFAULT_MARGINS[key]
        
        # Set individual margin attributes for convenience
        self.left_margin_mm = self.margins['left']
        self.right_margin_mm = self.margins['right']
        self.top_margin_mm = self.margins['top']
        self.bottom_margin_mm = self.margins['bottom']
        
        # Store original page size for display purposes
        self.original_page_size_str = page_size if isinstance(page_size, str) else None
        
        # Validate inputs
        self._validate_inputs()
        
        # Resolve page size
        self.page_size = self._resolve_page_size(page_size)
        self.page_width, self.page_height = self.page_size
        
        # Register fonts
        self.font_name = self._register_sans_font()
        self.serif_font_name, self.serif_font_embedded = self._register_serif_font()
        
        # Convert measurements to points
        self.spacing = self.spacing_mm * mm
        self.left_margin = self.left_margin_mm * mm
        self.right_margin = self.right_margin_mm * mm
        self.top_margin = self.top_margin_mm * mm
        self.bottom_margin = self.bottom_margin_mm * mm
        
        # State tracking
        self.actual_page_num = 1
        self.toc_page_map = {}
        
        # Initialize canvas
        self.canvas = canvas.Canvas(self.filename, pagesize=self.page_size)
    
    def get_margins(self):
        """
        Get current margins as a dictionary.
        
        Returns:
        --------
        dict : Dictionary with keys 'left', 'right', 'top', 'bottom' in mm
        """
        return self.margins.copy()
    
    def set_margins(self, margins=None, left=None, right=None, top=None, bottom=None):
        """
        Update margins after initialization.
        
        Parameters:
        -----------
        margins : dict, optional
            Dictionary with keys 'left', 'right', 'top', 'bottom' in mm
        left : float, optional
            Left margin in mm
        right : float, optional
            Right margin in mm
        top : float, optional
            Top margin in mm
        bottom : float, optional
            Bottom margin in mm
        """
        if margins is not None:
            self.margins.update(margins)
        
        if left is not None:
            self.margins['left'] = left
        if right is not None:
            self.margins['right'] = right
        if top is not None:
            self.margins['top'] = top
        if bottom is not None:
            self.margins['bottom'] = bottom
        
        # Update individual attributes
        self.left_margin_mm = self.margins['left']
        self.right_margin_mm = self.margins['right']
        self.top_margin_mm = self.margins['top']
        self.bottom_margin_mm = self.margins['bottom']
        
        # Update point values
        self.left_margin = self.left_margin_mm * mm
        self.right_margin = self.right_margin_mm * mm
        self.top_margin = self.top_margin_mm * mm
        self.bottom_margin = self.bottom_margin_mm * mm
    
    def _validate_inputs(self):
        """Validate input parameters."""
        if self.page_number_position not in self.VALID_PAGE_POSITIONS:
            raise ValueError(
                f"Invalid page_number_position: {self.page_number_position}. "
                f"Must be one of {self.VALID_PAGE_POSITIONS}"
            )
        
        if self.page_pattern not in self.VALID_PATTERNS:
            raise ValueError(
                f"Invalid page_pattern: {self.page_pattern}. "
                f"Must be one of {self.VALID_PATTERNS}"
            )
    
    def _resolve_page_size(self, page_size):
        """Resolve page size string to dimensions."""
        if isinstance(page_size, str):
            page_size_lower = page_size.lower()
            if page_size_lower in self.DEVICE_SIZES:
                return self.DEVICE_SIZES[page_size_lower]
            else:
                raise ValueError(
                    f"Unknown page size: {page_size}. "
                    f"Use a device name or a tuple (width, height)."
                )
        return page_size
    
    def _register_sans_font(self):
        """Register Arial font, fallback to Helvetica."""
        font_name = "Helvetica"
        try:
            arial_paths = [
                "C:\\Windows\\Fonts\\arial.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/usr/share/fonts/truetype/msttcorefonts/arial.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
            ]
            
            for path in arial_paths:
                if os.path.exists(path):
                    pdfmetrics.registerFont(TTFont('Arial', path))
                    font_name = "Arial"
                    break
        except:
            pass
        return font_name
    
    def _register_serif_font(self):
        """Register EB Garamond font, fallback to Helvetica."""
        serif_font_name = "Helvetica"
        serif_font_embedded = False
        try:
            garamond_paths = [
                "C:\\Windows\\Fonts\\EBGaramond-Regular.ttf",
                "/Library/Fonts/EBGaramond-Regular.ttf",
                "/System/Library/Fonts/Supplemental/EBGaramond-Regular.ttf",
                "~/Library/Fonts/EBGaramond-Regular.ttf",
                "~/Library/Fonts/EBGaramond-VariableFont_wght.ttf",
                "/usr/share/fonts/truetype/eb-garamond/EBGaramond-Regular.ttf",
                "/usr/share/fonts/truetype/ebgaramond/EBGaramond-Regular.ttf",
                "/usr/share/fonts/opentype/eb-garamond/EBGaramond-Regular.otf",
            ]
            
            for path in garamond_paths:
                expanded_path = os.path.expanduser(path)
                if os.path.exists(expanded_path):
                    pdfmetrics.registerFont(TTFont('EBGaramond', expanded_path))
                    serif_font_name = "EBGaramond"
                    serif_font_embedded = True
                    break
        except:
            pass
        return serif_font_name, serif_font_embedded
    
    def _get_display_name(self):
        """Get display name for the page size."""
        if self.original_page_size_str:
            return self.DEVICE_DISPLAY_NAMES.get(
                self.original_page_size_str.lower(),
                self.original_page_size_str
            )
        return 'Custom Size'
    
    def _create_title_page(self):
        """Create the title page."""
        c = self.canvas
        
        # Bookmark the title page
        c.bookmarkPage("title_page")
        c.bookmarkPage(f"page_num_{self.actual_page_num}")
        
        # Add "Linked Workbook" header at the top
        header_y = self.page_height - self.top_margin - (20 * mm)
        c.setFont(self.serif_font_name, 16)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawString(self.left_margin, header_y, "Linked Workbook")
        c.setFillColorRGB(0, 0, 0)
        
        # Form fields
        y_position = self.page_height - self.top_margin - 20 - (30 * mm)
        line_length = self.page_width - self.left_margin - self.right_margin
        label_x = self.left_margin
        
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.setFont(self.font_name, 7)
        
        # Title field
        c.line(label_x, y_position, label_x + line_length, y_position)
        y_position -= 12
        c.drawString(label_x, y_position, "Title")
        y_position -= 28
        
        # Owner field
        c.line(label_x, y_position, label_x + line_length, y_position)
        y_position -= 12
        c.drawString(label_x, y_position, "Owner")
        y_position -= 28
        
        # Description field (3 lines)
        c.line(label_x, y_position, label_x + line_length, y_position)
        y_position -= 20
        c.line(label_x, y_position, label_x + line_length, y_position)
        y_position -= 20
        c.line(label_x, y_position, label_x + line_length, y_position)
        y_position -= 12
        c.drawString(label_x, y_position, "Description")
        y_position -= 38
        
        # Date From field
        c.line(label_x, y_position, label_x + line_length, y_position)
        y_position -= 12
        c.drawString(label_x, y_position, "Date From")
        y_position -= 28
        
        # Date To field
        c.line(label_x, y_position, label_x + line_length, y_position)
        y_position -= 12
        c.drawString(label_x, y_position, "Date To")
        
        # Footer text
        size_display = self._get_display_name()
        template_text = f"For {size_display}"
        c.setFont("Helvetica-Oblique", 6)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(self.left_margin, 10 * mm, template_text)
        
        # Reset styles
        c.setFillColorRGB(0, 0, 0)
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1)
        
        c.showPage()
        self.actual_page_num += 1
    
    def _calculate_toc_pages(self):
        """Calculate number of TOC pages needed."""
        toc_line_spacing = self.toc_line_spacing_mm * mm
        toc_top_spacing = 20 + (10 * mm)
        toc_header_spacing = 20
        
        first_page_available_height = (
            self.page_height - self.top_margin - self.bottom_margin - 
            (5 * mm) - (20 * mm) - toc_header_spacing
        )
        other_page_available_height = (
            self.page_height - self.top_margin - self.bottom_margin - toc_top_spacing
        )
        
        first_page_entries = int(first_page_available_height / toc_line_spacing)
        entries_per_other_page = int(other_page_available_height / toc_line_spacing)
        
        if self.num_pages <= first_page_entries:
            return 1
        else:
            remaining_entries = self.num_pages - first_page_entries
            return 1 + ((remaining_entries + entries_per_other_page - 1) // 
                       entries_per_other_page)
    
    def _create_toc(self):
        """Create the table of contents."""
        c = self.canvas
        toc_line_spacing = self.toc_line_spacing_mm * mm
        toc_top_spacing = 20 + (10 * mm)
        toc_header_spacing = 20
        
        first_page_available_height = (
            self.page_height - self.top_margin - self.bottom_margin - 
            (5 * mm) - (20 * mm) - toc_header_spacing
        )
        other_page_available_height = (
            self.page_height - self.top_margin - self.bottom_margin - toc_top_spacing
        )
        
        first_page_entries = int(first_page_available_height / toc_line_spacing)
        entries_per_other_page = int(other_page_available_height / toc_line_spacing)
        
        num_toc_pages = self._calculate_toc_pages()
        first_content_page_num = self.actual_page_num + num_toc_pages
        
        entry_idx = 0
        for toc_page_idx in range(num_toc_pages):
            current_toc_page_num = self.actual_page_num
            toc_page_key = f"toc_page_{toc_page_idx + 1}"
            
            c.bookmarkPage(toc_page_key)
            c.bookmarkPage(f"page_num_{current_toc_page_num}")
            
            c.setLineWidth(0.5)
            c.setStrokeColorRGB(0.7, 0.7, 0.7)
            
            # Title on first TOC page
            if toc_page_idx == 0:
                c.setFont(self.serif_font_name, 16)
                c.setFillColorRGB(0.4, 0.4, 0.4)
                title_y_position = self.page_height - self.top_margin - (15 * mm)
                c.drawString(self.left_margin, title_y_position, "Table of Contents")
                c.setFillColorRGB(0, 0, 0)
                y_pos = title_y_position - toc_header_spacing
                entries_this_page = first_page_entries
            else:
                y_pos = self.page_height - self.top_margin - toc_top_spacing
                entries_this_page = entries_per_other_page
            
            # Draw TOC entries
            for _ in range(entries_this_page):
                if entry_idx >= self.num_pages:
                    break
                
                dot_page_num = entry_idx + 1
                display_page_num = entry_idx + 1
                self.toc_page_map[dot_page_num] = toc_page_key
                
                # Page number
                c.setFont(self.font_name, 8)
                c.setFillColorRGB(0, 0, 0)
                page_num_x = self.page_width - self.right_margin + (2 * mm)
                c.drawRightString(page_num_x, y_pos + 5, str(display_page_num))
                
                # Line for entry
                line_start = self.left_margin
                line_end = page_num_x + 2
                c.line(line_start, y_pos, line_end, y_pos)
                
                # Clickable link
                link_rect = (line_start, y_pos - 5, page_num_x, 
                           y_pos + toc_line_spacing - 5)
                c.linkRect("", f"page_{dot_page_num}", link_rect, relative=0)
                
                y_pos -= toc_line_spacing
                entry_idx += 1
            
            # Navigation links
            self._add_toc_navigation(toc_page_idx, num_toc_pages, current_toc_page_num)
            
            c.setFillColorRGB(0, 0, 0)
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(1)
            
            c.showPage()
            self.actual_page_num += 1
    
    def _add_toc_navigation(self, toc_page_idx, num_toc_pages, current_toc_page_num):
        """Add navigation links at bottom of TOC page."""
        c = self.canvas
        nav_y_position = 12 * mm
        c.setFont(self.font_name, 8)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        
        # Previous link
        if toc_page_idx > 0:
            prev_text = "Previous"
            prev_x = self.left_margin
            c.drawString(prev_x, nav_y_position, prev_text)
            text_width = c.stringWidth(prev_text, self.font_name, 8)
            link_rect = (prev_x - 2, nav_y_position - 2, 
                        prev_x + text_width + 2, nav_y_position + 12)
            c.linkRect("", f"page_num_{current_toc_page_num - 1}", 
                      link_rect, relative=0)
        
        # Cover link
        if self.include_title_page:
            cover_text = "Cover"
            cover_width = c.stringWidth(cover_text, self.font_name, 8)
            cover_x = (self.page_width - cover_width) / 2
            c.drawString(cover_x, nav_y_position, cover_text)
            link_rect = (cover_x - 2, nav_y_position - 2, 
                        cover_x + cover_width + 2, nav_y_position + 12)
            c.linkRect("", "title_page", link_rect, relative=0)
        
        # Next link
        if toc_page_idx < num_toc_pages - 1:
            next_text = "Next"
            next_width = c.stringWidth(next_text, self.font_name, 8)
            next_x = self.page_width - self.right_margin - next_width
            c.drawString(next_x, nav_y_position, next_text)
            link_rect = (next_x - 2, nav_y_position - 2, 
                        next_x + next_width + 2, nav_y_position + 12)
            c.linkRect("", f"page_num_{current_toc_page_num + 1}", 
                      link_rect, relative=0)
    
    def _draw_dots_pattern(self):
        """Draw dot grid pattern."""
        c = self.canvas
        x = self.left_margin
        while x <= self.page_width - self.right_margin:
            y = self.bottom_margin
            while y <= self.page_height - self.top_margin:
                c.circle(x, y, self.dot_radius, stroke=0, fill=1)
                y += self.spacing
            x += self.spacing
    
    def _draw_lines_pattern(self):
        """Draw horizontal lines pattern."""
        c = self.canvas
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        
        y = self.bottom_margin
        while y <= self.page_height - self.top_margin:
            c.line(self.left_margin, y, self.page_width - self.right_margin, y)
            y += self.spacing
        
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1)
    
    def _draw_grid_pattern(self):
        """Draw grid pattern."""
        c = self.canvas
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        
        available_width = self.page_width - self.left_margin - self.right_margin
        available_height = self.page_height - self.top_margin - self.bottom_margin
        
        num_squares_horizontal = int(available_width / self.spacing)
        num_squares_vertical = int(available_height / self.spacing)
        
        grid_width = num_squares_horizontal * self.spacing
        grid_height = num_squares_vertical * self.spacing
        
        grid_start_x = self.left_margin + (available_width - grid_width) / 2
        grid_start_y = self.bottom_margin + (available_height - grid_height) / 2
        
        # Horizontal lines
        for i in range(num_squares_vertical + 1):
            y = grid_start_y + (i * self.spacing)
            c.line(grid_start_x, y, grid_start_x + grid_width, y)
        
        # Vertical lines
        for i in range(num_squares_horizontal + 1):
            x = grid_start_x + (i * self.spacing)
            c.line(x, grid_start_y, x, grid_start_y + grid_height)
        
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1)
    
    def _draw_page_pattern(self):
        """Draw the specified pattern on the current page."""
        if self.page_pattern == 'dots':
            self._draw_dots_pattern()
        elif self.page_pattern == 'lines':
            self._draw_lines_pattern()
        elif self.page_pattern == 'grid':
            self._draw_grid_pattern()
        # 'blank' draws nothing
    
    def _add_page_number(self, display_page_num):
        """Add page number to the current page."""
        if self.page_number_position is None:
            return
        
        c = self.canvas
        font_size = 18  # Increased from 14
        c.setFont(self.font_name, font_size)
        c.setFillColorRGB(0.55, 0.55, 0.55)
        page_num_text = str(display_page_num)
        text_width = c.stringWidth(page_num_text, self.font_name, font_size)
        
        page_num_bottom = 11 * mm
        right_offset = 3 * mm  # Offset to move page number slightly to the right
        
        # Calculate position based on setting
        if self.page_pattern == 'grid' and self.page_number_position == 'lower-right':
            available_width = self.page_width - self.left_margin - self.right_margin
            num_squares_horizontal = int(available_width / self.spacing)
            grid_width = num_squares_horizontal * self.spacing
            grid_start_x = self.left_margin + (available_width - grid_width) / 2
            grid_end_x = grid_start_x + grid_width
            x_pos = grid_end_x - text_width - (3 * mm) + right_offset
            y_pos = page_num_bottom
        elif self.page_number_position == 'lower-left':
            x_pos = self.left_margin + right_offset
            y_pos = page_num_bottom
        elif self.page_number_position == 'lower-right':
            x_pos = self.page_width - self.right_margin - text_width + right_offset
            y_pos = page_num_bottom
        elif self.page_number_position == 'lower-middle':
            x_pos = (self.page_width - text_width) / 2 + right_offset
            y_pos = page_num_bottom
        elif self.page_number_position == 'upper-right':
            x_pos = self.page_width - self.right_margin - text_width + right_offset
            y_pos = self.page_height - self.top_margin / 2 - 10
        elif self.page_number_position == 'upper-middle':
            x_pos = (self.page_width - text_width) / 2 + right_offset
            y_pos = self.page_height - self.top_margin / 2 - 10
        else:
            return
        
        c.drawString(x_pos, y_pos, page_num_text)
        
        c.setFillColorRGB(0, 0, 0)
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1)
        
        # Make page number clickable to TOC
        if self.include_toc:
            dot_page_num = display_page_num
            if dot_page_num in self.toc_page_map:
                link_rect = (x_pos - 2, y_pos - 2, x_pos + text_width + 2, y_pos + font_size)
                c.linkRect("", self.toc_page_map[dot_page_num], link_rect, relative=0)
    
    def _create_content_pages(self):
        """Create all content pages."""
        c = self.canvas
        
        for page in range(self.num_pages):
            dot_page_num = page + 1
            display_page_num = page + 1
            
            c.bookmarkPage(f"page_{dot_page_num}")
            c.bookmarkPage(f"page_num_{self.actual_page_num}")
            
            self._draw_page_pattern()
            self._add_page_number(display_page_num)
            
            if page < self.num_pages - 1:
                c.showPage()
                self.actual_page_num += 1
    
    def _print_summary(self):
        """Print generation summary."""
        total_pages = self.num_pages
        if self.include_title_page:
            total_pages += 1
        if self.include_toc:
            num_toc_pages = self._calculate_toc_pages()
            total_pages += num_toc_pages
        
        print(f"PDF created: {self.filename}")
        print(f"  - Content pages: {self.num_pages}")
        if self.include_title_page:
            print(f"  - Title page: Yes")
        if self.include_toc:
            num_toc_pages = self._calculate_toc_pages()
            print(f"  - Table of Contents: Yes ({num_toc_pages} page(s))")
        print(f"  - Total pages in PDF: {total_pages}")
        print(f"  - Page pattern: {self.page_pattern}")
        if self.page_pattern in ['dots', 'lines', 'grid']:
            print(f"  - Pattern spacing: {self.spacing_mm}mm")
        print(f"  - Page size: {self.page_width/mm:.1f}mm x {self.page_height/mm:.1f}mm")
        print(f"  - Margins: L={self.left_margin_mm}mm, R={self.right_margin_mm}mm, "
              f"T={self.top_margin_mm}mm, B={self.bottom_margin_mm}mm")
        print(f"  - Page number position: "
              f"{self.page_number_position if self.page_number_position else 'None'}")
        print(f"  - Font used: {self.font_name}")
        if self.serif_font_embedded:
            print(f"  - Serif font used: {self.serif_font_name} (embedded in PDF)")
        else:
            print(f"  - Serif font used: {self.serif_font_name} (fallback)")
    
    def generate(self):
        """
        Generate the PDF notebook.
        
        This is the main method that orchestrates the PDF creation process.
        """
        # Create title page if requested
        if self.include_title_page:
            self._create_title_page()
        
        # Create table of contents if requested
        if self.include_toc:
            self._create_toc()
        
        # Create content pages
        self._create_content_pages()
        
        # Save the PDF
        self.canvas.save()
        
        # Print summary
        self._print_summary()


class PDFNotebookBatchGenerator:
    """
    A class for generating multiple PDF notebooks in batch.
    
    This class facilitates generating PDFs for multiple devices and patterns
    with consistent settings.
    """
    
    # Default devices to generate
    DEFAULT_DEVICES = [
        'remarkable1', 'remarkable2', 'move', 'pro',
        'booxnoteair', 'booxmaxlumi', 'booxnoteair3c', 'booxnoteair3',
        'booxnoteair4c', 'booxtabminic', 'booxnotemax', 'booxgo103',
        'supernotea5x', 'supernotea6x', 'supernotea6x2', 'supernotemanta'
    ]
    
    # Default patterns to generate
    DEFAULT_PATTERNS = ['dots', 'lines', 'grid', 'blank']
    
    PATTERN_DISPLAY_NAMES = {
        'dots': 'Dots',
        'lines': 'Lines',
        'grid': 'Grid',
        'blank': 'Blank'
    }
    
    def __init__(self, devices=None, patterns=None, num_pages=256,
                 page_number_position='lower-left', margins=None,
                 spacing_mm=None, dot_radius=None, toc_line_spacing_mm=None,
                 include_title_page=True, include_toc=True,
                 output_dir=None):
        """
        Initialize the batch generator.
        
        Parameters:
        -----------
        devices : list of str, optional
            List of device names to generate PDFs for (default: all supported)
        patterns : list of str, optional
            List of patterns to generate (default: all patterns)
        num_pages : int
            Number of content pages per notebook (default: 256)
        page_number_position : str
            Position of page numbers (default: 'lower-left')
        margins : dict, optional
            Margins dict to use for all notebooks
        spacing_mm : float, optional
            Pattern spacing in mm
        dot_radius : float, optional
            Dot radius in points
        toc_line_spacing_mm : float, optional
            TOC line spacing in mm
        include_title_page : bool
            Whether to include title page (default: True)
        include_toc : bool
            Whether to include table of contents (default: True)
        output_dir : str, optional
            Output directory for generated PDFs (default: current directory)
        """
        self.devices = devices if devices is not None else self.DEFAULT_DEVICES.copy()
        self.patterns = patterns if patterns is not None else self.DEFAULT_PATTERNS.copy()
        self.num_pages = num_pages
        self.page_number_position = page_number_position
        self.margins = margins
        self.spacing_mm = spacing_mm
        self.dot_radius = dot_radius
        self.toc_line_spacing_mm = toc_line_spacing_mm
        self.include_title_page = include_title_page
        self.include_toc = include_toc
        self.output_dir = output_dir if output_dir is not None else ""
        
        # Create output directory if specified and doesn't exist
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Statistics
        self.generated_count = 0
        self.failed_count = 0
        self.failed_files = []
    
    def get_output_filename(self, device, pattern):
        """
        Generate output filename for a device and pattern combination.
        
        Parameters:
        -----------
        device : str
            Device name
        pattern : str
            Pattern name
            
        Returns:
        --------
        str : Output filename
        """
        device_display = PDFHyperlinkedNotebookGenerator.DEVICE_DISPLAY_NAMES.get(
            device, device
        )
        pattern_display = self.PATTERN_DISPLAY_NAMES.get(pattern, pattern)
        filename = f"{device_display} - {pattern_display}.pdf"
        
        if self.output_dir:
            filename = os.path.join(self.output_dir, filename)
        
        return filename
    
    def generate_single(self, device, pattern, verbose=True):
        """
        Generate a single PDF for a device and pattern.
        
        Parameters:
        -----------
        device : str
            Device name
        pattern : str
            Pattern name
        verbose : bool
            Whether to print progress (default: True)
            
        Returns:
        --------
        bool : True if successful, False otherwise
        """
        output_file = self.get_output_filename(device, pattern)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Generating {os.path.basename(output_file)}...")
            print(f"{'='*60}")
        
        try:
            generator = PDFHyperlinkedNotebookGenerator(
                filename=output_file,
                num_pages=self.num_pages,
                page_size=device,
                page_number_position=self.page_number_position,
                margins=self.margins,
                spacing_mm=self.spacing_mm,
                dot_radius=self.dot_radius,
                toc_line_spacing_mm=self.toc_line_spacing_mm,
                include_title_page=self.include_title_page,
                include_toc=self.include_toc,
                page_pattern=pattern
            )
            generator.generate()
            self.generated_count += 1
            return True
        except Exception as e:
            self.failed_count += 1
            self.failed_files.append((output_file, str(e)))
            if verbose:
                print(f"ERROR: Failed to generate {output_file}: {e}")
            return False
    
    def generate_all(self, verbose=True):
        """
        Generate all PDFs for all device and pattern combinations.
        
        Parameters:
        -----------
        verbose : bool
            Whether to print progress (default: True)
            
        Returns:
        --------
        dict : Statistics about the generation process
        """
        # Reset statistics
        self.generated_count = 0
        self.failed_count = 0
        self.failed_files = []
        
        total = len(self.devices) * len(self.patterns)
        
        for device in self.devices:
            for pattern in self.patterns:
                self.generate_single(device, pattern, verbose=verbose)
        
        # Print summary
        if verbose:
            print(f"\n{'='*60}")
            print(f"Batch Generation Complete!")
            print(f"{'='*60}")
            print(f"  - Successfully generated: {self.generated_count}/{total}")
            if self.failed_count > 0:
                print(f"  - Failed: {self.failed_count}")
                print(f"\nFailed files:")
                for filename, error in self.failed_files:
                    print(f"  - {filename}: {error}")
            print(f"{'='*60}")
        
        return {
            'total': total,
            'generated': self.generated_count,
            'failed': self.failed_count,
            'failed_files': self.failed_files.copy()
        }
    
    def generate_for_devices(self, devices, verbose=True):
        """
        Generate PDFs for specific devices (all patterns).
        
        Parameters:
        -----------
        devices : list of str
            List of device names
        verbose : bool
            Whether to print progress (default: True)
            
        Returns:
        --------
        dict : Statistics about the generation process
        """
        original_devices = self.devices
        self.devices = devices
        result = self.generate_all(verbose=verbose)
        self.devices = original_devices
        return result
    
    def generate_for_patterns(self, patterns, verbose=True):
        """
        Generate PDFs for specific patterns (all devices).
        
        Parameters:
        -----------
        patterns : list of str
            List of pattern names
        verbose : bool
            Whether to print progress (default: True)
            
        Returns:
        --------
        dict : Statistics about the generation process
        """
        original_patterns = self.patterns
        self.patterns = patterns
        result = self.generate_all(verbose=verbose)
        self.patterns = original_patterns
        return result
    
    def list_devices(self):
        """List all supported devices."""
        return list(PDFHyperlinkedNotebookGenerator.DEVICE_SIZES.keys())
    
    def list_patterns(self):
        """List all supported patterns."""
        return self.DEFAULT_PATTERNS.copy()


if __name__ == "__main__":
    # Example 1: Generate all PDFs using batch generator
    print("="*60)
    print("Batch PDF Generation Example")
    print("="*60)
    
    batch_generator = PDFNotebookBatchGenerator(
        num_pages=256,
        page_number_position='lower-left',
        output_dir='toc-notebook'  # Output to 'toc-notebook' directory (will be created if it doesn't exist)
        # margins={'left': 10, 'right': 10, 'top': 10, 'bottom': 10},  # Custom margins
    )
    
    # Generate all combinations
    stats = batch_generator.generate_all()
    
    # Example 2: Generate for specific devices only
    # batch_generator.generate_for_devices(['remarkable2', 'booxnoteair'])
    
    # Example 3: Generate for specific patterns only
    # batch_generator.generate_for_patterns(['dots', 'lines'])
    
    # Example 4: Generate a single PDF manually
    # generator = PDFHyperlinkedNotebookGenerator(
    #     filename="custom_notebook.pdf",
    #     num_pages=100,
    #     page_size='remarkable2',
    #     page_pattern='dots',
    #     margins={'left': 8, 'right': 8, 'top': 8, 'bottom': 8}
    # )
    # generator.generate()

