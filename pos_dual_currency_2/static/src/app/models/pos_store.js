/** @odoo-module */

import { PosStore } from "@point_of_sale/app/services/pos_store";

import { patch } from "@web/core/utils/patch";
import { formatCurrency } from "@web/core/currency";

patch(PosStore.prototype, {
    dualCurrencyConfig: null,
    async setup() {
        await super.setup(...arguments);
        this.loadDualCurrencyConfig();
        
    },

    loadDualCurrencyConfig() {
        const config = this.config.raw;
        if (config.enable_dual_currency && config.dual_currency_id) {
            let rounding = config.dual_currency_rounding || 1;
            let exchangeRate = config.dual_currency_rate || 1.0;
            if (config.dual_currency_rate_type === 'auto') {
                const secondaryCurrency = this.models["res.currency"].getBy("id", config.dual_currency_id);

                return this.dualCurrencyConfig = {
                    enabled: config.enable_dual_currency,
                    currencyId: secondaryCurrency.id,
                    currencyName: secondaryCurrency.name,
                    exchangeRate: secondaryCurrency.rate,
                    rounding: secondaryCurrency.rounding,
                    currencySymbol: secondaryCurrency.symbol,
                    displayPosition: secondaryCurrency.position || 'below',
                    decimalPlaces: secondaryCurrency.decimal_places || 2
                };
            }
            this.dualCurrencyConfig = {
                enabled: config.enable_dual_currency,
                currencyId: config.dual_currency_id[0],
                currencyName: config.dual_currency_id[1],
                exchangeRate: exchangeRate,
                rounding: rounding,
                currencySymbol: this.getCurrencySymbol(config.dual_currency_id),
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
        
        return amount * this.dualCurrencyConfig.exchangeRate;
    },

    formatDualCurrency(amount) {
        if (!this.dualCurrencyConfig || !this.dualCurrencyConfig.enabled) {
            return '';
        }

        let convertedAmount = this.convertToDualCurrency(amount);

        let rounding = this.dualCurrencyConfig.rounding;
        let digits = this.dualCurrencyConfig.decimalPlaces || [69, 0];
        let decimals = this.dualCurrencyConfig.decimalPlaces || digits[1];
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
        if (this.dualCurrencyConfig && this.dualCurrencyConfig.currencySymbol && this.dualCurrencyConfig.displayPosition === 'after') {
            return `${formatted} ${this.dualCurrencyConfig ? this.dualCurrencyConfig.currencySymbol : ''}`;
        } else {
            return `${this.dualCurrencyConfig ? this.dualCurrencyConfig.currencySymbol : ''} ${formatted}`.trim();
        }
    },


    isDualCurrencyEnabled() {
        return this.dualCurrencyConfig && this.dualCurrencyConfig.enabled;
    },

    async printReceipt({
        basic = false,
        order = this.getOrder(),
        printBillActionTriggered = false,
    } = {}) {
        order.dual_currency_data = {};
        if (this.isDualCurrencyEnabled() && order) {
            const total = order._prices?.original?.taxDetails?.total_amount || 0;
            order.dual_currency_data.dual_currency_enabled = true;
            order.dual_currency_data.dual_currency_symbol = this.dualCurrencyConfig.currencySymbol;
            order.dual_currency_data.dual_currency_rate = this.dualCurrencyConfig.exchangeRate;
            order.dual_currency_data.dual_currency_total = this.formatDualCurrency(total);
            order.dual_currency_data.dual_currency_name = this.dualCurrencyConfig.currencyName;
        } else {
            order.dual_currency_data.dual_currency_enabled = false;
        }
        return super.printReceipt({basic, order, printBillActionTriggered});

    },
});
