﻿import textwrap
from datetime import timedelta
from typing import Awaitable, Callable, Dict, List, Optional  # noqa: F401

import bot
import lib.items.custom
from bot import utils
from lib.data import ChatCommandArgs, CustomCommand, CommandActionTokens  # noqa: F401,E501
from lib.helper import chat, timeout
from lib.helper.chat import min_args, not_feature, permission, ownerChannel
from . import library


@not_feature('nocustom')
async def customCommands(args: ChatCommandArgs) -> bool:
    command: Optional[CustomCommand]
    command = await library.get_command(args.data, args.message.command,
                                        args.chat.channel, args.permissions)
    if command is not None:
        cooldown: timedelta
        cooldown = timedelta(seconds=bot.config.customMessageCooldown)
        if chat.inCooldown(args, cooldown, 'customCommand', 'moderator'):
            return False

        cooldown = timedelta(seconds=bot.config.customMessageUserCooldown)
        if chat.in_user_cooldown(args, cooldown, 'customUserCommand',
                                 'moderator'):
            return False

        msgs: List[str] = await library.create_messages(command, args)
        args.chat.send(msgs)
        if args.permissions.chatModerator:
            await timeout.record_timeout(args.chat, args.nick, msgs,
                                         str(args.message), 'custom')
        return True
    return False


@ownerChannel
@permission('admin')
async def commandGlobal(args: ChatCommandArgs) -> bool:
    return await process_command(args, '#global')


@not_feature('nocustom')
@permission('moderator')
async def commandCommand(args: ChatCommandArgs) -> bool:
    return await process_command(args, args.chat.channel)


@min_args(3)
async def process_command(args: ChatCommandArgs,
                          broadcaster: str) -> bool:
    input: Optional[CommandActionTokens] = library.parse_action_message(
        args.message, broadcaster)
    if input is None:
        return False

    if input.level is None:
        args.chat.send(f'{args.nick} -> Invalid level, command ignored')
        return True
    if input.level:
        try:
            if not args.permissions[input.level]:
                args.chat.send(f'''\
{args.nick} -> You do not have permission to set that level''')
                return True
        except KeyError:
            args.chat.send(f'{args.nick} -> Invalid level, command ignored')
            return True

    actions: Dict[str, Callable[[ChatCommandArgs, CommandActionTokens],
                                Awaitable[bool]]]
    actions = {
        'add': insert_command,
        'insert': insert_command,
        'new': insert_command,
        'edit': update_command,
        'update': update_command,
        'replace': replace_command,
        'override': replace_command,
        'append': append_command,
        'del': delete_command,
        'delete': delete_command,
        'rem': delete_command,
        'remove': delete_command,
        'property': command_property,
        'raw': raw_command,
        'original': raw_command,
        'level': level_command,
        'rename': rename_command,
        }
    if input.action in actions:
        return await actions[input.action](args, input)
    else:
        return False


async def insert_command(args: ChatCommandArgs,
                         input: CommandActionTokens) -> bool:
    message: str
    successful: bool = await args.data.insertCustomCommand(
        input.broadcaster, input.level, input.command, input.text, args.nick)
    if successful:
        message = f'{args.nick} -> {input.command} was added successfully'
    else:
        message = f'''\
{args.nick} -> {input.command} was not added successfully. There might be an \
existing command'''
    args.chat.send(message)
    return True


async def update_command(args: ChatCommandArgs,
                         input: CommandActionTokens) -> bool:
    message: str
    successful: bool = await args.data.updateCustomCommand(
        input.broadcaster, input.level, input.command, input.text, args.nick)
    if successful:
        message = f'{args.nick} -> {input.command} was updated successfully'
    else:
        message = f'''\
{args.nick} -> {input.command} was not updated successfully. The command \
might not exist'''
    args.chat.send(message)
    return True


async def append_command(args: ChatCommandArgs,
                         input: CommandActionTokens) -> bool:
    message: str
    successful: bool = await args.data.appendCustomCommand(
        input.broadcaster, input.level, input.command, input.text, args.nick)
    if successful:
        message = f'''\
{args.nick} -> {input.command} was appended successfully'''
    else:
        message = f'''\
{args.nick} -> {input.command} was not appended successfully. The command \
might not exist'''
    args.chat.send(message)
    return True


async def replace_command(args: ChatCommandArgs,
                          input: CommandActionTokens) -> bool:
    message: str
    successful: bool = await args.data.replaceCustomCommand(
        input.broadcaster, input.level, input.command, input.text, args.nick)
    if successful:
        message = f'{args.nick} -> {input.command} was replaced successfully'
    else:
        message = f'''\
{args.nick} -> {input.command} was not replaced successfully. The command \
might not exist'''
    args.chat.send(message)
    return True


async def delete_command(args: ChatCommandArgs,
                         input: CommandActionTokens) -> bool:
    message: str
    successful: bool = await args.data.deleteCustomCommand(
        input.broadcaster, input.level, input.command, args.nick)
    if successful:
        message = f'{args.nick} -> {input.command} was removed successfully'
    else:
        message = f'''\
{args.nick} -> {input.command} was not removed successfully. The command \
might not exist'''
    args.chat.send(message)
    return True


@permission('broadcaster')
async def command_property(args: ChatCommandArgs,
                           input: CommandActionTokens) -> bool:
    if not input.text:
        return False
    parts: List[Optional[str]] = input.text.split(None, 1)
    if len(parts) < 2:
        parts.append(None)
    property, value = parts
    if property not in lib.items.custom.properties():
        args.chat.send(f'''\
{args.nick} -> The property '{property}' does not exist''')
        return True
    if await args.data.processCustomCommandProperty(
            input.broadcaster, input.level, input.command, property,
            value):
        if value is None:
            message = f'''\
{args.nick} -> {input.command} with {property} has been unset'''
        else:
            message = f'''\
{args.nick} -> {input.command} with {property} has been set with the value of \
{value}'''
    else:
        message = f'''\
{args.nick} -> {input.command} with {property} could not be processed'''
    args.chat.send(message)
    return True


async def raw_command(args: ChatCommandArgs,
                      input: CommandActionTokens) -> bool:
    command: Optional[str]
    command = await args.data.getCustomCommand(
        input.broadcaster, input.level, input.command)
    message: str
    if command is None:
        args.chat.send(f'{args.nick} -> {input.command} does not exist')
    else:
        utils.whisper(args.nick,
                      textwrap.wrap(command, width=bot.config.messageLimit))
    return True


async def level_command(args: ChatCommandArgs,
                        input: CommandActionTokens) -> bool:
    permission: str = input.text.lower()
    if permission not in library.permissions:
        message = f'{args.nick} -> {input.text} is an invalid permission'
    else:
        successful: bool = await args.data.levelCustomCommand(
            input.broadcaster, input.level, input.command, args.nick,
            library.permissions[permission])
        if successful:
            message = f'''\
{args.nick} -> {input.command} changed permission successfully'''
        else:
            message = f'''\
{args.nick} -> {input.command} was not changed successfully. The command \
might not exist or there is a command with that level existing'''
    args.chat.send(message)
    return True


async def rename_command(args: ChatCommandArgs,
                         input: CommandActionTokens) -> bool:
    newCommand: str = input.text and input.text.split(None, 1)[0]
    message: str
    if not newCommand:
        message = f'{args.nick} -> Please specify a command to rename to'
    else:
        successful: bool = await args.data.renameCustomCommand(
            input.broadcaster, input.level, input.command, args.nick,
            newCommand)
        if successful:
            message = f'''\
{args.nick} -> {input.command} was renamed to successfully to {newCommand}'''
        else:
            message = f'''\
{args.nick} -> {input.command} was not renamed successfully to {newCommand}. \
The command might not exist or there is a command already existing'''
    args.chat.send(message)
    return True
