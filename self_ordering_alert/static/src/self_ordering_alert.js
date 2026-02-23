/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";

patch(PosStore.prototype, {
    setup() {
        super.setup(...arguments);

        console.log("🛎 Self-order alert PosStore patch loaded");

        // ✅ Access services via env (NOT hooks)
        this.busService = this.env.services.bus_service;
        this.notification = this.env.services.notification;

        this.busService.addChannel("pos_order_notification");
        this.busService.subscribe("new_self_order", (data) => {
            console.log({data})
            this._handleSelfOrderAlert(data);
        });
        this.busService.subscribe("update_self_order", (data) => {
            console.log('update', {data})

            this._handleSelfOrderAlert(data);
        });
    },

    _handleSelfOrderAlert(data) {
        console.log({data});
        
        // 🔊 Sound
        const audio = new Audio(
            "/self_ordering_alert/static/assets/audio.wav"
        );
        audio.play().catch(() => {});

        // 🔔 Notification
        this.notification.add(
            `${data?.message || "New self-order received!"}`,
            {
                sticky: true,
            }
        );
    },
});
