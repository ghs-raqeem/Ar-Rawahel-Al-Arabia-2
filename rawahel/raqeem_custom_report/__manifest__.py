# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Raqeem custom report',
    'version' : '1.1',
    'author' : 'Iheb Ltaief',
    'summary': 'Raqeem custom report',
    'sequence': 2,
    'description': """

    """,
    'category': 'Report',
    'icon_image': 'static/description/icon.png',
    'website': 'https://www.odoo.com',
    'images' : [],
    'depends' : ['base', 'web'],
    'data': [
        'tmp_external_layout.xml',
    ],
    'demo': [
    ],
    'qweb': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
