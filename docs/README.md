In order to generate/update the HTML documentation page, it's required to install the following:
`pip install -U sphinx`
`pip install sphinx_rtf_theme`

Then, open a terminal and type the following commands within the ukat parent folder:
`cd docs`
#`sphinx-apidoc -M -f -e -t .\_templates -o "docsource" ..`
`sphinx-apidoc -M -f -e -t ".\_templates" -o "docsource" "..\CoreModules" "..\CoreModules\pyqtgraph"`
`sphinx-apidoc -M -f -e -t ".\_templates" -o "docsource" "..\Developer" "..\Developer\External"`
`sphinx-apidoc -M -f -e -t ".\_templates" -o "docsource" "..\MenuItems" "..\MenuItems\Joao-Development"`
`sphinx-build "docsource" "website"`

For more information, watch the following [Youtube video](https://www.youtube.com/watch?v=b4iFyrLQQh4)

