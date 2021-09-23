In order to generate/update the HTML documentation page, it's required to install the following:

`pip install -U sphinx`

`pip install sphinx_rtf_theme`

Before running any further commands, ensure that the "Documents/docsource" folder only contains the files "conf.py" and "index.rst".

Also, ensure that the "Documents" folder only contains the README.md file and the folders "_templates", "docsource" and "images".
Everything else should be deleted. If you see a large number of .html files, these should be deleted as they will be generated again during the commands below.

Then, open a terminal and type the following commands within the Weasel parent folder:

`cd Documents`

#`sphinx-apidoc -M -f -e -t .\_templates -o "docsource" ..`

`sphinx-apidoc -M -f -e -t ".\_templates" -o "docsource" "..\CoreModules"`

`sphinx-apidoc -M -f -e -t ".\_templates" -o "docsource" "..\Scripting"`


# Potentially include (or not) these in the future?

#`sphinx-apidoc -M -f -e -t ".\_templates" -o "docsource" "..\Pipelines"`

#`sphinx-apidoc -M -f -e -t ".\_templates" -o "docsource" "..\External"`

#`sphinx-apidoc -M -f -e -t ".\_templates" -o "docsource" "..\Configurations"`

`sphinx-build "docsource" .`

For more information, watch the following [Youtube video](https://www.youtube.com/watch?v=b4iFyrLQQh4)

