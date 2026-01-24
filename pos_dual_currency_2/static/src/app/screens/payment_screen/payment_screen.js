/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    get dualCurrencyEnabled() {
        return this.pos.isDualCurrencyEnabled();
    },

    get dualCurrencyAmount() {
        const total = this.currentOrder?.get_total_with_tax() || 0;
        return this.pos.formatDualCurrency(total);
    },

    get dualCurrencyConfig() {
        return this.pos.dualCurrencyConfig;
    },

    get dualCurrencyRemaining() {
        const remaining = this.currentOrder?.get_due() || 0;
        return this.pos.formatDualCurrency(remaining);
    },
});
