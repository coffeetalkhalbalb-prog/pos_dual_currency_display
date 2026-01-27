/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {
    get isComplete() {
        return this.isRemaining && this.order.orderHasZeroRemaining;
    },

    get isIncompleteAndPositive() {
        return !this.isComplete && this.order.remainingDue > 0;
    },

    get order() {
        return this.pos.getOrder();
    },

    get isRemaining() {
        const isNegative = this.order.totalDue < 0;
        const remainingDue = this.order.remainingDue;

        if ((isNegative && remainingDue > 0) || (!isNegative && remainingDue <= 0)) {
            return false;
        } else {
            return true;
        }
    },

    get statusText() {
        if (!this.isRemaining) {
            return _t("Change");
        } else {
            return _t("Remaining");
        }
    },

    get amountText() {
        if (!this.isRemaining) {
            return this.pos.formatDualCurrency(this.order.change);
        } else {
            return this.pos.formatDualCurrency(this.order.remainingDue);
        }
    },

    get dualCurrencyEnabled() {
        return this.pos.isDualCurrencyEnabled();
    },

    get dualCurrencyAmount() {
        const total = this.currentOrder._prices?.original?.taxDetails?.total_amount || 0;
        return this.pos.formatDualCurrency(total);
    },

    get dualCurrencyConfig() {
        return this.pos.dualCurrencyConfig;
    },

    get dualCurrencyRemaining() {
        const remaining = this.currentOrder?.remainingDue || 0;
        return this.pos.formatDualCurrency(remaining);
    },
});
