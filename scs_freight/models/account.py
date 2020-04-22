# See LICENSE file for full copyright and licensing details.
"""Account Model Related Opeartions."""

from odoo import models, fields


class AccountMove(models.Model):
    """Account Move(Invoice) Model."""

    _inherit = 'account.move'

    operation_id = fields.Many2one('freight.operation', string="Operation")


class AccountMoveLine(models.Model):
    """Account Move Line(Account Invoice Line) Model."""

    _inherit = 'account.move.line'

    service_id = fields.Many2one('operation.service', string="Service")
