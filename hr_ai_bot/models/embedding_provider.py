from odoo import models
import requests
import time
import logging

_logger = logging.getLogger(__name__)


class OpenAIProvider:
    """OpenAI embedding provider"""
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_embedding(self, text, max_retries=5):
        for attempt in range(max_retries):
            try:
                resp = requests.post(
                    'https://api.openai.com/v1/embeddings',
                    headers={
                        'Authorization': f"Bearer {self.api_key}",
                        'Content-Type': 'application/json',
                    },
                    json={
                        'model': 'text-embedding-3-small',
                        'input': text,
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                return resp.json()['data'][0]['embedding']
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    # Rate limited - wait and retry with exponential backoff
                    wait_time = 2 ** attempt  # 1, 2, 4, 8, 16 seconds
                    _logger.warning(f"OpenAI rate limit hit, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise
        raise Exception("Max retries exceeded for OpenAI embedding request")


class OllamaProvider:
    """Local Ollama embedding provider (free, no API key needed)"""
    
    def __init__(self, base_url='http://localhost:11434'):
        self.base_url = base_url
    
    def get_embedding(self, text):
        resp = requests.post(
            f'{self.base_url}/api/embeddings',
            json={
                'model': 'nomic-embed-text',
                'prompt': text,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()['embedding']



class HrAiEmbeddingProvider(models.AbstractModel):
    """Model to manage embedding providers"""
    _name = 'hr.ai.embedding.provider'
    _description = 'HR AI Embedding Provider'
    
    def get_embedding(self, text):
        """Get embedding using configured provider"""
        config = self.env['hr.ai.config'].get_config()
        
        if config.provider == 'openai':
            if not config.openai_api_key:
                raise Exception('OpenAI API key not configured')
            provider = OpenAIProvider(config.openai_api_key)
        elif config.provider == 'ollama':
            base_url = config.ollama_base_url or 'http://localhost:11434'
            provider = OllamaProvider(base_url)
        else:
            raise Exception(f'Unknown provider: {config.provider}')
        
        return provider.get_embedding(text)
