from odoo import models
import requests

class HrAiBot(models.AbstractModel):
    _name = 'hr.ai.bot'
    _description = 'HR AI Bot'

    def _get_embedding(self, text):
        """Get embedding using configured provider"""
        return self.env['hr.ai.embedding.provider'].get_embedding(text)

    def _search_context(self, question):
        q_embedding = self._get_embedding(question)

        self.env.cr.execute(
            """
            SELECT content
            FROM hr_ai_embedding
            ORDER BY embedding <-> %s::vector
            LIMIT 3
            """,
            (q_embedding,)
        )

        rows = self.env.cr.fetchall()
        return '\n'.join(r[0] for r in rows)

    def _ask_llm(self, context, question):
        prompt = f"""
You are an HR assistant.
Answer using only the context below.
If the answer is not in the context, say you don't know.

Context:
{context}

Question:
{question}
"""

        config = self.env['hr.ai.config'].get_config()
        
        if config.provider == 'openai':
            if not config.openai_api_key:
                raise Exception('OpenAI API key not configured')
            api_key = config.openai_api_key
            url = 'https://api.openai.com/v1/chat/completions'
            model = 'gpt-4o-mini'
            headers = {
                'Authorization': f"Bearer {api_key}",
                'Content-Type': 'application/json',
            }
        elif config.provider == 'deepseek':
            if not config.deepseek_api_key:
                raise Exception('DeepSeek API key not configured')
            api_key = config.deepseek_api_key
            url = 'https://api.deepseek.com/v1/chat/completions'
            model = 'deepseek-chat'
            headers = {
                'Authorization': f"Bearer {api_key}",
                'Content-Type': 'application/json',
            }
        elif config.provider == 'ollama':
            base_url = config.ollama_base_url or 'http://localhost:11434'
            url = f'{base_url}/api/chat'
            model = 'llama3.2'
            headers = {'Content-Type': 'application/json'}
        else:
            raise Exception(f'Unknown provider: {config.provider}')

        if config.provider == 'ollama':
            # Ollama uses different API format
            resp = requests.post(
                url,
                headers=headers,
                json={
                    'model': model,
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                    'stream': False,
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()['message']['content']
        else:
            # OpenAI/DeepSeek format
            resp = requests.post(
                url,
                headers=headers,
                json={
                    'model': model,
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()['choices'][0]['message']['content']

    def handle_question(self, message, channel):
        question = (message.body or '').strip()
        if not question:
            return

        context = self._search_context(question)
        answer = self._ask_llm(context, question)

        # Post with context flag to prevent infinite loop
        channel.with_context(hr_ai_bot_replying=True).message_post(
            body=answer,
            message_type='comment',
            subtype_xmlid='mail.mt_comment'
        )
