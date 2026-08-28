import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    # =========================================================
    # CUSTOM BASE TYPE
    # =========================================================

    base = fields.Selection(
        selection_add=[
            (
                "cost_sales_average",
                "Cost + Margin %",
            ),
        ],
        ondelete={
            "cost_sales_average": "cascade",
        },
    )

    # =========================================================
    # CONFIGURABLE MARGIN
    # =========================================================

    margin_percentage = fields.Float(
        string="Margin %",
        default=50.0,
        digits=(16, 2),
        help=(
            "Percentage of the margin between the normal sales price "
            "and cost that should be added to the cost."
        ),
    )

    # =========================================================
    # PRICE LABEL
    # =========================================================

    @api.depends(
        "compute_price",
        "fixed_price",
        "pricelist_id",
        "percent_price",
        "price_discount",
        "price_markup",
        "price_surcharge",
        "base",
        "base_pricelist_id",
        "margin_percentage",
    )
    def _compute_price_label(self):
        """
        Override Odoo's displayed Price description for our
        custom cost + margin rule.

        Normal Odoo rules are handled by the original method.
        """

        custom_items = self.filtered(
            lambda item: item.base == "cost_sales_average"
        )

        normal_items = self - custom_items

        # Let Odoo handle all normal pricelist rules.
        if normal_items:
            super(
                ProductPricelistItem,
                normal_items,
            )._compute_price_label()

        # Our custom rules.
        for item in custom_items:
            percentage = self._get_integer(
                item.margin_percentage
            )

            item.price = _(
                "Cost + %(percentage)s%% of margin",
                percentage=percentage,
            )

    # =========================================================
    # RULE DISCLAIMER / TOOLTIP
    # =========================================================

    @api.depends(
        "base",
        "compute_price",
        "price_discount",
        "price_markup",
        "price_round",
        "price_surcharge",
        "margin_percentage",
    )
    def _compute_rule_tip(self):
        """
        Override Odoo's standard formula explanation for the
        custom cost + margin rule.

        Instead of displaying:

            0% discount on sales price

        display:

            Cost + 50% of margin

            Final price = Cost + 50% × (Sales Price - Cost)
        """

        custom_items = self.filtered(
            lambda item: item.base == "cost_sales_average"
        )

        normal_items = self - custom_items

        # Let Odoo handle all normal rules.
        if normal_items:
            super(
                ProductPricelistItem,
                normal_items,
            )._compute_rule_tip()

        # Our custom rules.
        for item in custom_items:
            percentage = self._get_integer(
                item.margin_percentage
            )

            item.rule_tip = _(
                "Cost + %(percentage)s%% of margin\n"
                "Final price = Cost + "
                "%(percentage)s%% × (Sales Price - Cost)",
                percentage=percentage,
            )

    # =========================================================
    # BASE LABEL
    # =========================================================

    def _get_price_label_base_str(self):
        self.ensure_one()

        if self.base == "cost_sales_average":
            percentage = self._get_integer(
                self.margin_percentage
            )

            return _(
                "Cost + %(percentage)s%% of margin",
                percentage=percentage,
            )

        return super()._get_price_label_base_str()

    # =========================================================
    # CUSTOM PRICE CALCULATION
    # =========================================================

    def _compute_custom_cost_margin_price(
        self,
        product,
        quantity,
        uom,
        date,
        currency,
        **kwargs,
    ):
        """
        Calculate:

            Cost + X% of Margin

        Formula:

            margin = sales_price - cost

            final_price =
                cost + margin * margin_percentage / 100

        Add-on / variant extra prices are added to BOTH cost
        and sales price.

        Therefore the add-on itself receives no additional margin.

        Example:

            Cost = 5
            Sales Price = 8
            Add-on = 1
            Margin % = 50

            Adjusted Cost = 5 + 1 = 6
            Adjusted Sales = 8 + 1 = 9

            Margin = 9 - 6 = 3

            Final =
                6 + (3 * 50 / 100)

            Final = 7.50
        """

        currency.ensure_one()
        product.ensure_one()
        uom.ensure_one()

        # =====================================================
        # BASE COST
        # =====================================================

        cost_currency = product.cost_currency_id

        cost = product._price_compute(
            "standard_price",
            uom=uom,
            date=date,
        )[product.id]

        if cost_currency != currency:
            cost = cost_currency._convert(
                cost,
                currency,
                self.env.company,
                date,
                round=False,
            )

        # =====================================================
        # NORMAL SALES PRICE
        # =====================================================

        sales_currency = product.currency_id

        sales_price = product._price_compute(
            "list_price",
            uom=uom,
            date=date,
        )[product.id]

        if sales_currency != currency:
            sales_price = sales_currency._convert(
                sales_price,
                currency,
                self.env.company,
                date,
                round=False,
            )

        # =====================================================
        # ADD-ON / VARIANT EXTRA
        # =====================================================

        addon_price = (
            kwargs.get("price_extra")
            or kwargs.get("priceExtra")
            or 0.0
        )

        # Add the add-on to BOTH cost and sales price.
        #
        # This means the add-on itself carries no margin.

        adjusted_cost = cost + addon_price
        adjusted_sales_price = sales_price + addon_price

        # =====================================================
        # MARGIN
        # =====================================================

        margin = (
            adjusted_sales_price -
            adjusted_cost
        )

        # IMPORTANT:
        # Do not hardcode 50 here.
        #
        # The value comes from the pricelist rule.

        margin_percentage = self.margin_percentage or 0.0

        margin_to_keep = (
            margin *
            margin_percentage /
            100.0
        )

        final_price = (
            adjusted_cost +
            margin_to_keep
        )

        _logger.info(
            "[CUSTOM PRICELIST] "
            "rule=%s | product=%s | "
            "base_cost=%s | base_sales=%s | "
            "addon=%s | adjusted_cost=%s | "
            "adjusted_sales=%s | margin=%s | "
            "margin_percentage=%s | "
            "margin_to_keep=%s | "
            "final=%s",
            self.id,
            product.display_name,
            cost,
            sales_price,
            addon_price,
            adjusted_cost,
            adjusted_sales_price,
            margin,
            margin_percentage,
            margin_to_keep,
            final_price,
        )

        return final_price

    # =========================================================
    # ODOO PRICE COMPUTATION
    # =========================================================

    def _compute_price(
        self,
        product,
        quantity,
        uom,
        date,
        currency=None,
        **kwargs,
    ):
        """
        Intercept the custom base before Odoo's normal formula
        calculation.

        Odoo normally expects base to be:

            list_price
            standard_price
            pricelist

        Our custom base requires its own calculation.
        """

        # Some Odoo fallback paths can call this with an empty
        # recordset. Let Odoo handle those normally.
        if not self:
            return super()._compute_price(
                product,
                quantity,
                uom,
                date,
                currency=currency,
                **kwargs,
            )

        self.ensure_one()

        # =====================================================
        # CUSTOM RULE
        # =====================================================

        if self.base == "cost_sales_average":

            _logger.info(
                "[CUSTOM PRICELIST] "
                "_compute_price CUSTOM RULE %s for %s "
                "| margin=%s%%",
                self.id,
                product.display_name,
                self.margin_percentage,
            )

            return self._compute_custom_cost_margin_price(
                product,
                quantity,
                uom,
                date,
                currency,
                **kwargs,
            )

        # =====================================================
        # NORMAL ODOO RULE
        # =====================================================

        return super()._compute_price(
            product,
            quantity,
            uom,
            date,
            currency=currency,
            **kwargs,
        )

    # =========================================================
    # BACKWARD COMPATIBILITY
    # =========================================================

    def _compute_base_price(
        self,
        product,
        quantity,
        uom,
        date,
        currency,
        **kwargs,
    ):
        """
        Some Odoo code paths call _compute_base_price()
        directly.

        Handle our custom base here as well.
        """

        if not self:
            return super()._compute_base_price(
                product,
                quantity,
                uom,
                date,
                currency,
                **kwargs,
            )

        self.ensure_one()

        if self.base == "cost_sales_average":
            return self._compute_custom_cost_margin_price(
                product,
                quantity,
                uom,
                date,
                currency,
                **kwargs,
            )

        return super()._compute_base_price(
            product,
            quantity,
            uom,
            date,
            currency,
            **kwargs,
        )

    # =========================================================
    # ONCHANGE
    # =========================================================

    @api.onchange("base")
    def _onchange_base(self):
        super()._onchange_base()

        for item in self:
            if item.base == "cost_sales_average":
                item.update({
                    "price_discount": 0.0,
                    "price_markup": 0.0,
                    "price_surcharge": 0.0,
                    "price_round": 0.0,
                    "price_min_margin": 0.0,
                    "price_max_margin": 0.0,
                })

    # =========================================================
    # POS DATA
    # =========================================================

    @api.model
    def _load_pos_data_fields(self, config):
        """
        Make margin_percentage available to the POS frontend.
        """

        fields = super()._load_pos_data_fields(config)

        if "margin_percentage" not in fields:
            fields.append("margin_percentage")

        return fields