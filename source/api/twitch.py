﻿from . import oauth
from bot import globals
from contextlib import suppress
import configparser
import datetime
import http.client
import json
import os.path
import urllib.parse

def getTwitchClientId():
    if os.path.isfile('config.ini'):
        ini = configparser.ConfigParser()
        ini.read('config.ini')
        if 'twitch' in ini and 'twitchClientID' in ini['twitch']:
            return ini['twitch']['twitchClientID']
    return None

def twitchCall(channel, method, uri, headers={}, data=None):
    conn = http.client.HTTPSConnection('api.twitch.tv')
    
    if channel is not None and 'Authorization' not in headers:
        token = oauth.getOAuthToken(channel)
        if token is not None:
            headers['Authorization'] = 'OAuth ' + token
        headers['Accept'] = 'application/vnd.twitchtv.v3+json'
        clientId = getTwitchClientId()
        if clientId is not None:
            headers['Client-ID'] = clientId
    
    if data is not None:
        if type(data) is dict:
            data = urllib.parse.urlencode(data)
    
    conn.request(method, uri, data, headers)
    response = conn.getresponse()
    responseData = response.read()
    
    conn.close()
    
    return (response, responseData)

def updateTwitchEmotes():
    globals.globalEmotesCache = datetime.datetime.utcnow()
    emotesets = [str(i) for i in globals.emoteset]
    with suppress(OSError):
        response, data = twitchCall(
            None, 'GET',
            '/kraken/chat/emoticon_images?emotesets=' + ','.join(emotesets),
            headers = {
                'Accept': 'application/vnd.twitchtv.v3+json',
                })
        globalEmotes = json.loads(data.decode('utf-8'))['emoticon_sets']
        emotes = {}
        emoteSet = {}
        replaceGlobal = {
            1: ':)',
            2: ':(',
            3: ':D',
            4: '>(',
            5: ':z',
            6: 'o_O',
            7: 'B)',
            8: ':o',
            9: '<3',
            10: ':\\',
            11: ';)',
            12: ':P',
            13: ';P',
            14: 'R)',
            }
        for emoteSetId in globalEmotes:
            for emote in globalEmotes[emoteSetId]:
                if emote['id'] in replaceGlobal:
                    emotes[emote['id']] = replaceGlobal[emote['id']]
                else:
                    emotes[emote['id']] = emote['code']
                emoteSet[emote['id']] = int(emoteSetId)
        globals.globalEmotes = emotes
        globals.globalEmoteSets = emoteSet

def twitchChatServer(chat, headers={}, data=None):
    conn = http.client.HTTPSConnection('tmi.twitch.tv')
    
    if chat is not None and 'Authorization' not in headers:
        token = oauth.getOAuthToken(chat)
        if token is not None:
            headers['Authorization'] = 'OAuth ' + token
        headers['Accept'] = 'application/vnd.twitchtv.v3+json'
        clientId = getTwitchClientId()
        if clientId is not None:
            headers['Client-ID'] = clientId
    
    if data is not None:
        if type(data) is dict:
            data = urllib.parse.urlencode(data)
    
    uri = '/servers?channel=' + chat
    conn.request('GET', uri, data, headers)
    response = conn.getresponse()
    responseData = response.read()
    try:
        jData = json.loads(responseData.decode('utf-8'))
        return str(jData['cluster'])
    except:
        return None
    finally:
        conn.close()

def checkValidTwitchUser(user):
    user = user.lower()
    currentTime = datetime.datetime.utcnow()
    if 'validTwitchUser' not in globals.globalSessionData:
        globals.globalSessionData['validTwitchUser'] = {}
    validCache = globals.globalSessionData['validTwitchUser']
    if (user not in validCache or
        currentTime - validCache[user][1] > datetime.timedelta(minutes=1)):
        response, data = twitchCall(
            None, 'GET', '/kraken/channels/' + user,
            headers = {
                'Accept': 'application/vnd.twitchtv.v3+json',
                })
        validCache[user] = response.code == 200, currentTime
    return validCache[user][0]

def getFollowerCount(user):
    try:
        uri = '/kraken/users/' + user + '/follows/channels?limit=1'
        response, data = twitchCall(None, 'GET', uri)
        followerData = json.loads(data.decode('utf-8'))
        return int(followerData['_total'])
    except Exception:
        return None
