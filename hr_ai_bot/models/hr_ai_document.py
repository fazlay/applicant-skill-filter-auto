from odoo import models, fields
import base64
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    RecursiveCharacterTextSplitter = None


class HrAiDocument(models.Model):
    _name = 'hr.ai.document'
    _description = 'HR AI Knowledge Document'

    name = fields.Char(required=True)
    file = fields.Binary(required=True)

    def action_process_pdf(self):
        self.ensure_one()
        if not PdfReader:
            raise ImportError(
                'The "PyPDF2" Python package is required. '
                'Install it with: pip install PyPDF2'
            )

        pdf_bytes = base64.b64decode(self.file)
        reader = PdfReader(BytesIO(pdf_bytes))

        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''

        if not text.strip():
            _logger.warning("No text extracted from PDF: %s", self.name)
            return

        chunks = self._chunk_text(text)
        total_chunks = len(chunks)
        config = self.env['hr.ai.config'].get_config()

        for i, chunk in enumerate(chunks):
            _logger.info("Processing chunk %d/%d", i + 1, total_chunks)
            embedding = self.env['hr.ai.bot']._get_embedding(chunk)
            self.env['hr.ai.embedding']._insert_embedding(chunk, embedding)

    def _chunk_text(self, text):
        config = self.env['hr.ai.config'].get_config()

        if RecursiveCharacterTextSplitter:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.chunk_size * 4,
                chunk_overlap=config.chunk_overlap * 4,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            return splitter.split_text(text)

        words = text.split()
        chunk_size = config.chunk_size
        overlap = config.chunk_overlap
        step = chunk_size - overlap
        return [
            ' '.join(words[i:i + chunk_size])
            for i in range(0, max(len(words), 1), max(step, 1))
        ]
