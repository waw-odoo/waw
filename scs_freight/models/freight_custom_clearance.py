# See LICENSE file for full copyright and licensing details.
"""This file for custom clearance."""

from odoo import models, fields, api, _


class OperationCustom(models.Model):
    """Custom Clearance Model."""

    _name = 'operation.custom'
    _description = 'Custom Clearance'

    name = fields.Char(string="Name", default="Custom")
    operation_id = fields.Many2one('freight.operation', 'Freight Operation')
    agent_id = fields.Many2one('res.partner', string='Agent')
    date = fields.Date(string="Date")
    need_document = fields.Boolean("Need Document?")
    revision_count = fields.Integer(string="Revision",
                                    compute="_compute_count_revision")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'confirm'),
                              ('done', 'Done'), ('cancel', 'Cancel')],
                             default="draft")
    attachment_ids = fields.One2many('ir.attachment',
                                     'custom_id',
                                     string="Documents")
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.user.company_id)

    @api.onchange('operation_id')
    def change_agent(self):
        """Method to change the agent name."""
        for operation in self:
            operation.agent_id = operation.operation_id and \
                operation.operation_id.agent_id and \
                operation.operation_id.agent_id.id or False

    @api.constrains('operation_id')
    def _check_operation_id(self):
        for custom in self:
            if custom.operation_id:
                customs = self.env['operation.custom'].search(
                    [('operation_id', '=', custom.operation_id.id),
                     ('state', 'not in', ['done', 'cancel']),
                     ('id', '!=', custom.id)], limit=1)
                if customs:
                    raise Warning(_("%s have already custom activity.") %
                                  (customs.operation_id.name))

    def _compute_count_revision(self):
        for custom in self:
            revisons = self.env['operation.custom.revision'].search([
                ('custom_id', '=', custom.id)])
            custom.revision_count = len(revisons)

    def action_confirm_custom(self):
        """Confirm Clearance for the send agent."""
        for custom in self:
            custom_name = 'Custom'
            if custom.operation_id:
                custom_name = 'Custom-' + str(custom.operation_id.name)
            custom.write({'state': 'confirm', 'name': custom_name})
            custom.operation_id.write({'state': 'custom'})
            template = self.env.ref('scs_freight.custom_clearence_agent')
            mail_vals = {
                'attachment_ids': custom.attachment_ids.ids or []}
            if template:
                template.send_mail(custom.id, force_send=True,
                                   raise_exception=False,
                                   email_values=mail_vals)

    def action_clear_custom(self):
        """Done Clearance Activity."""
        for custom in self:
            custom.state = 'done'
            if custom.operation_id:
                custom.operation_id.state = 'in_transit'

    def action_cancel_custom(self):
        """Cancel Clearance Activity."""
        for custom in self:
            custom.state = 'cancel'
            custom.operation_id.state = 'in_progress'

    def operation_custom_revision(self):
        """Show particuler Revision for Clearance."""
        self.ensure_one()
        action = self.env.ref(
            'scs_freight.action_operation_custom_revision').read()[0]
        for custom in self:
            revisons = self.env['operation.custom.revision'].search([
                ('custom_id', '=', custom.id)])
            action['domain'] = [('id', 'in', revisons.ids)]
            action['context'] = {}
        return action


class OperationCustomRevision(models.Model):
    """Model for operation custom revision."""

    _name = 'operation.custom.revision'
    _description = 'Custom Clearance Rivision'

    name = fields.Char(string="Name")
    operation_id = fields.Many2one('freight.operation',
                                   string='Freight Operation')
    custom_id = fields.Many2one('operation.custom', string="Operation")
    agent_id = fields.Many2one('res.partner', string='Agent')
    operator_id = fields.Many2one('res.users', string="Operator")
    date = fields.Date(string="Date")
    reason = fields.Text(string="Reason")
    revision_doc_ids = fields.One2many('revision.doc', 'revision_id',
                                       string="Revisions")
    attachment_ids = fields.One2many('ir.attachment',
                                     'custom_id',
                                     string="Documents")


class RevsionDoc(models.Model):
    """Revision Doc List."""

    _name = 'revision.doc'
    _description = "Revision Document Lists"

    name = fields.Char(string='Doc Name')
    revision_id = fields.Many2one('operation.custom.revision',
                                  string="Revision")
