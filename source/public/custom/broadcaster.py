﻿def fieldBroadcaster(field, param, prefix, suffix, default, message,
                     tokens, channel, nick, query, now):
    if field.lower() == 'broadcaster' or field.lower() == 'streamer':
        return prefix + channel + suffix if channel else default
    return None
