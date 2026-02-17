"""
Configuration file for PDF to Markdown converter
Customize conversion settings here
"""

# Font size thresholds for heading detection
HEADING_SIZES = {
    'h1': 20,  # Font size > 20 = H1
    'h2': 16,  # Font size > 16 = H2
    'h3': 14,  # Font size > 14 = H3
    'h4': 13,  # Font size > 13 = H4
}

# Conversion options
CONVERSION_OPTIONS = {
    'preserve_images': True,
    'extract_tables': True,
    'detect_lists': True,
    'include_metadata': True,
    'add_page_numbers': True,
    'clean_whitespace': True,
}

# Output formatting
OUTPUT_FORMAT = {
    'page_separator': '\n\n---\n*Page {page_num}*\n\n',
    'metadata_separator': '\n---\n\n',
    'max_consecutive_newlines': 3,
}

# Processing limits
PROCESSING_LIMITS = {
    'max_file_size_mb': 50,
    'timeout_seconds': 300,
}
