# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('_ext'))


# -- Project information -----------------------------------------------------

project = 'Weasel'
copyright = '2021, Steve Shillitoe, Joao Sousa and Steven Sourbron'
author = 'Steve Shillitoe, Joao Sousa and Steven Sourbron'

# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.doctest',
              'sphinx.ext.coverage', 
              'sphinx.ext.napoleon',
              'sphinx.ext.viewcode',
              'sphinx.ext.graphviz',
              'sphinx.ext.githubpages']
              
# ghissue config
github_url = "https://github.com/QIB-Sheffield/WEASEL"
github_project_url = "https://github.com/QIB-Sheffield/WEASEL"
edit_on_github_project = 'QIB-Sheffield/WEASEL'
edit_on_github_branch = 'master'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Do not include full module name
add_module_names = False

pygments_style = 'sphinx'

# If false, no module index is generated.
# Setting to false fixes double module listing under header
html_use_modindex = False

html_favicon = '../images/uni-sheffield-logo-16.ico'
# html_logo = None
html_show_sourcelink = False
html_context = {
"author": "Steve Shillitoe, Joao Sousa and Steven Sourbron",
"display_github": True, # Add 'Edit on Github' link instead of 'View page source'
"last_updated": True,
"commit": False,
}