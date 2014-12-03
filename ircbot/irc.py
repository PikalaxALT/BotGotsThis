﻿import ircbot.message
import ircbot.socket

# Import some necessary libraries.
messaging = ircbot.message.MessageQueue()
socket = ircbot.socket.SocketThread()
channels = {}

def joinChannel(channel):
    if channel[0] != '#':
        channel = '#' + channel
    channel = channel.lower()
    if channel in channels:
        return False
    channels[channel] = ChannelData(channel, socket)
    socket.join(channels[channel])
    return True

def partChannel(channel):
    if channel[0] != '#':
        channel = '#' + channel
    if channel in channels:
        channels[channel].part()
        del channels[channel]

class ChannelData:
    __slots__ = ['_channel', '_socket', '_twitchStaff', '_twitchAdmin',
                 '_mods', '_users', '_sessionData']
    
    def __init__(self, channel, socket):
        self._channel = channel
        self._socket = socket
        self._twitchStaff = set()
        self._twitchAdmin = set()
        self._mods = set()
        self._users = set()
        self._sessionData = {}
    
    @property
    def channel(self):
        return self._channel
    
    @property
    def socket(self):
        return self._socket
    
    @property
    def twitchStaff(self):
        return frozenset(self._twitchStaff)
    
    @property
    def twitchAdmin(self):
        return frozenset(self._twitchAdmin)
    
    @property
    def mods(self):
        return frozenset(self._mods)
    
    @property
    def users(self):
        return frozenset(self._users)
    
    @property
    def sessionData(self):
        return self._sessionData
    
    def part(self):
        self.socket.part(self)
        messaging.clearQueue(self.channel)
        self._socket = None
    
    def sendMessage(self, msg, priority=1):
        messaging.queueMessage(self, msg, priority)
    
    def sendMulipleMessages(self, messages, priority=1):
        messaging.queueMultipleMessages(self, messages, priority)
    
    def clearMods(self):
        self._mods.clear()
    
    def addMod(self, mod):
        self._mods.add(mod)
    
    def addTwitchAdmin(self, admin):
        self._twitchAdmin.add(admin)
    
    def addTwitchStaff(self, staff):
        self._twitchStaff.add(staff)
