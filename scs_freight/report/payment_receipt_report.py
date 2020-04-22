# See LICENSE file for full copyright and licensing details.
"""Payment Receipt Report AbstractModel."""

from odoo import api, models, _
from odoo.exceptions import Warning


class InvPaymnetReceiptReport(models.AbstractModel):
    """Payment Receipt Report AbstractModel."""

    _name = 'report.scs_freight.inv_payment_receipt_report'
    _description = 'Report Invoice Payment Reciept'

    def get_payment_details(self, invoice=False):
        """Method to get the invoice payment details."""
        payments = self.env['account.payment'].search([
            ('invoice_ids', 'in', [invoice.id])])
        return payments

    @api.model
    def _get_report_values(self, docids, data=None):
        """Method to render the Invoice Payment Receipt report template."""
        docs = []
        inv_obj = self.env['account.move']
        if docids:
            invoices = inv_obj.search([('operation_id', 'in', docids),
                                       ('type', '=', 'out_invoice')])
            docs = self.env['freight.operation'].browse(docids)
        if not invoices:
            raise Warning(_("Current Shipping order have no Invoice!!"))
        docargs = {
            'docids': docids,
            'doc_model': 'freight.operation',
            'docs': docs,
            'data': data,
            'get_payment_details': self.get_payment_details,
        }
        return docargs


class BillPaymnetReceiptReport(models.AbstractModel):
    """Payment Receipt Report AbstractModel."""

    _name = 'report.scs_freight.bill_payment_receipt_report'
    _description = 'Report Bill Payment Reciept'

    def get_bill_payment_details(self, invoice=False):
        """Method to get the bill payment details."""
        payments = self.env['account.payment'].search([
            ('invoice_ids', 'in', [invoice.id])])
        return payments

    @api.model
    def _get_report_values(self, docids, data=None):
        """Method to render the Bill Payment Receipt report template."""
        docs = []
        inv_obj = self.env['account.move']
        if docids:
            bills = inv_obj.search([('operation_id', 'in', docids),
                                    ('type', '=', 'in_invoice')])
            docs = self.env['freight.operation'].browse(docids)
        if not bills:
            raise Warning(_("Current Shipping order have no Bill!!"))
        docargs = {
            'docids': docids,
            'doc_model': 'freight.operation',
            'docs': docs,
            'data': data,
            'get_bill_payment_details': self.get_bill_payment_details,
        }
        return docargs
