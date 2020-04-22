# See LICENSE file for full copyright and licensing details.
"""Model for the track operation."""

from odoo import models, fields, _
from odoo.exceptions import Warning


class WizTrackOperation(models.TransientModel):
    """Transiant Model for track Record."""

    _name = 'wiz.track.operation'
    _description = 'Track operation'

    order_number = fields.Char(string='Order Number')
    source_location = fields.Char(string='Source Location')
    dest_location = fields.Char(string='Dest Location')
    transport = fields.Char(string='Transport')
    status = fields.Char(string='Status')
    tracking_ids = fields.Many2many('operation.tracking',
                                    'tracking_track_operation_rel',
                                    'tracking_id', 'track_id',
                                    string="Tracking")

    def action_track(self):
        """Track the order via order Number."""
        self.ensure_one()
        for operation in self:
            order = self.env['freight.operation'].search([
                ('name', '=', operation.order_number)], limit=1)
            group = self.env.user.has_group(
                'scs_freight.freight_operation_admin')
            # if not order or order.customer_id != self.env.user.partner_id:
            #     raise Warning(_("No Order ID like [ %s ]!!") %
            #                   (operation.order_number))
            if not order:
                raise Warning(_("Shipment Order is not available with"
                            " this [ %s ] number.!!") %
                            (operation.order_number))
            if not group:
                if order.state in ['draft', 'confirm']:
                    raise Warning(_("Still no Activity for this order !!"))
                elif order.state == 'cancel':
                    raise Warning(_("This order was Cancelled. !!"))
            tracks = order.mapped('tracking_ids')
            track_list = []
            for track in tracks:
                track_list.append((0, 0, {
                    'source_location_id': track.source_location_id.id or False,
                    'dest_location_id': track.dest_location_id.id or False,
                    'date': track.date or False,
                    'activity': track.activity or ''}))
            operation.write({
                'transport': order.transport and order.transport.title() or '',
                'status': order.state and order.state.title() or '',
                'source_location': order.loading_port_id and
                order.loading_port_id.name or '',
                'dest_location': order.discharg_port_id and
                order.discharg_port_id.name or '',
                'tracking_ids': track_list
            })
            return {'view_type': 'form',
                    'view_mode': 'form',
                    'name': 'Track Shipping Order',
                    'res_model': 'wiz.track.operation',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'res_id': operation.id}
