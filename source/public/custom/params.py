﻿from contextlib import suppress
from typing import Match, Optional, Sequence
from ...data import CustomFieldArgs
import re


def fieldParams(args: CustomFieldArgs) -> Optional[str]:
    with suppress(TypeError):
        match = re.fullmatch(r'(\d+)(-(\d+))?|(\d+)-|-(\d+)', args.field)  # type: Match[str]
        if match is not None:
            matchParts = match.groups()  # type: Sequence[str]
            start = None  # type: Optional[int]
            stop = None  # type: Optional[int]
            if matchParts[0] is not None:
                start = int(matchParts[0])
                if matchParts[2] is not None:
                    stop = int(matchParts[2])
                else:
                    if start < len(args.message):
                        return args.prefix + args.message[start] + args.suffix
                    else:
                        return args.default
            elif matchParts[3] is not None:
                start = int(matchParts[3])
            elif matchParts[4] is not None:
                stop = int(matchParts[4])
            params = args.message[start:stop]
            if params:
                return args.prefix + params + args.suffix
            else:
                return args.default
    return None
