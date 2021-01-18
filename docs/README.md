In order to generate/update the HTML documentation page, it's required to install the following:

`pip install -U sphinx`

`pip install sphinx_rtf_theme`

Before running any further commands, ensure that the "docs/docsource" folder only contains the files "conf.py" and "index.rst".

Also, ensure that the "docs" folder only contains the README.md file and the folders "_templates", "docsource" and "images".
Everything else should be deleted. If you see a large number of .html files, thses should be deleted as they will be generated again during the commands below.

Then, open a terminal and type the following commands within the Weasel parent folder:

`cd docs`

#`sphinx-apidoc -M -f -e -t .\_templates -o "docsource" ..`

`sphinx-apidoc -M -f -e -t ".\_templates" -o "docsource" "..\CoreModules" "..\CoreModules\pyqtgraph"`

`sphinx-apidoc -M -f -e -t ".\_templates" -o "docsource" "..\Developer" "..\Developer\External"`

`sphinx-apidoc -M -f -e -t ".\_templates" -o "docsource" "..\MenuItems" "..\MenuItems\Joao-Development"`

`sphinx-build "docsource" .`

For more information, watch the following [Youtube video](https://www.youtube.com/watch?v=b4iFyrLQQh4)

