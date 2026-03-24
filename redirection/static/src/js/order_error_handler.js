/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { OrderService } from "@pos_self_order/app/services/order_service";
import { _t } from "@web/core/l10n/translation";

patch(OrderService.prototype, {
    async sendOrder(...args) {
        const result = await super.sendOrder(...args);

        // 👇 Handle backend error
        if (result && result.error) {
            this.env.services.notification.add(result.error, {
                type: "danger",
            });

            return; // stop flow
        }

        return result;
    },
});