from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class HrAiConfig(models.Model):
    _name = 'hr.ai.config'
    _description = 'HR AI Configuration'
    _rec_name = 'display_name'

    display_name = fields.Char(compute='_compute_display_name', store=False)

    # --- LLM Provider ---
    llm_provider = fields.Selection([
        ('openai', 'OpenAI'),
        ('deepseek', 'DeepSeek'),
        ('ollama', 'Ollama (Local)'),
    ], string='LLM Provider', default='ollama', required=True)

    llm_model = fields.Char(
        string='LLM Model',
        default='gpt-4o-mini',
        help='e.g. gpt-4o-mini, deepseek-chat, llama3.2',
    )

    llm_api_key = fields.Char(string='LLM API Key', password=True)

    llm_temperature = fields.Float(
        string='Temperature', default=0.7,
        help='Higher = more creative, lower = more deterministic (0.0-2.0)',
    )

    llm_max_tokens = fields.Integer(
        string='Max Tokens', default=2048,
        help='Maximum tokens in the LLM response',
    )

    # --- Embedding Provider ---
    embedding_provider = fields.Selection([
        ('openai', 'OpenAI'),
        ('ollama', 'Ollama (Local)'),
    ], string='Embedding Provider', default='ollama', required=True)

    embedding_model = fields.Char(
        string='Embedding Model',
        default='nomic-embed-text',
        help='e.g. text-embedding-3-small, nomic-embed-text',
    )

    embedding_api_key = fields.Char(
        string='Embedding API Key', password=True,
        help='Only needed for OpenAI embeddings',
    )

    embedding_dimension = fields.Integer(
        string='Embedding Dimension', default=768,
        help='Vector dimension (768 for nomic-embed-text, 1536 for text-embedding-3-small). '
             'Must match the pgvector column. Re-process documents after changing.',
    )

    # --- Shared ---
    ollama_base_url = fields.Char(
        string='Ollama Base URL',
        default='http://localhost:11434',
        help='Default: http://localhost:11434',
    )

    request_timeout = fields.Integer(
        string='Request Timeout (s)', default=30,
    )

    # --- RAG Parameters ---
    chunk_size = fields.Integer(string='Chunk Size (words)', default=500)
    chunk_overlap = fields.Integer(string='Chunk Overlap (words)', default=50)
    top_k = fields.Integer(string='Top-K Results', default=3)
    system_prompt = fields.Text(
        string='System Prompt',
        default=(
            "You are an HR assistant.\n"
            "Answer using only the context below.\n"
            "If the answer is not in the context, say you don't know."
        ),
    )

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"HR AI Config ({rec.llm_provider} / {rec.embedding_provider})"

    def get_config(self):
        config = self.search([], limit=1, order='write_date desc')
        if not config:
            config = self.create({
                'llm_provider': 'ollama',
                'embedding_provider': 'ollama',
            })
        _logger.info(
            "HR AI Config - LLM: %s/%s, Embedding: %s/%s",
            config.llm_provider, config.llm_model,
            config.embedding_provider, config.embedding_model,
        )
        return config
