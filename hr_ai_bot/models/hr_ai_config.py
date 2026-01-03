from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class HrAiConfig(models.Model):
    _name = 'hr.ai.config'
    _description = 'HR AI Configuration'
    _rec_name = 'provider'

    provider = fields.Selection(
        [
            ('openai', 'OpenAI'),
            ('ollama', 'Ollama (Local, Free)'),
        ],
        string='AI Provider',
        default='ollama',
        required=True,
    )

    openai_api_key = fields.Char(string='OpenAI API Key')
    ollama_base_url = fields.Char(
        string='Ollama Base URL',
        default='http://localhost:11434',
        help='Default: http://localhost:11434'
    )

    def get_config(self):
        """Get or create singleton config"""
        # Order by write_date desc to get the most recently modified config
        config = self.search([], limit=1, order='write_date desc')
        if not config:
            config = self.create({'provider': 'ollama'})
        # Reset invalid providers - prefer openai if key exists
        elif config.provider not in ('openai', 'ollama'):
            if config.openai_api_key:
                config.provider = 'openai'
            else:
                config.provider = 'ollama'
        
        _logger.info("HR AI Config - Provider: %s, Has OpenAI Key: %s", 
                     config.provider, bool(config.openai_api_key))
        return config
