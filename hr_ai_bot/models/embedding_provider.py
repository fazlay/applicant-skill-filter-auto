from odoo import models
import logging

_logger = logging.getLogger(__name__)

try:
    from litellm import embedding as litellm_embedding
except ImportError:
    litellm_embedding = None


class HrAiEmbeddingProvider(models.AbstractModel):
    _name = 'hr.ai.embedding.provider'
    _description = 'HR AI Embedding Provider'

    def get_embedding(self, text):
        if not litellm_embedding:
            raise ImportError(
                'The "litellm" Python package is required. '
                'Install it with: pip install litellm'
            )

        config = self.env['hr.ai.config'].get_config()
        model_name = f"{config.embedding_provider}/{config.embedding_model}"

        kwargs = {}
        if config.ollama_base_url and config.embedding_provider == 'ollama':
            kwargs['api_base'] = config.ollama_base_url
        if config.embedding_api_key:
            kwargs['api_key'] = config.embedding_api_key

        _logger.info("Getting embedding via LiteLLM: model=%s", model_name)

        response = litellm_embedding(
            model=model_name,
            input=[text],
            timeout=config.request_timeout,
            **kwargs,
        )

        return response.data[0]['embedding']
