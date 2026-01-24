/** @odoo-module */
import { registry } from "@web/core/registry";

// Patch POS to always load res.currency model
registry.category("pos_models_to_load").add("res.currency", {
    modelName: "res.currency",
    fields: ["name", "symbol", "rounding", "position", "digits"],
    domain: [], // load all currencies
    loaded: function(self, currencies) {
        // No-op, POS will store in self.models["res.currency"]
        return currencies;
    },
});
