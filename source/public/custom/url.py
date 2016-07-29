﻿from bot import config
from contextlib import suppress
from http.client import HTTPResponse
from typing import Optional
from ...data import CustomFieldArgs
import urllib.error
import urllib.request


def fieldUrl(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'url':
        url = args.param.replace('{query}', args.message.query)  # type: str
        url = url.replace('{user}', args.nick)
        url = url.replace('{nick}', args.nick)
        url = url.replace('{broadcaster}', args.channel)
        url = url.replace('{streamer}', args.channel)
        with suppress(urllib.error.URLError):
            with urllib.request.urlopen(
                    url, timeout=config.customMessageUrlTimeout) as res:  # --type: HTTPResponse
                if isinstance(res, HTTPResponse) and int(res.status) == 200:
                    data = res.read().decode('utf-8')  # type: str
                    data = data.replace('\r\n', ' ')
                    data = data.replace('\n', ' ')
                    data = data.replace('\r', ' ')
                    return (args.prefix or '') + data + (args.suffix or '')
        return args.default or ''
    return None
