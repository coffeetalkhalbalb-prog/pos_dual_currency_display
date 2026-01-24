from odoo import api
# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'
        
    dual_currency_rounding = fields.Float(
        string='Dual Currency Rounding',
        default=1.0,
        help='Rounding factor for the secondary currency (e.g. 10000 for LBP)'
    )

    @api.onchange('dual_currency_id', 'dual_currency_rate_type')
    def _onchange_dual_currency(self):
        """Update exchange rate, rounding, and amount per USD when currency or rate type changes"""
        if self.dual_currency_id:
            self.dual_currency_rounding = self.dual_currency_id.rounding
        if self.dual_currency_id and self.dual_currency_rate_type == 'auto':
            company_currency = self.company_id.currency_id
            if company_currency and self.dual_currency_id:
                # Always compute: units of secondary per 1 USD
                usd = self.env.ref('base.USD', raise_if_not_found=False)
                if usd and self.dual_currency_id != usd:
                    usd_rate = usd.rate or 1.0
                    secondary_rate = self.dual_currency_id.rate or 1.0
                    self.dual_currency_rate = secondary_rate / usd_rate
                elif usd and self.dual_currency_id == usd:
                    self.dual_currency_rate = 1.0
                else:
                    primary_rate = company_currency.rate or 1.0
                    secondary_rate = self.dual_currency_id.rate or 1.0
                    self.dual_currency_rate = secondary_rate / primary_rate

    enable_dual_currency = fields.Boolean(
        string='Enable Dual Currency Display',
        default=False,
        help='Enable dual currency display on POS screen and receipt'
    )
    dual_currency_id = fields.Many2one(
        'res.currency',
        string='Secondary Currency',
        help='Secondary currency to display'
    )
    dual_currency_rate = fields.Float(
        string='Exchange Rate',
        digits=(12, 6),
        default=1.0,
        help='Exchange rate from primary currency to secondary currency'
    )
    dual_currency_rate_type = fields.Selection([
        ('manual', 'Manual Rate'),
        ('auto', 'Automatic Rate'),
    ], string='Rate Type', default='manual',
       help='Manual: Use custom rate / Automatic: Use system currency rate')
    dual_currency_position = fields.Selection([
        ('below', 'Below Total'),
        ('beside', 'Beside Total'),
    ], string='Display Position', default='below',
       help='Position of dual currency display')

    @api.onchange('dual_currency_id', 'dual_currency_rate_type')
    def _onchange_dual_currency(self):
        """Update exchange rate when currency or rate type changes"""
        if self.dual_currency_id and self.dual_currency_rate_type == 'auto':
            company_currency = self.company_id.currency_id
            if company_currency and self.dual_currency_id:
                # Always compute: units of secondary per 1 USD
                # If company currency is USD, this is just the secondary currency's rate to USD
                # If not, convert via company currency
                usd = self.env.ref('base.USD', raise_if_not_found=False)
                if usd and self.dual_currency_id != usd:
                    # units per USD = (secondary.rate / usd.rate)
                    usd_rate = usd.rate or 1.0
                    secondary_rate = self.dual_currency_id.rate or 1.0
                    self.dual_currency_rate = secondary_rate / usd_rate
                elif usd and self.dual_currency_id == usd:
                    self.dual_currency_rate = 1.0
                else:
                    # fallback: use company/secondary
                    primary_rate = company_currency.rate or 1.0
                    secondary_rate = self.dual_currency_id.rate or 1.0
                    self.dual_currency_rate = secondary_rate / primary_rate

    def get_dual_currency_config(self):
        """Return dual currency configuration for POS"""
        self.ensure_one()
        if not self.enable_dual_currency or not self.dual_currency_id:
            return {}
        
        return {
            'enabled': self.enable_dual_currency,
            'currency_name': self.dual_currency_id.name,
            'currency_symbol': self.dual_currency_id.symbol,
            'currency_position': self.dual_currency_id.position,
            'exchange_rate': self.dual_currency_rate,
            'display_position': self.dual_currency_position,
            'decimal_places': self.dual_currency_id.decimal_places,
        }
    
class PosConfig(models.Model):
    _inherit = 'pos.config'

    # ... (Your existing fields and methods) ...
    
    @api.model
    def _load_pos_data_read(self, records, config):
        res = super()._load_pos_data_read(records, config)
        
        for record_data in res:
            source_record = records.filtered(lambda r: r.id == record_data['id'])
            
            # The error is here: source_record.currency_id is a browse record object
            # record_data.update({'currency_id': source_record.currency_id, ...}) 

            record_data.update({
                'enable_dual_currency': source_record.enable_dual_currency,
                'dual_currency_rate': source_record.dual_currency_rate,
                'dual_currency_position': source_record.dual_currency_position,
                # Map Many2one correctly as an ID (int) or an array [id, name] if needed
                'currency_id': source_record.currency_id.id if source_record.currency_id else False, # <--- FIXED
                'dual_currency_id': [source_record.dual_currency_id.id, source_record.dual_currency_id.name] 
                                    if source_record.dual_currency_id else False,
            })
        return res

    
class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _load_pos_data_fields(self, config_id):
        # DO NOT add config fields here. Only add fields that belong to the pos.session table.
        return super()._load_pos_data_fields(config_id)
