import asyncio
from telethon import TelegramClient
from django.conf import settings
from asgiref.sync import async_to_sync

client = TelegramClient(
    settings.TELEGRAM_SESSION,
    settings.TELEGRAM_API_ID,
    settings.TELEGRAM_API_HASH
)

_start_lock = asyncio.Lock()

async def start_client():
    """Connects and starts the client if not already started."""
    if not client.is_connected():
        async with _start_lock:
            # Double check after acquiring the lock
            if not client.is_connected():
                await client.start(phone=settings.TELEGRAM_PHONE)

def start_client_sync():
    """
    Synchronous version of start_client. Safe to call multiple times.
    """
    async_to_sync(start_client)()
