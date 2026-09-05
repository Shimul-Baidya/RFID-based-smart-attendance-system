import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('..'))

project = 'RFID Attendance System'
copyright = '2026, Shimul Baidya'
author = 'Shimul Baidya'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

