# models/invoice_template.py
from odoo import fields, models, api, Command


class InvoiceTemplate(models.Model):
    _name = 'invoice.template'
    _description = 'Invoice Template'
    _order = 'name'

    name = fields.Char(required=True, string='Template Name')
    note = fields.Text(string='Note')
    line_ids = fields.One2many(
        'invoice.template.line',
        'template_id',
        string='Lines'
    )
    total_type_id = fields.Many2one(
        'invoice.total.type',
        string='Total Calculation Method',
        help='Select a total calculation method to apply when this template is used'
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Invoicing Journal',
        domain=[('type', 'in', ('sale', 'general'))],
        help='If set, invoice with this template will use this journal'
    )
    active = fields.Boolean(default=True)


# Extend account.move to add template field and onchange
class AccountMove(models.Model):
    _inherit = 'account.move'

    template_id = fields.Many2one(
        'invoice.template',
        string='Invoice Template',
        help='Select a template to pre-fill invoice lines'
    )

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Apply template to invoice when selected."""
        if not self.template_id:
            return {'value': {}}

        template = self.template_id

        # Get max sequence for new lines
        max_seq = max(self.invoice_line_ids.mapped('sequence'), default=0)

        # Build list of line values using Command.create format
        commands = []
        for template_line in template.line_ids.sorted('sequence'):
            max_seq += 10
            commands.append(Command.create({
                'product_id': template_line.product_id.id,
                'name': template_line.name or template_line.product_id.name,
                'quantity': template_line.quantity,
                'price_unit': template_line.price_unit or template_line.product_id.list_price,
                'sequence': max_seq,
            }))

        # Assign lines using commands
        if commands:
            self.invoice_line_ids = commands

        # Apply total type if template has one
        if template.total_type_id:
            self.total_type_id = template.total_type_id.id

        # Apply journal if template has one
        if template.journal_id:
            self.journal_id = template.journal_id.id

        # Clear template selection after applying
        self.template_id = False

        return {'value': {}}