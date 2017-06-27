﻿from .public import whisper as publicList
from collections import ChainMap
from source import data
from typing import Mapping, Optional
try:
    from .private import whisper as privateList
except ImportError:
    from .private.default import whisper as privateList  # type: ignore

WhisperDict = Mapping[str, Optional[data.WhisperCommand]]


def commands() -> WhisperDict:
    return ChainMap(privateList.commands(), publicList.commands())


def commandsStartWith() -> WhisperDict:
    return ChainMap(privateList.commandsStartWith(),
                    publicList.commandsStartWith())
