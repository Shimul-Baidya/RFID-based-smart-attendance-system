"""Sphinx configuration for RFID Based Smart Attendance System."""

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("../.."))

import app.models  # noqa: F401

project = 'RFID Based Smart Attendance System'
copyright = '2026, Md. Ahad Siddiki'
author = 'Md. Ahad Siddiki'
release = '1.0'

# Enable autodoc and docstring formatting
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ['_templates']
exclude_patterns = []

language = 'en'

html_theme = 'alabaster'
html_static_path = ['_static']
