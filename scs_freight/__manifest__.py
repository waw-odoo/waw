# See LICENSE file for full copyright and licensing details.

{
    # Module Info.
    "name": "Freight Management",
    "version": "13.0.1.0.0",
    "sequence": 1,
    "category": "Transport",
    "license": 'LGPL-3',
    "summary": """Freight Management System for Carriers, Transport,
                  Goods Import/Export, Shipping and
                  Transportation Solutions,
                  Freight Management Software.""",
    "description": """Freight Management System for Carriers, Transport,
                      Goods Import/Export, Shipping and
                      Transportation Solutions,
                      Freight Management Software.""",

    # Author
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",

    # Dependencies
    "depends": ['product', 'account'],

    # Data
    "data": [
        'security/freight_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_template.xml',
        'views/operation_service_view.xml',
        'views/freight_operation_view.xml',
        'wizard/wiz_order_track_view.xml',
        'wizard/wiz_custom_revision_reason_view.xml',
        'wizard/wiz_set_shipping_date_view.xml',
        'views/freight_custom_clearance_view.xml',
        'views/freight_config.xml',
        'views/res_partner.xml',
        'views/product.xml',
        'views/operation_tracking_view.xml',
        'report/shipping_analysis.xml',
        'report/shipping_order.xml',
        'report/payment_receipt_report_view.xml',
        'report/report_registration.xml',
    ],

    # Odoo App Store Specific
    'images': ['static/description/odoo-app-freight.jpg'],

    # Technical
    "application": True,
    "installable": True,
    'price': 80,
    'currency': 'EUR',
}
