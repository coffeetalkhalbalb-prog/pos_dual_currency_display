/** @odoo-module */
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
   get dualCurrencyEnabled() {
        console.log('hshshs', this.pos.isDualCurrencyEnabled());

        return this.pos.isDualCurrencyEnabled();
    },

    get dualCurrencyAmount() {
        console.log('this:', this);
        
        const total = this.getOrder()._prices?.original?.taxDetails?.total_amount || 0;
        console.log('getting total', this.formatDualCurrency(total));
        
        return this.formatDualCurrency(total);
    },

    get dualCurrencyConfig() {
        return this.dualCurrencyConfig;
    },
});
