from typing_extensions import Literal, TypeAlias

__all__ = ["AudioResponseFormat"]

AudioResponseFormat: TypeAlias = Literal["json", "text", "srt", "verbose_json", "vtt"]
