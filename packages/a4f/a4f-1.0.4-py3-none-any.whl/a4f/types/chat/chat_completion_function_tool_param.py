from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ChatCompletionFunctionToolParam"]


class ChatCompletionFunctionToolParam(TypedDict, total=False):

    type: Required[Literal["function"]]
    """The type of the tool. Currently, only `function` is supported."""
