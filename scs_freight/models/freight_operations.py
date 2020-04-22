# See LICENSE file for full copyright and licensing details.
"""This module contain feright operations."""

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class FreightOperation(models.Model):
    """Freight Operaton Model."""

    _name = 'freight.operation'
    _description = 'Freight Operations'

    name = fields.Char(string="Name", copy=False)
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.user.company_id)
    direction = fields.Selection([('import', 'Import'), ('export', 'Export')],
                                 string='Direction', default="import")
    transport = fields.Selection([('land', 'Land'), ('ocean', 'Ocean'),
                                  ('air', 'Air')], default="land",
                                 string="Transport")
    ocean_shipping = fields.Selection([('fcl', 'FCL'), ('lcl', 'LCL')],
                                      string='Ocean Shipping',
                                      help="""FCL: Full Conteiner Load. \
                                            LCL: Less Conteiner Load.""")
    land_shipping = fields.Selection([('ftl', 'FTL'), ('ltc', 'LTL')],
                                     string='Land Shipping',
                                     help="""FTL: Full Truckload.
                                            LTL: Less Then Truckload.""")
    customer_id = fields.Many2one('res.partner', string="Customer")
    consignee_id = fields.Many2one('res.partner', string="Consignee")
    operator_id = fields.Many2one('res.users', string='Operator',
                                  default=lambda self: self.env.user.id)
    loading_port_id = fields.Many2one('freight.port', string="Loading Port")
    discharg_port_id = fields.Many2one('freight.port',
                                       string="Discharging Port")
    voyage_no = fields.Char(string='Voyage No')
    vessel_id = fields.Many2one('freight.vessels', string="Vessel",
                                domain="[('transport', '=', transport)]")
    airline_id = fields.Many2one('freight.airline', string="Air Line")
    note = fields.Text(string="Notes")
    agent_id = fields.Many2one('res.partner', string='Agent')
    operation_line_ids = fields.One2many(
        'freight.operation.line', 'operation_id', string="Order")
    routes_ids = fields.One2many(
        'operation.route', 'operation_id', string="Routes")
    service_ids = fields.One2many('operation.service', 'operation_id',
                                  string="Services")
    tracking_ids = fields.One2many('operation.tracking', 'operation_id',
                                   string="Trackings")
    state = fields.Selection([('draft', 'New'),
                              ('confirm', 'Confirm'),
                              ('in_progress', 'In Progress'),
                              ('custom', 'Custom'),
                              ('in_transit', 'In Transit'),
                              ('recived', 'Received'),
                              ('delivered', 'Delivered'),
                              ('cancel', 'Cancel')],
                             default="draft", string="Status")
    order_date = fields.Datetime(string='Order Date',
                                 default=datetime.now())
    company_id = fields.Many2one(
        'res.company', string="Company", default=lambda self: self.env.user.company_id)
    exp_send_date = fields.Date(string='Expected Send Date',
                                help="Expected Send Date")
    act_send_date = fields.Date(string='Actual Send Date',
                                help="Actual Send Date")
    exp_rec_date = fields.Date(string='Expected Receive Date',
                               help="Expected Received Date")
    act_rec_date = fields.Date(string='Actual Receive Date',
                               help="Actual Received Date")
    opp_party_id = fields.Many2one('res.partner', string="Party")
    invoice_id = fields.Many2one('account.move', string="Invoice", copy=False)
    bill_id = fields.Many2one('account.move', string="Bill")
    exp_inv_payment = fields.Float(
        string='Sale Amount', compute="_compute_expected_recivable_payment")
    exp_bill_payment = fields.Float(
        string='Cost Amount', compute="_compute_expected_payable_payment")
    exp_payment_margin = fields.Float(compute="_compute_exp_payment_margin",
                                      string="Expected Margin")
    act_inv_payment = fields.Float(string='Act Rec Payment',
                                   compute="_compute_actual_recivable_payment",
                                   help="Actual Recivable Payment")
    act_bill_payment = fields.Float(string='Act Pay Payment',
                                    compute="_compute_actual_payable_payment",
                                    help="Actual Payable Payment")
    act_payment_margin = fields.Float(string='Actual Margin',
                                      compute="_compute_act_payment_margin",
                                      store=True)
    inv_amount_due = fields.Float(compute="_compute_inv_amount_due",
                                  string="Invoice Amount Due")
    bill_amount_due = fields.Float(compute="_compute_bill_amount_due",
                                   string="Bill Amount Due")
    total_service = fields.Integer(
        string='Total Services', compute="_compute_total_services")
    total_custom = fields.Integer(
        string='Custom Clearance', compute="_compute_total_custom")
    total_weight = fields.Float(string='Total Weight', store=True,
                                compute="_compute_weight_and_volume")
    total_volume = fields.Float(string='Total Volume', store=True,
                                compute="_compute_weight_and_volume")
    bill_count = fields.Integer(compute='count_bill', string="Bill")
    invoice_count = fields.Integer(compute='count_bill', string="Invoice")
    service_count = fields.Integer(compute='count_bill')
    # income_acc_id = fields.Many2one("account.account",
    #                                 string="Income Account")
    # expence_acc_id = fields.Many2one("account.account",
    #                                  string="Expense Account")
    # amount_due_margin = fields.Float(compute="_compute_amount_due_margin")

    def count_bill(self):
        """Method to count Invoice, Bill and Service."""
        obj = self.env['account.move']
        obj1 = self.env['operation.service']
        for operation in self:
            operation.bill_count = obj.search_count(
                [('operation_id', '=', operation.id), ('type', '=', 'in_invoice')])
            operation.invoice_count = obj.search_count(
                [('operation_id', '=', operation.id), ('type', '=', 'out_invoice')])
            operation.service_count = obj1.search_count(
                [('operation_id', '=', operation.id)])

    @api.constrains('order_date', 'exp_send_date',
                    'act_send_date', 'exp_rec_date', 'act_rec_date')
    def _check_date(self):
        for operation in self:
            order_date = operation.order_date and operation.order_date.date()
            if operation.exp_send_date and \
                    operation.exp_send_date < order_date:
                raise Warning(_("Expected Send date should be greater or"
                                "equals to Order Date !!"))
            elif operation.act_send_date and \
                    operation.act_send_date < order_date:
                raise Warning(_("Actual Send date should be greater or"
                                "equals to Order Date !!"))
            elif operation.exp_rec_date and \
                    operation.exp_rec_date < order_date:
                raise Warning(_("Expected Received date should be greater or"
                                "equals to Order Date !!"))
            elif operation.act_rec_date and \
                    operation.act_rec_date < order_date:
                raise Warning(_("Actual Received date should be greater or"
                                "equals to Order Date !!"))

    @api.constrains('operation_line_ids')
    def _check_container_capacity(self):
        for operation in self:
            for line in operation.operation_line_ids:
                containers = operation.operation_line_ids.filtered(
                    lambda rec: rec.container_id.id == line.container_id.id)
                order_weight = order_volume = 0.0
                for container in containers:
                    order_weight += container.exp_gross_weight or 0.0
                    order_volume += container.exp_vol or 0.0
                if order_weight > line.container_id.weight:
                    raise Warning(_("%s Container's Weight Capacity is %s! \n \
                    You planned more weight then container capacity!!")
                                  % (line.container_id.name,
                                     line.container_id.weight))

                if order_volume > line.container_id.volume:
                    raise Warning(_("%s Container's Volume Capacity is %s! \n \
                    You planned more volume then container capacity!!")
                                  % (line.container_id.name,
                                     line.container_id.volume))

    @api.onchange('discharg_port_id', 'transport')
    def _check_port_type(self):
        for operation in self:
            if operation.discharg_port_id and operation.transport:
                if operation.transport == 'land':
                    if not operation.discharg_port_id.is_land:
                        raise Warning(_("%s port have no land route!") %
                                      (operation.discharg_port_id.name))
                elif operation.transport == 'ocean':
                    if not operation.discharg_port_id.is_ocean:
                        raise Warning(_("%s port have no ocean route!") %
                                      (operation.discharg_port_id.name))
                elif operation.transport == 'air':
                    if not operation.discharg_port_id.is_air:
                        raise Warning(_("%s port have no air route!") %
                                      (operation.discharg_port_id.name))

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        """Onchange to set the consignee_id."""
        for operation in self:
            operation.consignee_id = operation.customer_id and \
                operation.customer_id.id or False

    def _compute_expected_recivable_payment(self):
        """Calculate the total invoice amount."""
        for operation in self:
            invs = self.env['account.move'].search([
                ('operation_id', '=', operation.id),
                ('type', '=', 'out_invoice'),
                ('state', 'not in', ['cancel'])])
            operation.exp_inv_payment = sum(invs.mapped('amount_total')) or 0.0

    def _compute_expected_payable_payment(self):
        """Calculate expected payable amount of Bill."""
        for operation in self:
            bills = self.env['account.move'].search([
                ('operation_id', '=', operation.id),
                ('type', '=', 'in_invoice'),
                ('state', 'not in', ['cancel'])])
            operation.exp_bill_payment = \
                sum(bills.mapped('amount_total')) or 0.0

    def _compute_exp_payment_margin(self):
        """Exapected Payment Margin.

        exp_inv_payment - exp_bill_payment = margin
        """
        for operation in self:
            operation.exp_payment_margin = operation.exp_inv_payment - \
                operation.exp_bill_payment

    def _compute_actual_recivable_payment(self):
        """Calculate Actual Receivable(Invoice) Payment."""
        for operation in self:
            invs = self.env['account.move'].search([
                ('operation_id', '=', operation.id),
                ('type', '=', 'out_invoice'),
                ('state', 'not in', ['cancel'])])
            total = 0.0
            for inv in invs:
                total += inv.amount_total - inv.residual
            operation.act_rec_payment = total

    def _compute_actual_payable_payment(self):
        """Calculate actual Payable(Bill) Payment."""
        for operation in self:
            bills = self.env['account.move'].search([
                ('operation_id', '=', operation.id),
                ('type', '=', 'in_invoice'),
                ('state', 'not in', ['cancel'])])
            total = 0.0
            for bill in bills:
                total += bill.amount_total - bill.residual
            operation.act_rec_payment = total

    def _compute_inv_amount_due(self):
        """Count Remaining invoice amount."""
        for operation in self:
            invs = self.env['account.move'].search([
                ('operation_id', '=', operation.id),
                ('type', '=', 'out_invoice'),
                ('state', 'not in', ['cancel'])])
            operation.inv_amount_due = \
                sum(invs.mapped('amount_residual')) or 0.0

    def _compute_bill_amount_due(self):
        """Count Remaining Bill amount."""
        for operation in self:
            bills = self.env['account.move'].search([
                ('operation_id', '=', operation.id),
                ('type', '=', 'in_invoice'),
                ('state', 'not in', ['cancel'])])
            operation.bill_amount_due = \
                sum(bills.mapped('amount_residual')) or 0.0

    def _compute_total_services(self):
        for operation in self:
            services = self.env['operation.service'].search(
                [('operation_id', '=', operation.id)])
            operation.total_service = len(services)

    def _compute_total_custom(self):
        for operation in self:
            customs = self.env['operation.custom'].search([
                ('operation_id', '=', operation.id)])
            operation.total_custom = len(customs)

    @api.depends('operation_line_ids')
    def _compute_weight_and_volume(self):
        for operation in self:
            total_weight = 0.0
            total_volume = 0.0
            for line in operation.operation_line_ids:
                total_weight += line.exp_gross_weight or 0.0
                total_volume += line.exp_vol or 0.0
            operation.total_weight = total_weight
            operation.total_volume = total_volume

    @api.model
    def create(self, vals):
        """Base ORM Method."""
        rec = super(FreightOperation, self).create(vals)
        if not vals.get('operation_line_ids', False):
            raise Warning(_("Add at least one order Line !!"))
        return rec

    def write(self, vals):
        """Overridden write Method."""
        rec = super(FreightOperation, self).write(vals)
        for freight in self:
            for route in freight.routes_ids:
                if route.service_ids:
                    route.service_ids.write({'operation_id': freight.id})
        return rec

    def unlink(self):
        """ORM Method delete the record."""
        for operation in self:
            if operation.state not in ['draft', 'cancel']:
                raise Warning(_("You can't delete this Shipping Operation.\n"
                                "Please set it Cancel before delete."))

    def action_confirm(self):
        """Action Confirm Method."""
        seq_obj = self.env['ir.sequence']
        for operation in self:
            operation_vals = {}
            for line in operation.operation_line_ids:
                if line.exp_vol > line.container_id.volume:
                    raise Warning(_("%s Container's Volume Capacity is %s !!\n"
                                    "You planned more volume then container"
                                    "capacity!!") % (line.container_id.name,
                                                     line.container_id.volume))
                if line.exp_gross_weight > line.container_id.weight:
                    raise Warning(_("%s Container's Weight Capacity is %s !!\n"
                                    "You planned more weight then container"
                                    "capacity!!") % (line.container_id.name,
                                                     line.container_id.weight))
            if not operation.name:
                operation_vals.update({
                    'name': seq_obj.next_by_code('freight.operation.direct')
                })
            route_val = {
                'route_operation': 'main_carrige',
                'source_location': operation.loading_port_id and
                operation.loading_port_id.id or False,
                'dest_location': operation.discharg_port_id and
                operation.discharg_port_id.id or False,
                'transport': operation.transport
            }
            operation_vals.update({
                'state': 'confirm',
                'routes_ids': [(0, 0, route_val)]
            })
            operation.write(operation_vals)
            containers = operation.operation_line_ids.mapped('container_id')
            if containers:
                containers.write({'state': 'reserve'})
            services = operation.mapped('routes_ids').mapped('service_ids')
            if services:
                services.write({'operation_id': operation.id})

    def action_cancel(self):
        """Cancel the Freight Operation."""
        for operation in self:
            operation.write({'state': 'cancel'})
            containers = operation.operation_line_ids.mapped('container_id')
            if containers:
                containers.write({'state': 'available'})

    def action_set_to_draft(self):
        """Set freight operation in 'draft' state."""
        inv_obj = self.env['account.move']
        for operation in self:
            invs = inv_obj.search([('operation_id', '=', operation.id),
                                   ('state', 'in', ['draft', 'cancel'])])
            invs.unlink()
            operation.write({'state': 'draft',
                             # 'sale_amount': 0.0,
                             # 'cost_amount': 0.0,
                             # 'margin': 0.0,
                             'act_inv_payment': 0.0,
                             'act_bill_payment': 0.0,
                             'inv_amount_due': 0.0,
                             'bill_amount_due': 0.0,
                             'routes_ids': [],
                             'tracking_ids': [],
                             'service_ids': []})
            containers = operation.operation_line_ids.mapped('container_id')
            if containers:
                containers.write({'state': 'available'})
            if operation.service_ids:
                operation.service_ids.write({'invoice_id': False,
                                             'inv_line_id': False,
                                             'bill_id': False,
                                             'bill_line_id': False})

    def action_invoice(self):
        """Create Invoice for the freight operation."""
        inv_obj = self.env['account.move']
        # inv_line_obj = self.env['account.move.line']
        for operation in self:
            services = operation.mapped('routes_ids').mapped('service_ids')
            services.write({'operation_id': operation.id})
            invoice = inv_obj.search([
                ('operation_id', '=', operation.id),
                ('type', '=', 'out_invoice'),
                ('state', '=', 'draft'),
                ('partner_id', '=', operation.consignee_id and
                    operation.consignee_id.id or False)], limit=1)
            done_line = operation.operation_line_ids.mapped('invoice_id')
            done_services = operation.service_ids.mapped('invoice_id')
            if len(done_line) < len(operation.operation_line_ids) \
                    or len(done_services) < len(operation.service_ids):
                if not invoice:
                    inv_val = {
                        'operation_id': operation.id or False,
                        'type': 'out_invoice',
                        'state': 'draft',
                        'partner_id': operation.consignee_id.id or False,
                        'invoice_date': fields.Date.context_today(self)
                        # 'account_id': operation.consignee_id.
                        # property_account_receivable_id.id or False,
                    }
                    invoice = inv_obj.create(inv_val)
                operation.write({'invoice_id': invoice.id})
                for line in operation.service_ids:
                    if not line.invoice_id and not line.inv_line_id:
                        # we did the below code to update inv line id
                        # in service, other wise we can do that by
                        # creating common vals
                        invoice.write({'invoice_line_ids': [(0, 0, {
                            'move_id': invoice.id or False,
                            'service_id': line.id or False,
                            # 'account_id': account_id.id or False,
                            'name': line.product_id and
                            line.product_id.name or '',
                            'product_id': line.product_id and
                            line.product_id.id or False,
                            'quantity': line.qty or 0.0,
                            'product_uom_id': line.uom_id and
                            line.uom_id.id or False,
                            'price_unit': line.list_price or 0.0
                        })]})
                        ser_upd_vals = {'invoice_id': invoice.id or False}
                        if invoice.invoice_line_ids:
                            inv_l_id = invoice.invoice_line_ids.search([
                                ('service_id', '=', line.id),
                                ('id', 'in', invoice.invoice_line_ids.ids)],
                                limit=1)
                            ser_upd_vals.update({
                                'inv_line_id': inv_l_id and
                                inv_l_id.id or False
                            })
                        line.write(ser_upd_vals)
                for line in operation.operation_line_ids:
                    if not line.invoice_id and not line.inv_line_id:
                        qty = 0.0
                        if line.billing_on == 'volume':
                            qty = line.exp_vol or 0.0
                        elif line.billing_on == 'weight':
                            qty = line.exp_gross_weight or 0.0
                        invoice.write({'invoice_line_ids': [(0, 0, {
                            'move_id': invoice.id or False,
                            'name': line.product_id and
                            line.product_id.name or '',
                            'product_id': line.product_id and
                            line.product_id.id or False,
                            'quantity': qty,
                            'product_uom_id': line.product_id and
                            line.product_id.uom_id and
                            line.product_id.uom_id.id or '',
                            'price_unit': line.price or 0.0,
                        })]})
                        ser_upd_vals = {'invoice_id': invoice.id or False}
                        if invoice.invoice_line_ids:
                            inv_l_id = invoice.invoice_line_ids.search([
                                ('service_id', '=', line.id),
                                ('id', 'in', invoice.invoice_line_ids.ids)],
                                limit=1)
                            ser_upd_vals.update({
                                'inv_line_id': inv_l_id and
                                inv_l_id.id or False
                            })
                        line.write(ser_upd_vals)

    # def operation_invoice(self):
    #     """Show Invoice for specific Freight Operation smart Button."""
    #     self.ensure_one()
    #     action = self.env.ref('account.action_move_out_invoice_type').read()[0]
    #     for operation in self:
    #         invoice = self.env['account.move'].search([
    #             ('operation_id', '=', operation.id),
    #             ('type', '=', 'out_invoice')])
    #         action['domain'] = [('id', 'in', invoice.ids)]
    #     return action

    def action_bill(self):
        """Create Bill for the freight operation."""
        bill_obj = self.env['account.move']
        # bill_line_obj = self.env['account.move.line']
        for operation in self:
            if not operation.service_ids:
                raise Warning(_("Direct Shipment have No any Service Line for Bill\n"
                                "Please add service line first to Generate Bill."))
            services = operation.mapped('routes_ids').mapped('service_ids')
            services.write({'operation_id': operation.id})
            for line in operation.service_ids:
                if not line.bill_id and not line.bill_line_id:
                    bill = bill_obj.search([
                        ('operation_id', '=', operation.id),
                        ('type', '=', 'in_invoice'),
                        ('state', '=', 'draft'),
                        ('partner_id', '=', line.vendor_id.id)], limit=1)
                    if not bill:
                        bill_val = {
                            'operation_id': operation.id or False,
                            'type': 'in_invoice',
                            'state': 'draft',
                            'partner_id': line.vendor_id.id or False,
                            'invoice_date': datetime.now().strftime(DTF)
                        }
                        bill = bill_obj.create(bill_val)
                        operation.write({'bill_id': bill.id})
                    # Used write Call because of Bill Invoice is shows
                    # unbalanced issue when we direct create the line.
                    bill.write({'invoice_line_ids': [(0, 0, {
                        'move_id': bill.id,
                        'service_id': line.id or False,
                        'product_id': line.product_id and
                        line.product_id.id or False,
                        'name': line.product_id and
                        line.product_id.name or '',
                        'quantity': line.qty or 1.0,
                        'product_uom_id': line.uom_id and
                        line.uom_id.id or False,
                        'price_unit': line.list_price or 0.0
                    })]})
                    ser_upd_vals = {
                        'bill_id': bill.id,
                    }
                    if bill.invoice_line_ids:
                        bill_l_id = bill.invoice_line_ids.search([
                            ('service_id', '=', line.id),
                            ('id', 'in', bill.invoice_line_ids.ids)], limit=1)
                        ser_upd_vals.update({
                            'bill_line_id': bill_l_id and bill_l_id.id or False
                        })
                    line.write(ser_upd_vals)

    # def operation_bill(self):
    #     """Show Bill for specific Freight Operation smart Button."""
    #     self.ensure_one()
    #     action = self.env.ref('account.action_move_in_invoice_type').read()[0]
    #     for operation in self:
    #         bill = self.env['account.move'].search([
    #             ('operation_id', '=', operation.id),
    #             ('type', '=', 'in_invoice')])
    #         action['domain'] = [('id', 'in', bill.ids)]
    #     return action

    def action_in_progress(self):
        """Send operation in In Progress state."""
        for operation in self:
            services = operation.mapped('routes_ids').mapped('service_ids')
            if services:
                services.write({'operation_id': operation.id})
            operation.write({'state': 'in_progress'})

    def action_in_transit(self):
        """Send operation in In Trnsit state."""
        for operation in self:
            services = operation.mapped('routes_ids').mapped('service_ids')
            if services:
                services.write({'operation_id': operation.id})
            operation.write({'state': 'in_transit'})

    def action_recived(self):
        """Send operation in In Received state."""
        for operation in self:
            services = operation.mapped('routes_ids').mapped('service_ids')
            if services:
                services.write({'operation_id': operation.id})
            operation.write({
                'state': 'recived',
                'act_rec_date': datetime.now().date()
            })
            containers = operation.operation_line_ids.mapped('container_id')
            if containers:
                containers.write({
                    'state': 'available',
                })

    def action_delivered(self):
        """Send Operation in Delivered State."""
        for operation in self:
            services = operation.mapped('routes_ids').mapped('service_ids')
            if services:
                services.write({'operation_id': operation.id})
            operation.write({'state': 'delivered'})
            containers = operation.operation_line_ids.mapped('container_id')
            if containers:
                containers.write({'state': 'available'})

    def operation_custom_clarance(self):
        """Show particular custom activity for that order."""
        self.ensure_one()
        action = self.env.ref(
            'scs_freight.action_operation_custom').read()[0]
        for operation in self:
            customs = self.env['operation.custom'].search([
                ('operation_id', '=', operation.id)])
            action['domain'] = [('id', 'in', customs.ids)]
        return action


class FreightOperationLine(models.Model):
    """Freight Operation Line Model."""

    _name = 'freight.operation.line'
    _description = 'Order Line'
    _rec_name = 'container_id'

    container_id = fields.Many2one('freight.container', string="Container")
    product_id = fields.Many2one('product.product', string='Goods')
    qty = fields.Float(string="Qty")
    billing_on = fields.Selection([('weight', 'Weight'),
                                   ('volume', 'Volume')], string="Billing On",
                                  default='weight')
    sale_price = fields.Float(string='Sale Price',
                              compute="_compute_calculate_sale_price",
                              store=True)
    price = fields.Float(string='Price')
    exp_gross_weight = fields.Float(string="Gross Weight",
                                    help="Expected Weight in kg.")
    exp_vol = fields.Float(string="Volume",
                           help="Expected Volume in m3 Measure")
    price_list_id = fields.Many2one('operation.price.list', string="Pricing")
    goods_desc = fields.Text(string="Description of Goods")
    operation_id = fields.Many2one('freight.operation', string='Operation')
    invoice_id = fields.Many2one('account.move', string="Invoice")
    inv_line_id = fields.Many2one('account.move.line',
                                  string="Invoice Line")

    @api.constrains('exp_gross_weight', 'exp_vol')
    def _check_weight_volume(self):
        for freight_line in self:
            if freight_line.exp_gross_weight < 0.0:
                raise Warning(_("You can't enter weight in Negative value!!"))
            if freight_line.exp_vol < 0.0:
                raise Warning(_("You can't enter volume in Negative value!!"))

    @api.onchange('container_id')
    def _onchange_container_id(self):
        for freight_line in self:
            if freight_line.container_id and \
                    freight_line.container_id.state == 'reserve':
                raise Warning(_("%s is not avilable!!") % (
                    freight_line.container_id.name))

    @api.onchange('price_list_id', 'billing_on')
    def _onchange_price(self):
        for line in self:
            if line.price_list_id:
                if line.billing_on == 'volume':
                    line.exp_gross_weight = 0.0
                    line.price = line.price_list_id.volume_price or 0.0
                else:
                    line.exp_vol = 0.0
                    line.price = line.price_list_id.weight_price or 0.0

    @api.depends('billing_on', 'price_list_id',
                 'exp_gross_weight', 'exp_vol')
    def _compute_calculate_sale_price(self):
        for line in self:
            if line.billing_on == 'weight':
                line.sale_price = line.exp_gross_weight * line.price
            elif line.billing_on == 'volume':
                line.sale_price = line.exp_vol * line.price


class OperationRoute(models.Model):
    """Freight Operation Route."""

    _name = 'operation.route'
    _description = 'Freight Operation Routes'

    route_operation = fields.Selection([
        ('main_carrige', 'Main Carriage'),
        ('picking', 'Picking'),
        ('oncarrige', 'On Carriage'),
        ('precarrige', 'Pre Carriage'),
        ('delivery', 'Delivery')], string="Route Operations")
    date = fields.Date(string='Send Date')
    recived_date = fields.Date(string='Received Date')
    source_location = fields.Many2one('freight.port', string="Source Location")
    dest_location = fields.Many2one('freight.port',
                                    string="Destination Location")
    transport = fields.Selection([('land', 'Land'), ('ocean', 'Ocean'),
                                  ('air', 'Air')], string="Transport")
    operation_id = fields.Many2one('freight.operation', string="Operation")
    service_ids = fields.One2many('operation.service', 'route_id',
                                  string="Services")
    cost_total = fields.Float(string="Cost", compute="_compute_cost_total",
                              store=True)
    sale_total = fields.Float(string="Sale", compute="_compute_sale_total",
                              store=True)

    @api.depends('service_ids')
    def _compute_cost_total(self):
        """Compute total cost amount."""
        for route in self:
            cost_total = 0.0
            if route.service_ids:
                cost_total = sum(route.service_ids.mapped('cost_total'))
            route.cost_total = cost_total

    @api.depends('service_ids')
    def _compute_sale_total(self):
        """Compute total sale amount."""
        for route in self:
            sale_total = 0.0
            if route.service_ids:
                sale_total = sum(route.service_ids.mapped('sale_total'))
            route.sale_total = sale_total

    # @api.multi
    # def name_get(self):
    #     """name_get method."""
    #     res = []
    #     for route in self:
    #         if route.source_location and route.dest_location:
    #             rec_str = route.source_location.name + ' to ' +\
    #                 route.dest_location.name
    #             res.append((route.id, rec_str))
    #     return res


class OperationService(models.Model):
    """Operation related Services."""

    _name = 'operation.service'
    _description = "Operation Sevices"

    product_id = fields.Many2one('product.product', string="Service")
    operation_id = fields.Many2one('freight.operation', string="Operation")
    route_id = fields.Many2one('operation.route', string="Route")
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    invoice_id = fields.Many2one('account.move', string="Invoice")
    inv_line_id = fields.Many2one('account.move.line',
                                  string="Invoice Line")
    bill_id = fields.Many2one('account.move', string="Bill")
    bill_line_id = fields.Many2one('account.move.line', string="Bill Line")
    qty = fields.Integer(string='QTY', default=1)
    uom_id = fields.Many2one('uom.uom', string="Unit of Mesure")
    route_service = fields.Boolean(string='Is Route Service', default=False)
    list_price = fields.Float(string="Sale Price")
    cost_price = fields.Float(string="Cost")
    sale_total = fields.Float(compute="_compute_sale_total",
                              string="Sale Total", store=True)
    cost_total = fields.Float(compute="_compute_cost_total",
                              string="Cost Total", store=True)

    @api.constrains('qty', 'list_price', 'cost_price')
    def _check_qty_and_price(self):
        """Constrain to check qty and price."""
        for service in self:
            if service.qty < 0:
                raise Warning(_("You can't enter Negative QTY for services!!"))
            if service.list_price < 0:
                raise Warning("You can't enter Sale Price in Negative \
                    for service!!")
            if service.cost_price < 0:
                raise Warning("You can't enter Cost Price in Negative \
                    for service!!")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Onchange to update list and cost price."""
        if self.product_id:
            self.update({
                'list_price': self.product_id.list_price or 0.0,
                'cost_price': self.product_id.standard_price or 0.0
            })

    @api.depends('qty', 'list_price')
    def _compute_sale_total(self):
        """Compute total sale amount."""
        for service in self:
            service.sale_total = service.qty * service.list_price or 0.0

    @api.depends('qty', 'cost_price')
    def _compute_cost_total(self):
        """Compute total cost amount."""
        for service in self:
            service.cost_total = service.qty * service.cost_price or 0.0
