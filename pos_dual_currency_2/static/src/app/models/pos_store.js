/** @odoo-module */

import { PosStore } from "@point_of_sale/app/services/pos_store";

import { patch } from "@web/core/utils/patch";
import { formatCurrency } from "@web/core/currency";

patch(PosStore.prototype, {
    dualCurrencyConfig: null,
    async setup() {
        await super.setup(...arguments);
        this.loadDualCurrencyConfig();
        console.log(this.dualCurrencyConfig);
        
    },

    loadDualCurrencyConfig() {
        console.log(this.config, this.config.raw);
        const config = this.config.raw;
        if (config.enable_dual_currency && config.dual_currency_id) {
            let rounding = config.dual_currency_rounding || 1;
            let exchangeRate = config.dual_currency_rate || 1.0;
            if (config.dual_currency_rate_type === 'auto' && config.dual_currency_amount_per_usd) {
                // If auto, correct the exchange rate based on amount per USD
                exchangeRate = 1.0 / config.dual_currency_amount_per_usd;
            }
            this.dualCurrencyConfig = {
                enabled: config.enable_dual_currency,
                currencyId: config.dual_currency_id[0],
                currencyName: config.dual_currency_id[1],
                exchangeRate: exchangeRate,
                rounding: rounding,
                currencySymbol: this.getCurrencySymbol(config.dual_currency_id[0]),
                displayPosition: config.dual_currency_position || 'below',
                decimalPlaces: 2
            };
        }
    },

    getCurrencySymbol(currencyId) {
        const currency = this.models['res.currency'].get(currencyId);
        
        return currency ? currency.symbol : 'LBP';
    },

    convertToDualCurrency(amount) {
        if (!this.dualCurrencyConfig || !this.dualCurrencyConfig.enabled) {
            return 0;
        }
        console.log({amount, rate: this.dualCurrencyConfig.exchangeRate});
        
        return amount * this.dualCurrencyConfig.exchangeRate;
    },

    formatDualCurrency(amount) {
        if (!this.dualCurrencyConfig || !this.dualCurrencyConfig.enabled) {
            return '';
        }

        let convertedAmount = this.convertToDualCurrency(amount);
        const currencyId = this.dualCurrencyConfig.currencyId;
        const currencyRecord = this.models['res.currency']?.get(currencyId) || null;
        console.log(this.models['res.currency'], currencyRecord);
        
        const symbol = this.dualCurrencyConfig.currencySymbol || currencyRecord?.symbol || '';

        let rounding = this.dualCurrencyConfig.rounding || (currencyRecord?.rounding ? Number(currencyRecord.rounding) : 0);
        let digits = currencyRecord?.digits || [69, 0];
        let decimals = digits[1];
        if (rounding >= 1) {
            // Round to nearest rounding (e.g. 10,000)
            convertedAmount = Math.round(convertedAmount / rounding) * rounding;
            decimals = 0;
        } else if (rounding > 0 && rounding < 1) {
            decimals = Math.max(0, Math.round(Math.log10(1 / rounding)));
        }

        // Format with grouping, use currency symbol position
        const nf = new Intl.NumberFormat(undefined, {
            minimumFractionDigits: 0,
            maximumFractionDigits: decimals,
            useGrouping: true,
        });
        let formatted = nf.format(convertedAmount);
        if (currencyRecord && currencyRecord.position === 'after') {
            return `${formatted} ${currencyRecord.symbol}`;
        } else {
            return `${currencyRecord ? currencyRecord.symbol : ''} ${formatted}`.trim();
        }
    },


    isDualCurrencyEnabled() {
        return this.dualCurrencyConfig && this.dualCurrencyConfig.enabled;
    },

    getReceiptHeaderData(order) {
        const result = super.getReceiptHeaderData(...arguments);
        
        if (this.isDualCurrencyEnabled() && order) {
            const total = order.get_total_with_tax();
            result.dual_currency_enabled = true;
            result.dual_currency_symbol = this.dualCurrencyConfig.currencySymbol;
            result.dual_currency_total = this.formatDualCurrency(total);
            result.dual_currency_name = this.dualCurrencyConfig.currencyName;
        } else {
            result.dual_currency_enabled = false;
        }
        
        return result;
    },
});
