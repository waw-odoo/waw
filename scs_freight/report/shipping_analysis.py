# See LICENSE file for full copyright and licensing details.
"""Analysis report for the shipping operations."""

from odoo import models, fields
from odoo import tools


class ShippingOperationReport(models.Model):
    """Shipping operation Report Model."""

    _name = 'shipping.operation.report'
    _description = 'Shipping Operation Report'
    _auto = False

    name = fields.Char(string='Name')
    customer_id = fields.Many2one('res.partner', string="Customer")
    agent_id = fields.Many2one('res.partner', string='Agent')
    loading_port_id = fields.Many2one('freight.port', string="Loading Port")
    discharg_port_id = fields.Many2one('freight.port',
                                       string="Discharging Port")
    direction = fields.Selection([('import', 'Import'),
                                  ('export', 'Export')],
                                 string='Direction')
    transport = fields.Selection([('land', 'Land'), ('ocean', 'Ocean'),
                                  ('air', 'Air')], string="Transport")
    order_date = fields.Datetime(string='Order Date')
    inv_payment = fields.Float(string='Invoice Amount')
    bill_payment = fields.Float(string='Bill Amount')

    # @api.model_cr
    def init(self):
        """Initalization method."""
        tools.drop_view_if_exists(self.env.cr, 'shipping_operation_report')
        self.env.cr.execute("""create or replace view shipping_operation_report
            as (select id as id,
            name as name,
            customer_id as customer_id,
            agent_id as agent_id,
            loading_port_id as loading_port_id,
            discharg_port_id as discharg_port_id,
            direction as direction,
            transport as transport,
            order_date as order_date,
            (select sum(amount_total) from account_move \
            where operation_id=freight_operation.id and \
                type='out_invoice') as inv_payment,
                (select sum(amount_total) from account_move where
                operation_id=freight_operation.id and \
                type='in_invoice') as bill_payment
            from freight_operation)""")
