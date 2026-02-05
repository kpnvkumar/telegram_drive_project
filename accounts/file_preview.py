import io
from .telegram_client import client

async def get_file_content_as_bytes(message):
    return await client.download_media(message, bytes)

def get_docx_preview(file_data, file_name, file_size, mime_type):
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_data))
        content = '\n\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
        return {
            'type': 'text',
            'content': content,
            'name': file_name,
            'mime_type': mime_type,
        }
    except Exception as e:
        print(f"Error getting docx preview for {file_name}: {e}")
        return {
            'type': 'file',
            'name': file_name,
            'size': file_size,
            'mime_type': mime_type,
            'error': f'Could not extract text: {str(e)}'
        }

def get_pdf_preview(file_data, file_name, file_size, mime_type):
    try:
        from PyPDF2 import PdfReader
        pdf = PdfReader(io.BytesIO(file_data))
        content = '\n\n'.join([page.extract_text() for page in pdf.pages if page.extract_text()])
        return {
            'type': 'text',
            'content': content,
            'name': file_name,
            'mime_type': mime_type
        }
    except Exception as e:
        print(f"Error getting pdf preview for {file_name}: {e}")
        return {
            'type': 'file',
            'name': file_name,
            'size': file_size,
            'mime_type': mime_type,
            'error': f'Could not extract text: {str(e)}'
        }

def get_text_preview(file_data, file_name, file_size, mime_type):
    try:
        content = file_data.decode('utf-8')
        return {
            'type': 'text',
            'content': content,
            'name': file_name,
            'mime_type': mime_type
        }
    except UnicodeDecodeError:
        return {
            'type': 'file',
            'name': file_name,
            'size': file_size,
            'mime_type': mime_type,
            'error': 'File is not UTF-8 encoded.'
        }

def get_image_preview(file_data, file_name, mime_type):
    return {
        'type': 'image',
        'data': file_data,
        'mime_type': mime_type,
        'name': file_name
    }
