from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `scalekit_demo.resources` module.

    This is used so that we can lazily import `scalekit_demo.resources` only when
    needed *and* so that users can just import `scalekit_demo` and reference `scalekit_demo.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("scalekit_demo.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
