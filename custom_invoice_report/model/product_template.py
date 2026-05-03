# models/product_template.py
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    use_custom_calc = fields.Boolean(
        string="Use Custom Calculation",
        help="Enable to write custom Python logic for invoice line total calculation"
    )

    custom_calc_code = fields.Text(
        string="Custom Calculation Code",
        help="""
Available variables in the code:
- line: current account.move.line record
- move: parent account.move record
- product: product.product record (line.product_id)
- siblings: all invoice lines sorted by sequence
- prev_line: previous line in sequence (or None)
- result: SET THIS to the calculated amount (float)

Example:
# 5% local tax on lines above in same section
total = sum(l.price_subtotal for l in siblings if l.sequence < line.sequence)
result = total * 0.05
"""
    )
