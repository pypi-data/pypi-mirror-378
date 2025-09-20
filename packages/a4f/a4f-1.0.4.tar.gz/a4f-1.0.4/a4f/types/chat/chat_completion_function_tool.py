from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ChatCompletionFunctionTool"]


class ChatCompletionFunctionTool(BaseModel):

    type: Literal["function"]
    """The type of the tool. Currently, only `function` is supported."""
