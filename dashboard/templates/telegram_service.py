from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.types import InputPeerChannel
from telethon import TelegramClient
from django.conf import settings
from telethon.errors import SessionPasswordNeededError, FloodWaitError, AuthKeyUnregisteredError, UserDeactivatedError, ChannelPrivateError
from asgiref.sync import async_to_sync
import io
import logging

logger = logging.getLogger(__name__)


# -------------------------------
# CREATE / GET USER CHANNEL
# -------------------------------
async def _get_or_create_channel(channel_name: str):
    async with TelegramClient(settings.TELEGRAM_SESSION, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH) as client:
        await client.start(phone=settings.TELEGRAM_PHONE)
        dialogs = await client.get_dialogs()

        for dialog in dialogs:
            if dialog.name == channel_name:
                return {
                    'id': dialog.entity.id,
                    'access_hash': dialog.entity.access_hash
                }

        result = await client(
            CreateChannelRequest(
                title=channel_name,
                about=f"Saved files for {channel_name}",
                megagroup=False
            )
        )

        channel = result.chats[0]
        return {
            'id': channel.id,
            'access_hash': channel.access_hash
        }


def get_channel_id(email: str) -> dict:
    """
    channel_name = email before '@'
    Returns {'id': int, 'access_hash': int}
    """
    channel_name = email.split('@')[0]
    return async_to_sync(_get_or_create_channel)(channel_name)


# -------------------------------
# UPLOAD FILE
# -------------------------------
async def _upload_file(peer, uploaded_file, file_name: str):
    async with TelegramClient(settings.TELEGRAM_SESSION, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH) as client:
        await client.start(phone=settings.TELEGRAM_PHONE)

        entity = peer
        if isinstance(peer, dict):
            entity = InputPeerChannel(peer['id'], peer['access_hash'])

        file_content = uploaded_file.read()
        file_obj = io.BytesIO(file_content)
        file_obj.name = file_name
        await client.send_file(
            entity=entity,
            file=file_obj,
            force_document=True
        )


def upload_file(peer, uploaded_file, file_name):
    async_to_sync(_upload_file)(peer, uploaded_file, file_name)


# -------------------------------
# LIST FILES FROM CHANNEL
# -------------------------------
async def _list_files(channel_id: int):
    async with TelegramClient(settings.TELEGRAM_SESSION, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH) as client:
        await client.start(phone=settings.TELEGRAM_PHONE)

        peer = channel_id
        if isinstance(channel_id, dict):
            peer = InputPeerChannel(channel_id['id'], channel_id['access_hash'])

        messages = []
        async for msg in client.iter_messages(peer):
            if msg.file:
                messages.append({
                    "id": msg.id,
                    "name": msg.file.name,
                    "size": msg.file.size,
                    "date": msg.date,
                    "mime_type": msg.file.mime_type,
                })
        return messages


def list_files(channel_id: int):
    files = async_to_sync(_list_files)(channel_id)
    
    TEXT_EXTENSIONS = (
        '.txt', '.md', '.py', '.json', '.xml',
        '.html', '.css', '.js', '.log',
        '.csv', '.yaml', '.yml'
    )
    
    # Document formats that can be previewed
    DOCUMENT_EXTENSIONS = (
        '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'
    )
    
    for file in files:
        file_name = (file.get('name') or '').lower()
        is_image = file.get('mime_type', '').startswith('image/')
        is_text = file_name.endswith(TEXT_EXTENSIONS) or file.get('mime_type', '').startswith('text/')
        is_document = file_name.endswith(DOCUMENT_EXTENSIONS)
        
        file['is_previewable'] = is_image or is_text or is_document
        file['is_text'] = is_text
        file['is_document'] = is_document
    
    return files


# -------------------------------
# DOWNLOAD FILE
# -------------------------------
async def _download_file(channel_id: int, message_id: int, path: str):
    async with TelegramClient(
        settings.TELEGRAM_SESSION,
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH
    ) as client:
        await client.start(phone=settings.TELEGRAM_PHONE)
        await client.download_media(
            message=message_id,
            file=path
        )

def download_file(channel_id: int, message_id: int, path: str):
    async_to_sync(_download_file)(channel_id, message_id, path)



# -------------------------------
# GET FILE PREVIEW
# -------------------------------
async def _get_file_preview(channel_id: int, message_id: int):
    async with TelegramClient(
        settings.TELEGRAM_SESSION,
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH
    ) as client:
        await client.start(phone=settings.TELEGRAM_PHONE)

        peer = channel_id
        if isinstance(channel_id, dict):
            peer = InputPeerChannel(channel_id['id'], channel_id['access_hash'])

        message = await client.get_messages(peer, ids=message_id)

        if not message or not message.file:
            return None

        file_name = (message.file.name or "").lower()

        TEXT_EXTENSIONS = (
            '.txt', '.md', '.py', '.json', '.xml',
            '.html', '.css', '.js', '.log',
            '.csv', '.yaml', '.yml'
        )

        # ---------------- IMAGE PREVIEW ----------------
        if message.file.mime_type and message.file.mime_type.startswith('image/'):
            file_data = await client.download_media(message, bytes)
            return {
                'type': 'image',
                'data': file_data,
                'mime_type': message.file.mime_type,
                'name': message.file.name
            }

        # ---------------- TEXT PREVIEW ----------------
        elif file_name.endswith(TEXT_EXTENSIONS):
            file_data = await client.download_media(message, bytes)
            try:
                content = file_data.decode('utf-8')
                return {
                    'type': 'text',
                    'content': content,
                    'name': message.file.name,
                    'mime_type': message.file.mime_type
                }
            except UnicodeDecodeError:
                return {
                    'type': 'file',
                    'name': message.file.name,
                    'size': message.file.size,
                    'mime_type': message.file.mime_type
                }

        # ---------------- DOCX PREVIEW ----------------
        elif file_name.endswith('.docx'):
            file_data = await client.download_media(message, bytes)
            try:
                from docx import Document
                doc = Document(io.BytesIO(file_data))
                content = '\n\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
                return {
                    'type': 'text',
                    'content': content,
                    'name': message.file.name,
                    'mime_type': message.file.mime_type
                }
            except Exception as e:
                return {
                    'type': 'file',
                    'name': message.file.name,
                    'size': message.file.size,
                    'mime_type': message.file.mime_type,
                    'error': f'Could not extract text: {str(e)}'
                }

        # ---------------- PDF PREVIEW ----------------
        elif file_name.endswith('.pdf'):
            file_data = await client.download_media(message, bytes)
            try:
                from PyPDF2 import PdfReader
                pdf = PdfReader(io.BytesIO(file_data))
                content = '\n\n'.join([page.extract_text() for page in pdf.pages if page.extract_text()])
                return {
                    'type': 'text',
                    'content': content,
                    'name': message.file.name,
                    'mime_type': message.file.mime_type
                }
            except Exception as e:
                return {
                    'type': 'file',
                    'name': message.file.name,
                    'size': message.file.size,
                    'mime_type': message.file.mime_type,
                    'error': f'Could not extract text: {str(e)}'
                }

        # ---------------- OTHER FILES ----------------
        return {
            'type': 'file',
            'name': message.file.name,
            'size': message.file.size,
            'mime_type': message.file.mime_type
        }


def get_file_preview(channel_id: int, message_id: int):
    return async_to_sync(_get_file_preview)(channel_id, message_id)


# -------------------------------
# GET FILE DATA
# -------------------------------
async def _get_file_data(channel_id: int, message_id: int):
    async with TelegramClient(
        settings.TELEGRAM_SESSION,
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH
    ) as client:
        await client.start(phone=settings.TELEGRAM_PHONE)

        peer = channel_id
        if isinstance(channel_id, dict):
            peer = InputPeerChannel(channel_id['id'], channel_id['access_hash'])

        message = await client.get_messages(peer, ids=message_id)

        if not message or not message.file:
            return None

        file_data = await client.download_media(message, bytes)
        return {
            'name': message.file.name or "download",
            'mime_type': message.file.mime_type or 'application/octet-stream',
            'data': file_data
        }


def get_file_data(channel_id: int, message_id: int):
    return async_to_sync(_get_file_data)(channel_id, message_id)
