from odoo import api, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    @api.model
    def _load_pos_data_fields(self, config):
        fields = super()._load_pos_data_fields(config)

        if "margin_percentage" not in fields:
            fields.append("margin_percentage")

        return fields