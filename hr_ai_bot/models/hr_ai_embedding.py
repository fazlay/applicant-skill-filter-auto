from odoo import models

class HrAiEmbedding(models.Model):
    _name = 'hr.ai.embedding'
    _description = 'HR AI Embedding'
    _auto = False

    def _insert_embedding(self, content, embedding):
        self.env.cr.execute(
            "INSERT INTO hr_ai_embedding (content, embedding) VALUES (%s, %s)",
            (content, embedding)
        )
