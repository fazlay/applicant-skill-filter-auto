from odoo import models, fields, api
import base64
from io import BytesIO
import time
import logging

_logger = logging.getLogger(__name__)

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

class HrAiDocument(models.Model):
    _name = 'hr.ai.document'
    _description = 'HR AI Knowledge Document'

    name = fields.Char(required=True)
    file = fields.Binary(required=True)

    def action_process_pdf(self):
        self.ensure_one()
        if not PdfReader:
            return

        pdf_bytes = base64.b64decode(self.file)
        reader = PdfReader(BytesIO(pdf_bytes))

        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''

        chunks = self._chunk_text(text)
        total_chunks = len(chunks)
        
        config = self.env['hr.ai.config'].get_config()
        # Add delay between API calls for OpenAI to avoid rate limits
        delay = 0.5 if config.provider == 'openai' else 0

        for i, chunk in enumerate(chunks):
            _logger.info(f"Processing chunk {i + 1}/{total_chunks}")
            embedding = self.env['hr.ai.bot']._get_embedding(chunk)
            self.env['hr.ai.embedding']._insert_embedding(chunk, embedding)
            
            # Small delay to avoid rate limiting
            if delay and i < total_chunks - 1:
                time.sleep(delay)

    def _chunk_text(self, text, size=500):
        words = text.split()
        return [' '.join(words[i:i+size]) for i in range(0, len(words), size)]
