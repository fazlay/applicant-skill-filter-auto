from odoo import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_recalculate_custom_lines(self):
        """Recalculate all custom calculation lines in this invoice."""
        self.ensure_one()
        if self.invoice_line_ids:
            self.invoice_line_ids._compute_totals()
        return True