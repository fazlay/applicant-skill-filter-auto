from odoo import models, fields


class HrAiSettings(models.Model):
    _name = 'hr.ai.settings'
    _description = 'HR AI Settings'
    _rec_name = 'embedding_provider'

    embedding_provider = fields.Selection(
        [
            ('ollama', 'Ollama (Free, Local)'),
            ('openai', 'OpenAI'),
            ('deepseek', 'DeepSeek'),
        ],
        string='Embedding Provider',
        default='ollama',
        required=True,
    )

    openai_api_key = fields.Char(
        string='OpenAI API Key (Embeddings)',
    )

    openai_api_key_llm = fields.Char(
        string='OpenAI API Key (Chat)',
    )

    deepseek_api_key = fields.Char(
        string='DeepSeek API Key',
    )

    ollama_base_url = fields.Char(
        string='Ollama Base URL',
        default='http://localhost:11434',
    )

    ollama_model = fields.Char(
        string='Ollama Embedding Model',
        default='nomic-embed-text',
    )

    def get_provider_config(self):
        """Get the singleton settings record"""
        return self.search([], limit=1) or self.create({})
