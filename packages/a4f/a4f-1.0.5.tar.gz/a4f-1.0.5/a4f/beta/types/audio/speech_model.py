from typing_extensions import Literal, TypeAlias

__all__ = ["SpeechModel"]

SpeechModel: TypeAlias = Literal["tts-1", "tts-1-hd", "gpt-4o-mini-tts"]
