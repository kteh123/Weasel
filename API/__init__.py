"""
A collection of Weasel superclasses used for scripting pipelines. 

You can access to all functions in this module inside `Menus` and `Pipelines` via the `weasel` global variable. The way to call the functions in this `API` module is by typing `weasel.__function_name__()` regardless of the API class in which the `__funtion_name__` is in.

These functions are essentially comprehensive but simple to use wrappers of the `CoreModules`, `DICOM` and `Display` packages in Weasel.
"""