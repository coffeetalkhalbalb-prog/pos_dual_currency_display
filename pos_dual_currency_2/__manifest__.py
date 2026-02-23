# -*- coding: utf-8 -*-
{
    'name': 'POS Dual Currency Display 2',
    'version': '19.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Display dual currency conversion in POS with real-time rates',
    'description': """
        POS Dual Currency Display
        =========================
        * Display secondary currency on POS register total
        * Real-time currency conversion
        * Display dual currency on receipt print
        * Configurable exchange rate and currency
    """,
    'author': 'haha',
    'depends': ['point_of_sale', 'pos_self_order', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            # Check if this file is actually a template (starting with <templates>)
            # If it is a backend view (starting with <odoo>), it MUST be in 'data', not 'assets'
            'pos_dual_currency_2/static/src/xml/pos_dual_currency_templates.xml', 
            'pos_dual_currency_2/static/src/app/screens/product_screen/product_screen.js',
            'pos_dual_currency_2/static/src/app/screens/product_screen/product_screen.xml',
            'pos_dual_currency_2/static/src/app/screens/payment_screen/payment_screen.js',
            'pos_dual_currency_2/static/src/app/screens/payment_screen/payment_screen.xml',
            'pos_dual_currency_2/static/src/app/models/pos_store.js',
            'pos_dual_currency_2/static/src/css/pos_dual_currency.css',
        ],
        'pos_self_order.assets': [
            'pos_dual_currency_2/static/src/app/screens/self_ordering/self_ordering.js',
            'pos_dual_currency_2/static/src/app/screens/self_ordering/self_ordering.xml'
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
