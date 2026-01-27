# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'
        
    enable_dual_currency = fields.Boolean(string='Enable Dual Currency Display', default=False)
    dual_currency_id = fields.Many2one('res.currency', string='Secondary Currency')
    dual_currency_rate = fields.Float(string='Exchange Rate', digits=(12, 6), default=1.0)
    dual_currency_rounding = fields.Float(string='Rounding factor', default=1.0)
    dual_currency_rate_type = fields.Selection([
        ('manual', 'Manual Rate'),
        ('auto', 'Automatic Rate'),
    ], string='Rate Type', default='manual')
    dual_currency_position = fields.Selection([
        ('below', 'Below Total'),
        ('beside', 'Beside Total'),
    ], string='Display Position', default='below')

    @api.onchange('dual_currency_id', 'dual_currency_rate_type')
    def _onchange_dual_currency(self):
        """Merged Onchange Logic"""
        if not self.dual_currency_id:
            return

        # 1. Handle Rounding
        self.dual_currency_rounding = self.dual_currency_id.rounding

        # 2. Handle Rate
        if self.dual_currency_rate_type == 'auto':
            company_curr = self.company_id.currency_id
            usd = self.env.ref('base.USD', raise_if_not_found=False)
            
            # Use Odoo's built-in _get_conversion_rate for accuracy
            if usd:
                # Get rate relative to USD
                self.dual_currency_rate = self.dual_currency_id.rate / (usd.rate or 1.0)
            else:
                # Fallback to company currency
                self.dual_currency_rate = self.dual_currency_id.rate / (company_curr.rate or 1.0)

class ResCurrency(models.Model):
    _inherit = 'res.currency'
    # By inheriting pos.load.mixin, this model becomes 'loadable' into POS
    _inherit = ['res.currency', 'pos.load.mixin']

    
    def _load_pos_data_fields(self, config_id):
        # Define fields needed in the POS frontend (e.g., name, symbol, rate)
        return ['name', 'symbol', 'rounding', 'decimal_places', 'rate', 'id', 'position']
    
    def _load_pos_data_domain(self, data, config):
        # This removes the default restriction and loads all active currencies
        return [('active', '=', True)]


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_config(self):
        """Add your custom fields to the config loader"""
        params = super()._loader_params_pos_config()
        params['search_params']['fields'].extend([
            'enable_dual_currency', 
            'dual_currency_id', 
            'dual_currency_rate', 
            'dual_currency_position',
            'dual_currency_rounding'
        ])
        return params

    def _load_pos_data_models(self, config_id):
        # Retrieve the standard list of models
        data_models = super()._load_pos_data_models(config_id)
        # Add 'res.currency' to the list if not already present
        if 'res.currency' not in data_models:
            data_models.append('res.currency')
        return data_models
