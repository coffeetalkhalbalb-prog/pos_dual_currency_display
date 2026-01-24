# -*- coding: utf-8 -*-

from odoo import models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _order_fields(self, ui_order):
        """Extend order fields to include dual currency info"""
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        
        # Add dual currency information for receipt
        if ui_order.get('dual_currency_info'):
            order_fields['dual_currency_info'] = ui_order['dual_currency_info']
        
        return order_fields

    def _export_for_ui(self, order):
        """Add dual currency data to receipt"""
        result = super(PosOrder, self)._export_for_ui(order)
        
        if order.config_id.enable_dual_currency and order.config_id.dual_currency_id:
            total = order.amount_total
            rate = order.config_id.dual_currency_rate
            converted_amount = total * rate
            
            result['dual_currency_enabled'] = True
            result['dual_currency_symbol'] = order.config_id.dual_currency_id.symbol
            result['dual_currency_total'] = '{:.2f}'.format(converted_amount)
            result['dual_currency_name'] = order.config_id.dual_currency_id.name
        else:
            result['dual_currency_enabled'] = False
            
        return result
