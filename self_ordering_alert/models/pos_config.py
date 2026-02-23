from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if hasattr(order, 'source') and order.source == 'mobile':
                items_info = [{
                    'product': line.product_id.display_name,
                    'quantity': line.qty,
                    'price_unit': line.price_unit,
                    'total': line.price_subtotal
                } for line in order.lines]

                _logger.info("New self-order received: %s", order.name)
                _logger.info("Order details: %s", items_info)

                table_num = order.self_ordering_table_id.table_number if order.self_ordering_table_id else "Unknown"

                merged = {}

                for item in items_info:
                    name = item['product']
                    if name in merged:
                        merged[name]['quantity'] += item['quantity']
                        merged[name]['total'] += item['total']
                    else:
                        # Create a copy to avoid modifying the original list
                        merged[name] = item.copy()

                self.env['bus.bus']._sendone(
                    'pos_order_notification',
                    'new_self_order',
                    {
                        'message': f"Table {table_num}:\n" +
                                   ", ".join([f"{int(i['quantity'])} x {i['product']}" for i in list(merged.values())]),
                        'order_id': order.id,
                        'items': items_info,
                        'type': 'new_self_order'
                    }
                )
        return orders

    def write(self, vals):
        for order in self:
            if hasattr(order, 'source') and order.source == 'mobile':

                # Store previous quantities per line
                previous_quantities = {
                    line.id: line.qty for line in order.lines
                }

                res = super(PosOrder, order).write(vals)

                changed_items = []

                for line in order.lines:
                    old_qty = previous_quantities.get(line.id, 0)

                    if line.qty > old_qty:
                        added_qty = line.qty - old_qty

                        changed_items.append({
                            'product': line.product_id.display_name,
                            'quantity': added_qty,
                            'price_unit': line.price_unit,
                            'total': added_qty * line.price_unit
                        })

                if changed_items:
                    table_num = order.self_ordering_table_id.table_number if order.self_ordering_table_id else "Unknown"

                    self.env['bus.bus']._sendone(
                        'pos_order_notification',
                        'new_self_order',
                        {
                            'message': f"Table {table_num}:\n" +
                                ", ".join([f"{int(i['quantity'])} x {i['product']}" for i in changed_items]),
                            'order_id': order.id,
                            'items': changed_items,
                            'type': 'new_self_order'
                        }
                    )

            else:
                res = super(PosOrder, order).write(vals)

        return res