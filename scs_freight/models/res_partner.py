# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResPartner(models.Model):
    """Inherit Partner Model."""

    _inherit = 'res.partner'

    agent = fields.Boolean(string="Is Agent?")
