import os
import asyncio
import functools

from pyrogram import Client , filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message , CallbackQuery , ChatPrivileges

from typing import Union
from functools import wraps

from d4rk.Logs import setup_logger


logger = setup_logger(__name__)

command_registry = []
last_index_per_chat = {}
bot_order_per_chat = {}
responded_messages = {}
chat_locks = {}

def get_priority(description: str) -> int:
    desc_lower = description.lower()
    if "(owner only)" in desc_lower:return 4
    elif "(sudo only)" in desc_lower:return 3
    elif "(admin only)" in desc_lower:return 2
    else:return 1
    
def reorder_command_registry():
    global command_registry
    command_registry.sort(key=lambda cmd: get_priority(cmd["description"]))

def get_commands():
    global command_registry
    return command_registry

def new_task():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            asyncio.create_task(func(*args, **kwargs))
        return wrapper
    return decorator

def retry():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def runner():
                try:await func(*args, **kwargs)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await func(*args, **kwargs)
            asyncio.create_task(runner())
        return wrapper
    return decorator

def round_robin():
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message, *args, **kwargs):
            chat_id = message.chat.id
            msg_id = message.id
            
            if message.chat.type.name.lower() == "private":
                return await func(client, message, *args, **kwargs)

            if chat_id not in bot_order_per_chat:
                bot_order_per_chat[chat_id] = [client.me.id]
                last_index_per_chat[chat_id] = 0
                responded_messages[chat_id] = set()
                chat_locks[chat_id] = asyncio.Lock()

            if client.me.id not in bot_order_per_chat[chat_id]:
                bot_order_per_chat[chat_id].append(client.me.id)

            async with chat_locks[chat_id]:
                if msg_id in responded_messages[chat_id]:
                    return
                current_index = last_index_per_chat[chat_id]
                selected_bot_id = bot_order_per_chat[chat_id][current_index]

                if client.me.id == selected_bot_id:
                    result = await func(client, message, *args, **kwargs)
                    responded_messages[chat_id].add(msg_id)
                    last_index_per_chat[chat_id] = (current_index + 1) % len(bot_order_per_chat[chat_id])
                    return result
        return wrapper
    return decorator


def command(command: Union[str, list], description: str,Custom_filter=None):
    def decorator(func):
        command_registry.append({
            "command": command,
            "description": description,
            "handler": func
        })
        logger.info(f"Registered command: {command} - {description}")
        if Custom_filter:
            filter = filters.command(command) & Custom_filter
        else:
            filter = filters.command(command)
        @Client.on_message(filter)
        @round_robin()
        @wraps(func)
        async def wrapper(client, message):
            return await func(client, message)
        reorder_command_registry()
        return wrapper
    return decorator

