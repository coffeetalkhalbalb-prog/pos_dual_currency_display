{
    "name": "Custom Pricelists",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "summary": "POS pricelist based on cost and a configurable margin percentage",
    "description": """
Custom POS pricelist pricing based on product cost and a configurable
percentage of the normal sales margin.

Formula:

    Final Price = Cost + (Sales Price - Cost) × Margin %

Example:

    Cost = $5.00
    Sales Price = $8.00
    Margin = 50%

    Final Price = $5.00 + ($8.00 - $5.00) × 50%
                = $6.50

The margin percentage can be configured independently for each
pricelist rule.

Product variant/add-on extra prices are added to both the cost and
sales price before calculating the margin. Therefore, the add-on
price itself does not receive an additional margin.

The custom pricing calculation is intended for the Point of Sale.
""",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": [
        "product",
        "point_of_sale",
    ],
    "data": [
        "views/pricelist_item_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "custome_pricelists/static/src/js/margin_pricelist.js",
        ],
    },
    "installable": True,
    "application": False,
}