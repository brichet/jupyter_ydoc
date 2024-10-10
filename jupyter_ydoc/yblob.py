# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import base64
from functools import partial
from typing import Any, Callable, Optional, Union

from pycrdt import Awareness, Doc, Map

from .ybasedoc import YBaseDoc


class YBlob(YBaseDoc):
    """
    Extends :class:`YBaseDoc`, and represents a blob document.
    It is currently encoded as base64 because of:
    https://github.com/y-crdt/ypy/issues/108#issuecomment-1377055465
    The Y document can be set from bytes or from str, in which case it is assumed to be encoded as
    base64.

    Schema:

    .. code-block:: json

        {
            "state": YMap,
            "source": YMap
        }
    """

    def __init__(self, ydoc: Optional[Doc] = None, awareness: Optional[Awareness] = None):
        """
        Constructs a YBlob.

        :param ydoc: The :class:`pycrdt.Doc` that will hold the data of the document, if provided.
        :type ydoc: :class:`pycrdt.Doc`, optional.
        :param awareness: The :class:`pycrdt.Awareness` that shares non persistent data
                          between clients.
        :type awareness: :class:`pycrdt.Awareness`, optional.
        """
        super().__init__(ydoc, awareness)
        self._ysource = self._ydoc.get("source", type=Map)
        self.undo_manager.expand_scope(self._ysource)

    @property
    def version(self) -> str:
        """
        Returns the version of the document.

        :return: Document's version.
        :rtype: str
        """
        return "1.0.0"

    def get(self) -> bytes:
        """
        Returns the content of the document.

        :return: Document's content.
        :rtype: bytes
        """
        return base64.b64decode(self._ysource.get("base64", "").encode())

    def set(self, value: Union[bytes, str]) -> None:
        """
        Sets the content of the document.

        :param value: The content of the document.
        :type value: Union[bytes, str]
        """
        if isinstance(value, bytes):
            value = base64.b64encode(value).decode()
        self._ysource["base64"] = value

    def observe(self, callback: Callable[[str, Any], None]) -> None:
        """
        Subscribes to document changes.

        :param callback: Callback that will be called when the document changes.
        :type callback: Callable[[str, Any], None]
        """
        self.unobserve()
        self._subscriptions[self._ystate] = self._ystate.observe(partial(callback, "state"))
        self._subscriptions[self._ysource] = self._ysource.observe(partial(callback, "source"))
