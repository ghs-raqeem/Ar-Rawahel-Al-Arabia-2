# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2018 Odoo IT now <http://www.odooitnow.com/>
# See LICENSE file for full copyright and licensing details.
#
##############################################################################
{
    'name': 'Website Pre Loader',
    'category': 'Website',
    'summary': 'Website Pre Loader',

    'version': '0.1',
    'description': """
Website Pre Loader
==================
This module allows Pre Loader when page takes time to load in the website.
        """,

    'author': 'Odoo IT now',
    'website': 'http://www.odooitnow.com/',

    'depends': [
        'web'
        ],
    'data': [
        'views/assets.xml',
        'views/website_preloader_templates.xml'
    ],
    'images': ['images/OdooITnow_screenshot.png'],

    'price': 0.0,
    'currency': 'EUR',

    'installable': True,
    'application': False
}
