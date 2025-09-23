from importlib.metadata import version, PackageNotFoundError

from mkdocs_callouts_codeblock.plugin import CalloutsPlugin

try:
    __version__ = version("mkdocs-callouts-codeblock")
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    pass
