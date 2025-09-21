from ._boyer_moore import search, search_m

try:
    from . import _bm  # type: ignore # noqa: F401
except ModuleNotFoundError:
    raise RuntimeError("Failed to load _bm module.")

__version__ = "2.2.0"
__all__ = ["__version__", "search", "search_m"]
