from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)

        # Skip if we're in the context of the bot posting a reply
        if self.env.context.get('hr_ai_bot_replying'):
            return messages

        for msg in messages:
            # Check if message is in discuss channel
            if msg.model == 'discuss.channel' and msg.res_id and msg.body:
                channel = self.env['discuss.channel'].browse(msg.res_id)
                if channel.name == 'HR AI Assistant' and msg.message_type == 'comment':
                    _logger.info(f"HR AI Bot: Received question: {msg.body[:100]}")
                    try:
                        self.env['hr.ai.bot'].handle_question(msg, channel)
                    except Exception as e:
                        _logger.error(f"HR AI Bot error: {str(e)}", exc_info=True)
                        # Post error message with bot context flag set
                        channel.with_context(hr_ai_bot_replying=True).message_post(
                            body=f"Sorry, I encountered an error: {str(e)}",
                            message_type='comment',
                        )

        return messages
