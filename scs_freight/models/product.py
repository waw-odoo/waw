# See LICENSE file for full copyright and licensing details.
"""This file contain operation related to service."""

from odoo import models, fields


class Product(models.Model):
    """Inherit Product Model."""

    _inherit = 'product.product'

    vendor_id = fields.Many2one('res.partner', string="Vendor",
                                domain="[('is_vendor', '=', True)]")
