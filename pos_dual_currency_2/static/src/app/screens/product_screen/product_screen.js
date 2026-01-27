/** @odoo-module */
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
   get dualCurrencyEnabled() {
        return this.pos.isDualCurrencyEnabled();
    },

    get dualCurrencyAmount() {
        const total = this.getOrder()._prices?.original?.taxDetails?.total_amount || 0;
        return this.formatDualCurrency(total);
    },

    get dualCurrencyConfig() {
        return this.dualCurrencyConfig;
    },
});
