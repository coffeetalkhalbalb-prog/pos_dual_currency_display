/** @odoo-module **/

import { ProductListPage } from "@pos_self_order/app/pages/product_list_page/product_list_page";
import { OrderWidget } from "@pos_self_order/app/components/order_widget/order_widget";
import { CartPage } from "@pos_self_order/app/pages/cart_page/cart_page";
import { patch } from "@web/core/utils/patch";

const mixin = {
    getFormatedPrice(price) {
        const {
            rate,
            position,
            rounding,
            symbol,
            decimal_places
        } = this.selfOrder.config.dual_currency_id;

        let convertedAmount = price * rate;

        let decimals = decimal_places;
        if (rounding >= 1) {
            convertedAmount = Math.round(convertedAmount / rounding) * rounding;
            decimals = 0;
        } else if (rounding > 0 && rounding < 1) {
            decimals = Math.max(0, Math.round(Math.log10(1 / rounding)));
        }

        const nf = new Intl.NumberFormat(undefined, {
            minimumFractionDigits: 0,
            maximumFractionDigits: decimals,
            useGrouping: true,
        });

        const formatted = nf.format(convertedAmount);
        return position === 'after'
            ? `${formatted} ${symbol}`
            : `${symbol} ${formatted}`;
    },
};
patch(ProductListPage.prototype, {
    ...mixin,

    getSecondaryPrice(product) {
        const price = this.selfOrder.getProductDisplayPrice(product);

        return this.getFormatedPrice(price);
    }
});
patch(OrderWidget.prototype, {
    ...mixin,

    get secondaryTotal() {
        const total = this.selfOrder.orderLineNotSend.priceWithTax;
        return this.getFormatedPrice(total);
    }
});

patch(CartPage.prototype, {
    ...mixin,

    get secondaryTotal() {
        const total = this.selfOrder.orderLineNotSend?.priceWithTax 
                        || this.totalPriceAndTax?.priceWithTax
                        || 0;
        return this.getFormatedPrice(total);
    },

    getSecondaryLinePrice(line) {
        const price = this.getPrice(line) || 0;
        return this.getFormatedPrice(price);
    }
});