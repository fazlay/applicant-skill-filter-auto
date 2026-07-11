from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

try:
    from litellm import completion as litellm_completion
except ImportError:
    litellm_completion = None


class HrAiBot(models.AbstractModel):
    _name = 'hr.ai.bot'
    _description = 'HR AI Bot'

    def _get_embedding(self, text):
        return self.env['hr.ai.embedding.provider'].get_embedding(text)

    def _search_context(self, question):
        config = self.env['hr.ai.config'].get_config()
        q_embedding = self._get_embedding(question)

        self.env.cr.execute(
            """
            SELECT content
            FROM hr_ai_embedding
            ORDER BY embedding <-> %s::vector
            LIMIT %s
            """,
            (q_embedding, config.top_k),
        )

        rows = self.env.cr.fetchall()
        return '\n'.join(r[0] for r in rows)

    def _ask_llm(self, context, question):
        if not litellm_completion:
            raise ImportError(
                'The "litellm" Python package is required. '
                'Install it with: pip install litellm'
            )

        config = self.env['hr.ai.config'].get_config()
        model_name = f"{config.llm_provider}/{config.llm_model}"

        prompt = config.system_prompt or (
            "You are an HR assistant.\n"
            "Answer using only the context below.\n"
            "If the answer is not in the context, say you don't know."
        )

        messages = [
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': f"Context:\n{context}\n\nQuestion:\n{question}"},
        ]

        kwargs = {}
        if config.ollama_base_url and config.llm_provider == 'ollama':
            kwargs['api_base'] = config.ollama_base_url
        if config.llm_api_key:
            kwargs['api_key'] = config.llm_api_key

        _logger.info("LLM call via LiteLLM: model=%s", model_name)

        response = litellm_completion(
            model=model_name,
            messages=messages,
            temperature=config.llm_temperature,
            max_tokens=config.llm_max_tokens,
            timeout=config.request_timeout,
            **kwargs,
        )

        return response.choices[0].message.content

    def _get_bot_partner(self):
        ICP = self.env['ir.config_parameter'].sudo()
        partner_id = ICP.get_param('hr_ai_bot.bot_partner_id')
        if partner_id:
            partner = self.env['res.partner'].browse(int(partner_id))
            if partner.exists():
                return partner

        partner = self.env['res.partner'].search(
            [('name', '=', 'HR AI Assistant Bot')], limit=1
        )
        if not partner:
            partner = self.env['res.partner'].create({
                'name': 'HR AI Assistant Bot',
                'email': 'hr.ai.bot@company.com',
            })

        ICP.set_param('hr_ai_bot.bot_partner_id', str(partner.id))
        return partner

    def handle_question(self, message, channel):
        question = (message.body or '').strip()
        if not question:
            return

        if len(question) > 4096:
            question = question[:4096]

        context = self._search_context(question)
        answer = self._ask_llm(context, question)

        bot_partner = self._get_bot_partner()

        channel.with_context(hr_ai_bot_replying=True).message_post(
            body=answer,
            author_id=bot_partner.id,
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
        )
