# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import datetime

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------

project = 'NHS_postprocessing'
copyright = f'{datetime.datetime.now().year}, Uchechukwu Udenze'
author = 'Uchechukwu Udenze'
version = {}
with open("../../postprocessinglib/__version__.py", "r") as fp:
    exec(fp.read(), version)
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_automodapi.automodapi',
    'sphinx.ext.autodoc',  # autodocument
    'sphinx.ext.napoleon',  # google and numpy doc string support
    'sphinx.ext.mathjax',  # latex rendering of equations using MathJax
    'nbsphinx',  # for direct embedding of jupyter notebooks into sphinx docs
    'nbsphinx_link'  # to be able to include notebooks from outside of the docs folder
    ]

templates_path = ['_templates']
exclude_patterns = ['**.ipynb_checkpoints', '_build']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']

# -- Napoleon autodoc options -------------------------------------------------
napoleon_numpy_docstring = True
