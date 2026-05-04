from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


class AccountMove(models.Model):
    _inherit = "account.move"

    use_custom_total = fields.Boolean(
        string="Use Custom Total Calculation",
        help="Enable to write custom Python logic for invoice total"
    )

    custom_total_code = fields.Text(
        string="Custom Total Formula",
        help="""
Available variables:
- move: current invoice record
- lines: all invoice lines (recordset)
- result: SET THIS to the calculated total amount (float)

Example:
# Sum all line subtotals
result = sum(l.price_subtotal for l in lines)
"""
    )

    custom_total = fields.Monetary(
        string="Custom Total",
        compute='_compute_custom_total',
        store=True,
        readonly=False,
    )

    @api.depends('invoice_line_ids.price_subtotal', 'use_custom_total', 'custom_total_code')
    def _compute_custom_total(self):
        for move in self:
            if not move.use_custom_total or not move.custom_total_code:
                move.custom_total = move.amount_untaxed
                continue

            localdict = {
                'move': move,
                'lines': move.invoice_line_ids,
                'result': 0.0,
            }

            try:
                safe_eval(move.custom_total_code, localdict, mode='exec', nocopy=True)
                move.custom_total = localdict.get('result', move.amount_untaxed)
            except Exception as e:
                move.custom_total = move.amount_untaxed

    def action_recalculate_custom_lines(self):
        """Recalculate all custom calculation lines in this invoice."""
        self.ensure_one()
        if self.invoice_line_ids:
            self.invoice_line_ids._compute_totals()
        self._compute_custom_total()
        return True