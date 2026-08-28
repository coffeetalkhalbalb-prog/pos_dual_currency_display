import { patch } from "@web/core/utils/patch";
import { ProductPricelistItem } from "@point_of_sale/app/models/product_pricelist_item";

patch(ProductPricelistItem.prototype, {
    _load_pos_data_fields() {
        const fields = super._load_pos_data_fields();

        if (!fields.includes("margin_percentage")) {
            fields.push("margin_percentage");
        }

        return fields;
    },
});