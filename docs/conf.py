# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Pelican backend"
copyright = "2020, Open Contracting Partnership"
author = "Open Contracting Partnership"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
# Eduard Rüppell, Philipp Jakob Cretzschmar, Karl Heinrich Georg von Heyden & Friedrich Sigismund Leuckart,
# "Atlas zu der Reise im nördlichen Afrika" (1826-1828).
# Digitized by the Biodiversity Heritage Library (https://doi.org/10.5962/bhl.title.53779),
# courtesy of Field Museum of Natural History Library. Public domain. https://flic.kr/p/bAXJcz
html_logo = "_static/logo.jpg"

# -- Extension configuration -------------------------------------------------

autodoc_default_options = {
    "members": None,
    "member-order": "bysource",
}
autodoc_typehints = "description"

extlinks = {
    "issue": ("https://github.com/open-contracting/pelican-backend/issues/%s", "#%s"),
    "commit": ("https://github.com/open-contracting/pelican-backend/commit/%s", "%s"),
    "compare": ("https://github.com/open-contracting/pelican-backend/compare/%s", "%s"),
}
