# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Freight management system',
    'version' : '1.1',
    'author' : 'Iheb Ltaief',
    'summary': ' Freight management and Tracking system',
    'sequence': 1,
    'description': """
        - Management of freight operations.
        - Tracking system
    """,
    'category': 'Fleet',
    'icon_image': 'static/description/icon.png',
    'website': 'https://www.odoo.com',
    'images' : [],
    'depends' : ['stock_picking_batch', 'account_invoicing','fleet', 'hr','theme_clean' ],
    'data': [
        'security/freight_system_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/invoice_data.xml',
        'data/website.xml',
        'views/product.xml',
        'views/res_users.xml',
        'views/stock_picking.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
        'views/warehouse.xml',
        'views/route.xml',
        'views/fleet.xml',
        'views/policy_view.xml',
        'wizard/policy_validation.xml',
        'wizard/policy_receipt.xml',
        'wizard/confirm_return.xml',
        'views/invoice.xml',
        'views/trips.xml',
        'views/freight_system_menu.xml',
        'views/configurations.xml',
        'report/tmp_external_layout.xml',
        'report/report_policy.xml',
        'report/product_product_templates.xml',
        'report/label_vehicle.xml',
        'report/report_trip.xml',
        'report/report_trip_delivery.xml',
        'views/website_track.xml'
    ],
    'demo': [
    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
