import logging
import asyncio
import re
import sys

from aiohttp import ClientSession
from pyrogram import Client
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import *
from pyromod import listen
from rich.logging import RichHandler
from pytgcalls import GroupCallFactory

from ubot.config import *

# Remove global ClientSession initialization
# aiosession = ClientSession()

def gas():
    execvp(executable, [executable, "-m", "ubot"])

class ConnectionHandler(logging.Handler):
    def emit(self, record):
        for X in ["OSError", "socket"]:
            if X in record.getMessage():
                sys.exit()

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

formatter = logging.Formatter("[%(levelname)s] - %(name)s - %(message)s", "%d-%b %H:%M")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
connection_handler = ConnectionHandler()

logger.addHandler(stream_handler)
logger.addHandler(connection_handler)

LOGS = logging.getLogger(__name__)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

class Ubot(Client):
    __module__ = "pyrogram.client"
    _ubot = []
    _prefix = {}
    _get_my_id = []
    _translate = {}
    _get_my_peer = {}

    def __init__(self, api_id, api_hash, device_model="🖕🏻ReloadYourBot 🖕🏻", **kwargs):
        super().__init__(**kwargs)
        self.api_id = api_id
        self.api_hash = api_hash
        self.device_model = device_model
        self.aiosession = None  # Initialize later

    async def setup(self):
        self.aiosession = ClientSession()
        self.group_call = GroupCallFactory(self).get_file_group_call("input.raw")

    def on_message(self, filters=None, group=-1):
        def decorator(func):
            for ub in self._ubot:
                ub.add_handler(MessageHandler(func, filters), group)
            return func
        return decorator

    def set_prefix(self, user_id, prefix):
        self._prefix[self.me.id] = prefix

    async def start(self):
        while True:
            try:
                await super().start()
                await self.setup()  # Ensure ClientSession is initialized
                handler = await get_pref(self.me.id)
                if handler:
                    self._prefix[self.me.id] = handler
                else:
                    self._prefix[self.me.id] = [".", ",", ":", ";", "!"]
                self._ubot.append(self)
                self._get_my_id.append(self.me.id)
                self._translate[self.me.id] = "id"
                print(f"[𝐈𝐍𝐅𝐎] - ({self.me.id}) - 𝐒𝐓𝐀𝐑𝐓𝐄𝐃")
                break  # Exit loop if successful
            except OSError as e:
                print(f"Connection lost: {e}")
                await asyncio.sleep(10)  # Wait before retrying

    async def stop(self):
        if self.aiosession:
            await self.aiosession.close()
        await super().stop()

async def get_prefix(user_id):
    return ubot._prefix.get(user_id, ".")

def anjay(cmd):
    command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")

    async def func(_, client, message):
        if message.text and message.from_user:
            text = message.text.strip()
            username = client.me.username or ""
            prefixes = await get_prefix(client.me.id)

            if not text:
                return False

            for prefix in prefixes:
                if not text.startswith(prefix):
                    continue

                without_prefix = text[len(prefix):]

                for command in cmd.split("|"):
                    if not re.match(
                        rf"^(?:{command}(?:@?{username})?)(?:\s|$)",
                        without_prefix,
                        flags=re.IGNORECASE if not False else 0,
                    ):
                        continue

                    without_command = re.sub(
                        rf"{command}(?:@?{username})?\s?",
                        "",
                        without_prefix,
                        count=1,
                        flags=re.IGNORECASE if not False else 0,
                    )
                    message.command = [command] + [
                        re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "")
                        for m in command_re.finditer(without_command)
                    ]

                    return True

        return False

    return filters.create(func)

ubot = Ubot(
    name="ubot",
    api_id=API_ID,
    api_hash=API_HASH,
    device_model="🖕🏻ReloadYourBot🖕🏻")

class Bot(Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, device_model="ultra-bot")

    def on_message(self, filters=None, group=-1):
        def decorator(func):
            self.add_handler(MessageHandler(func, filters), group)
            return func
        return decorator

    def on_callback_query(self, filters=None, group=-1):
        def decorator(func):
            self.add_handler(CallbackQueryHandler(func, filters), group)
            return func
        return decorator

    async def start(self):
        await super().start()

bot = Bot(
    name="bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=30,
)

from ubot.core.database import *
from ubot.core.function import *
from ubot.core.helpers import *
from ubot.core.plugins import *
