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
            ORDER BY embedding <-> %s
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

        settings = self.env['hr.ai.settings'].get_provider_config()
        openai_api_key = settings.openai_api_key_llm
        
        if not openai_api_key:
            raise Exception('OpenAI API key for chat not configured in HR AI Settings')

        resp = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f"Bearer {openai_api_key}",
                'Content-Type': 'application/json',
            },
            json={
                'model': 'gpt-4o-mini',
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

        channel.message_post(
            body=answer,
            message_type='comment',
            subtype_xmlid='mail.mt_comment'
        )
