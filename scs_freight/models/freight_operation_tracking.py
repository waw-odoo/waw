# See LICENSE file for full copyright and licensing details.
"""This module contains feright operations."""

from odoo import models, fields


class OperationTracking(models.Model):
    """Track the Freight Operation."""

    _name = 'operation.tracking'
    _description = 'Detail for track order'

    source_location_id = fields.Many2one('freight.port',
                                         string='Source Location')
    dest_location_id = fields.Many2one('freight.port',
                                       string='Dest Location')
    date = fields.Date(string='Date')
    activity = fields.Char(string='Activity')
    operation_id = fields.Many2one('freight.operation', string='Operation')
