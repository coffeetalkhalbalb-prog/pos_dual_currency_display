# -*- coding: utf-8 -*-

{
     'name': 'POS Self-Order Alert',
     'version': '1.0',
     'depends': ['point_of_sale', 'bus'],
     'data': [],
     'assets': {
         'point_of_sale._assets_pos': [
             'self_ordering_alert/static/src/self_ordering_alert.js',
         ],
     },
     'installable': True,
 }